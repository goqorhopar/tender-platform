"""Tender management endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.models.user import User
from app.models.tender import Tender, TenderStatus, TenderType
from app.schemas.tender import (
    TenderCreate,
    TenderUpdate,
    TenderResponse,
    TenderSearch,
    TenderListResponse,
    TenderStatusEnum,
    TenderTypeEnum,
)
from app.utils.deps import get_current_user

router = APIRouter()


@router.post("", response_model=TenderResponse, status_code=status.HTTP_201_CREATED)
async def create_tender(
    tender_data: TenderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new tender.
    
    Creates a new tender with the provided information.
    The tender is created in DRAFT status by default.
    """
    # Check if tender number already exists
    result = await db.execute(
        select(Tender).where(Tender.tender_number == tender_data.tender_number)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tender with this number already exists",
        )
    
    # Create new tender
    new_tender = Tender(
        tender_number=tender_data.tender_number,
        title=tender_data.title,
        description=tender_data.description,
        initial_price=tender_data.initial_price,
        current_price=tender_data.initial_price,
        currency=tender_data.currency,
        tender_type=TenderType(tender_data.tender_type.value),
        customer_name=tender_data.customer_name,
        customer_inn=tender_data.customer_inn,
        submission_deadline=tender_data.submission_deadline,
        region=tender_data.region,
        source_url=tender_data.source_url,
        status=TenderStatus.DRAFT,
    )
    
    db.add(new_tender)
    await db.commit()
    await db.refresh(new_tender)
    
    return new_tender


@router.get("", response_model=TenderListResponse)
async def list_tenders(
    search: TenderSearch = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List tenders with filtering and pagination.
    
    Returns a paginated list of tenders matching the search criteria.
    """
    # Build query filters
    filters = []
    
    if search.query:
        filters.append(
            or_(
                Tender.title.ilike(f"%{search.query}%"),
                Tender.description.ilike(f"%{search.query}%"),
                Tender.tender_number.ilike(f"%{search.query}%"),
            )
        )
    
    if search.status:
        filters.append(Tender.status == TenderStatus(search.status.value))
    
    if search.tender_type:
        filters.append(Tender.tender_type == TenderType(search.tender_type.value))
    
    if search.min_price is not None:
        filters.append(Tender.current_price >= search.min_price)
    
    if search.max_price is not None:
        filters.append(Tender.current_price <= search.max_price)
    
    if search.region:
        filters.append(Tender.region == search.region)
    
    if search.is_favorite is not None:
        filters.append(Tender.is_favorite == search.is_favorite)
    
    # Execute query with filters
    query = select(Tender).where(and_(*filters)) if filters else select(Tender)
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    # Apply pagination
    offset = (search.page - 1) * search.page_size
    query = query.offset(offset).limit(search.page_size)
    
    result = await db.execute(query)
    tenders = result.scalars().all()
    
    # Calculate total pages
    pages = (total + search.page_size - 1) // search.page_size
    
    return TenderListResponse(
        items=[TenderResponse.model_validate(t) for t in tenders],
        total=total,
        page=search.page,
        page_size=search.page_size,
        pages=pages,
    )


@router.get("/{tender_id}", response_model=TenderResponse)
async def get_tender(
    tender_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get tender by ID.
    
    Returns detailed information about a specific tender.
    """
    import uuid
    try:
        tender_uuid = uuid.UUID(tender_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid tender ID format",
        )
    
    result = await db.execute(select(Tender).where(Tender.id == tender_uuid))
    tender = result.scalar_one_or_none()
    
    if not tender:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tender not found",
        )
    
    return tender


@router.patch("/{tender_id}", response_model=TenderResponse)
async def update_tender(
    tender_id: str,
    tender_data: TenderUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update tender information.
    
    Updates the specified fields of an existing tender.
    """
    import uuid
    try:
        tender_uuid = uuid.UUID(tender_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid tender ID format",
        )
    
    result = await db.execute(select(Tender).where(Tender.id == tender_uuid))
    tender = result.scalar_one_or_none()
    
    if not tender:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tender not found",
        )
    
    # Update fields
    update_data = tender_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "status" and value:
            value = TenderStatus(value.value)
        setattr(tender, field, value)
    
    await db.commit()
    await db.refresh(tender)
    
    return tender


@router.delete("/{tender_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tender(
    tender_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete tender by ID.
    
    Permanently removes a tender from the system.
    """
    import uuid
    try:
        tender_uuid = uuid.UUID(tender_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid tender ID format",
        )
    
    result = await db.execute(select(Tender).where(Tender.id == tender_uuid))
    tender = result.scalar_one_or_none()
    
    if not tender:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tender not found",
        )
    
    await db.delete(tender)
    await db.commit()
    
    return None


@router.post("/{tender_id}/favorite", response_model=TenderResponse)
async def toggle_favorite(
    tender_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Toggle tender favorite status.
    
    Marks or unmarks a tender as favorite.
    """
    import uuid
    try:
        tender_uuid = uuid.UUID(tender_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid tender ID format",
        )
    
    result = await db.execute(select(Tender).where(Tender.id == tender_uuid))
    tender = result.scalar_one_or_none()
    
    if not tender:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tender not found",
        )
    
    tender.is_favorite = not tender.is_favorite
    await db.commit()
    await db.refresh(tender)
    
    return tender


@router.post("/{tender_id}/analyze")
async def analyze_tender(
    tender_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Trigger AI analysis for a tender.
    
    Queues an async task to analyze the tender using AI.
    Returns the task ID for tracking progress.
    """
    import uuid
    try:
        tender_uuid = uuid.UUID(tender_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid tender ID format",
        )
    
    result = await db.execute(select(Tender).where(Tender.id == tender_uuid))
    tender = result.scalar_one_or_none()
    
    if not tender:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tender not found",
        )
    
    # Queue analysis task
    from app.tasks.tender_tasks import analyze_tender as analyze_task
    task = analyze_task.delay(str(tender_uuid))
    
    return {
        "task_id": task.id,
        "tender_id": str(tender_uuid),
        "status": "queued",
    }
