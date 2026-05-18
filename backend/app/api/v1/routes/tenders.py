"""
Tender Platform - Tender Routes
CRUD operations and search functionality for tenders.
"""

from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime

from app.db.database import get_db
from app.models import User, Tender, TenderStatus, TenderType
from app.api.v1.routes.auth import get_current_active_user
from app.core.logging_config import get_logger


router = APIRouter()
logger = get_logger(__name__)


# ============================================================================
# TENDER ENDPOINTS
# ============================================================================
@router.post("", response_model=dict)
async def create_tender(
    request: Request,
    tender_data: dict,  # Would use proper schema in production
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Create a new tender.
    """
    tender = Tender(
        **tender_data,
        created_by=current_user.id,
    )
    
    db.add(tender)
    db.commit()
    db.refresh(tender)
    
    logger.info(f"Tender created: {tender.tender_number} by {current_user.email}")
    
    return {"id": str(tender.id), "message": "Tender created successfully"}


@router.get("", response_model=dict)
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
    
    total = query.count()
    tenders = query.offset(skip).limit(limit).all()
    
    return {
        "items": [
            {
                "id": str(t.id),
                "title": t.title,
                "tender_number": t.tender_number,
                "status": t.status.value,
                "initial_price": t.initial_price,
                "currency": t.currency,
                "submission_deadline": t.submission_deadline.isoformat() if t.submission_deadline else None,
            }
            for t in tenders
        ],
        "total": total,
        "page": (skip // limit) + 1,
        "page_size": limit,
    }


@router.get("/{tender_id}", response_model=dict)
async def get_tender(
    request: Request,
    tender_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get tender by ID.
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
    
    return {
        "id": str(tender.id),
        "title": tender.title,
        "description": tender.description,
        "tender_number": tender.tender_number,
        "status": tender.status.value,
        "type": tender.type.value,
        "initial_price": tender.initial_price,
        "currency": tender.currency,
        "customer_name": tender.customer_name,
        "publication_date": tender.publication_date.isoformat() if tender.publication_date else None,
        "submission_deadline": tender.submission_deadline.isoformat() if tender.submission_deadline else None,
    }


@router.put("/{tender_id}", response_model=dict)
async def update_tender(
    request: Request,
    tender_id: UUID,
    tender_data: dict,
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
    
    # Update fields
    for key, value in tender_data.items():
        if hasattr(tender, key):
            setattr(tender, key, value)
    
    tender.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(tender)
    
    logger.info(f"Tender updated: {tender.tender_number} by {current_user.email}")
    
    return {"message": "Tender updated successfully"}


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
