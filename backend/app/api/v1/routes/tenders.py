"""
Tender Platform - Tender Routes
CRUD operations and search functionality for tenders.
"""

from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session, selectinload
from uuid import UUID
from datetime import datetime

from app.db.database import get_db
from app.models import User, Tender, TenderStatus, TenderType
from app.api.v1.routes.auth import get_current_active_user
from app.schemas.tender import (
    TenderCreate,
    TenderUpdate,
    TenderResponse,
    TenderListResponse,
    TenderListItem,
    TenderSearchRequest,
)
from app.core.logging_config import get_logger


router = APIRouter()
logger = get_logger(__name__)


# ============================================================================
# TENDER ENDPOINTS
# ============================================================================
@router.post("", response_model=TenderResponse)
async def create_tender(
    request: Request,
    tender_data: TenderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Create a new tender.
    """
    tender = Tender(
        title=tender_data.title,
        description=tender_data.description,
        tender_number=tender_data.tender_number,
        type=tender_data.type,
        status=tender_data.status,
        category=tender_data.category,
        initial_price=tender_data.initial_price,
        currency=tender_data.currency,
        customer_name=tender_data.customer_name,
        customer_inn=tender_data.customer_inn,
        customer_region=tender_data.customer_region,
        submission_deadline=tender_data.submission_deadline,
        publication_date=tender_data.publication_date,
        okpd2_codes=tender_data.okpd2_codes or [],
        documents_url=tender_data.documents_url,
        technical_spec_url=tender_data.technical_spec_url,
        creator_id=current_user.id,
    )
    
    db.add(tender)
    db.commit()
    db.refresh(tender)
    
    logger.info(f"Tender created: {tender.tender_number} by {current_user.email}")
    
    return tender


@router.get("", response_model=TenderListResponse)
async def list_tenders(
    request: Request,
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[TenderStatus] = None,
    type_filter: Optional[TenderType] = None,
    search: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    List tenders with filtering and pagination.
    Optimized query with proper indexing.
    """
    query = db.query(Tender).filter(Tender.is_deleted == False)
    
    # Apply filters
    if status_filter:
        query = query.filter(Tender.status == status_filter)
    if type_filter:
        query = query.filter(Tender.type == type_filter)
    if search:
        query = query.filter(
            (Tender.title.ilike(f"%{search}%")) |
            (Tender.description.ilike(f"%{search}%")) |
            (Tender.tender_number.ilike(f"%{search}%"))
        )
    if min_price is not None:
        query = query.filter(Tender.initial_price >= min_price)
    if max_price is not None:
        query = query.filter(Tender.initial_price <= max_price)
    
    # Get total count before pagination
    total = query.count()
    
    # Apply pagination with eager loading to avoid N+1 queries
    tenders = query.options(
        selectinload(Tender.creator)
    ).offset(skip).limit(limit).all()
    
    # Convert to list items
    items = [
        TenderListItem(
            id=t.id,
            title=t.title,
            tender_number=t.tender_number,
            status=t.status,
            initial_price=t.initial_price,
            currency=t.currency,
            submission_deadline=t.submission_deadline,
            publication_date=t.publication_date,
        )
        for t in tenders
    ]
    
    page = (skip // limit) + 1 if limit > 0 else 1
    
    return TenderListResponse(
        items=items,
        total=total,
        page=page,
        page_size=limit,
        pages=(total + limit - 1) // limit if limit > 0 else 0,
    )


@router.get("/{tender_id}", response_model=TenderResponse)
async def get_tender(
    request: Request,
    tender_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get tender by ID.
    """
    tender = db.query(Tender).options(
        selectinload(Tender.creator),
        selectinload(Tender.assigned_to)
    ).filter(
        Tender.id == tender_id,
        Tender.is_deleted == False
    ).first()
    
    if not tender:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tender not found",
        )
    
    return tender


@router.put("/{tender_id}", response_model=TenderResponse)
async def update_tender(
    request: Request,
    tender_id: UUID,
    tender_data: TenderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update tender by ID.
    """
    tender = db.query(Tender).filter(
        Tender.id == tender_id,
        Tender.is_deleted == False
    ).first()
    
    if not tender:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tender not found",
        )
    
    # Update only provided fields
    update_data = tender_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if hasattr(tender, key):
            setattr(tender, key, value)
    
    tender.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(tender)
    
    logger.info(f"Tender updated: {tender.tender_number} by {current_user.email}")
    
    return tender


@router.delete("/{tender_id}")
async def delete_tender(
    request: Request,
    tender_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Delete tender by ID (soft delete).
    """
    tender = db.query(Tender).filter(
        Tender.id == tender_id,
        Tender.is_deleted == False
    ).first()
    
    if not tender:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tender not found",
        )
    
    tender.is_deleted = True
    tender.deleted_at = datetime.utcnow()
    db.commit()
    
    logger.info(f"Tender deleted: {tender.tender_number} by {current_user.email}")
    
    return {"message": "Tender deleted successfully"}
