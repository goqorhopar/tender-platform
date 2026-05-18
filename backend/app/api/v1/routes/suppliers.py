"""Supplier management endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_

from app.database import get_db
from app.models.user import User
from app.models.supplier import Supplier
from app.schemas.supplier import (
    SupplierCreate,
    SupplierUpdate,
    SupplierResponse,
    SupplierSearch,
    SupplierListResponse,
)
from app.utils.deps import get_current_user

router = APIRouter()


@router.post("", response_model=SupplierResponse, status_code=status.HTTP_201_CREATED)
async def create_supplier(
    supplier_data: SupplierCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new supplier.
    
    Creates a new supplier with the provided information.
    """
    # Check if supplier with this INN already exists
    result = await db.execute(
        select(Supplier).where(Supplier.inn == supplier_data.inn)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Supplier with this INN already exists",
        )
    
    # Create new supplier
    new_supplier = Supplier(
        name=supplier_data.name,
        inn=supplier_data.inn,
        kpp=supplier_data.kpp,
        email=supplier_data.email,
        phone=supplier_data.phone,
        legal_address=supplier_data.legal_address,
        actual_address=supplier_data.actual_address,
        website=supplier_data.website,
        specialization=supplier_data.specialization,
    )
    
    db.add(new_supplier)
    await db.commit()
    await db.refresh(new_supplier)
    
    return new_supplier


@router.get("", response_model=SupplierListResponse)
async def list_suppliers(
    search: SupplierSearch = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List suppliers with filtering and pagination.
    
    Returns a paginated list of suppliers matching the search criteria.
    """
    # Build query filters
    filters = []
    
    if search.query:
        filters.append(
            or_(
                Supplier.name.ilike(f"%{search.query}%"),
                Supplier.inn.ilike(f"%{search.query}%"),
            )
        )
    
    if search.inn:
        filters.append(Supplier.inn == search.inn)
    
    if search.is_blacklisted is not None:
        filters.append(Supplier.is_blacklisted == search.is_blacklisted)
    
    if search.is_verified is not None:
        filters.append(Supplier.is_verified == search.is_verified)
    
    # Execute query with filters
    query = select(Supplier).where(and_(*filters)) if filters else select(Supplier)
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    # Apply pagination
    offset = (search.page - 1) * search.page_size
    query = query.offset(offset).limit(search.page_size)
    
    result = await db.execute(query)
    suppliers = result.scalars().all()
    
    # Calculate total pages
    pages = (total + search.page_size - 1) // search.page_size
    
    return SupplierListResponse(
        items=[SupplierResponse.model_validate(s) for s in suppliers],
        total=total,
        page=search.page,
        page_size=search.page_size,
        pages=pages,
    )


@router.get("/{supplier_id}", response_model=SupplierResponse)
async def get_supplier(
    supplier_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get supplier by ID.
    
    Returns detailed information about a specific supplier.
    """
    import uuid
    try:
        supplier_uuid = uuid.UUID(supplier_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid supplier ID format",
        )
    
    result = await db.execute(select(Supplier).where(Supplier.id == supplier_uuid))
    supplier = result.scalar_one_or_none()
    
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found",
        )
    
    return supplier


@router.patch("/{supplier_id}", response_model=SupplierResponse)
async def update_supplier(
    supplier_id: str,
    supplier_data: SupplierUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update supplier information.
    
    Updates the specified fields of an existing supplier.
    """
    import uuid
    try:
        supplier_uuid = uuid.UUID(supplier_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid supplier ID format",
        )
    
    result = await db.execute(select(Supplier).where(Supplier.id == supplier_uuid))
    supplier = result.scalar_one_or_none()
    
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found",
        )
    
    # Check if new INN conflicts with existing supplier
    if supplier_data.inn and supplier_data.inn != supplier.inn:
        existing = await db.execute(
            select(Supplier).where(Supplier.inn == supplier_data.inn)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Another supplier with this INN already exists",
            )
    
    # Update fields
    update_data = supplier_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(supplier, field, value)
    
    await db.commit()
    await db.refresh(supplier)
    
    return supplier


@router.delete("/{supplier_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_supplier(
    supplier_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete supplier by ID.
    
    Permanently removes a supplier from the system.
    """
    import uuid
    try:
        supplier_uuid = uuid.UUID(supplier_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid supplier ID format",
        )
    
    result = await db.execute(select(Supplier).where(Supplier.id == supplier_uuid))
    supplier = result.scalar_one_or_none()
    
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found",
        )
    
    await db.delete(supplier)
    await db.commit()
    
    return None


@router.post("/{supplier_id}/blacklist", response_model=SupplierResponse)
async def toggle_blacklist(
    supplier_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Toggle supplier blacklist status.
    
    Marks or unmarks a supplier as blacklisted.
    """
    import uuid
    try:
        supplier_uuid = uuid.UUID(supplier_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid supplier ID format",
        )
    
    result = await db.execute(select(Supplier).where(Supplier.id == supplier_uuid))
    supplier = result.scalar_one_or_none()
    
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found",
        )
    
    supplier.is_blacklisted = not supplier.is_blacklisted
    await db.commit()
    await db.refresh(supplier)
    
    return supplier


@router.post("/{supplier_id}/verify", response_model=SupplierResponse)
async def verify_supplier(
    supplier_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Mark supplier as verified.
    
    Sets the supplier's verification status to true.
    """
    import uuid
    try:
        supplier_uuid = uuid.UUID(supplier_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid supplier ID format",
        )
    
    result = await db.execute(select(Supplier).where(Supplier.id == supplier_uuid))
    supplier = result.scalar_one_or_none()
    
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found",
        )
    
    supplier.is_verified = True
    await db.commit()
    await db.refresh(supplier)
    
    return supplier
