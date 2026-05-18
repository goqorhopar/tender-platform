"""
Tender Platform - Document Routes
File upload, download, and management endpoints.
"""

from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Request
from sqlalchemy.orm import Session
from uuid import UUID
import hashlib
from pathlib import Path

from app.db.database import get_db
from app.models import User, TenderDocument, DocumentType
from app.api.v1.routes.auth import get_current_active_user
from app.core.config import settings
from app.core.security import secure_filename, validate_file_extension, generate_file_hash
from app.core.logging_config import get_logger


router = APIRouter()
logger = get_logger(__name__)


# ============================================================================
# DOCUMENT ENDPOINTS
# ============================================================================
@router.post("/upload", response_model=dict)
async def upload_document(
    request: Request,
    file: UploadFile = File(...),
    tender_id: Optional[UUID] = None,
    document_type: DocumentType = DocumentType.OTHER,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Upload a document.
    """
    # Validate file extension
    if not validate_file_extension(file.filename or "", settings.ALLOWED_EXTENSIONS):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {settings.ALLOWED_EXTENSIONS}",
        )
    
    # Read file content
    content = await file.read()
    
    # Check file size
    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE} bytes",
        )
    
    # Generate secure filename and hash
    secure_name = secure_filename(file.filename or "unnamed")
    file_hash = generate_file_hash(content)
    
    # Save file locally (in production, use S3)
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = upload_dir / f"{secure_name}"
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Create database record
    document = TenderDocument(
        tender_id=tender_id,
        name=secure_name,
        original_filename=file.filename,
        file_type=document_type,
        mime_type=file.content_type or "application/octet-stream",
        file_size=len(content),
        storage_path=str(file_path),
        uploaded_by_id=current_user.id,
        checksum=file_hash,
    )
    
    db.add(document)
    db.commit()
    db.refresh(document)
    
    logger.info(f"Document uploaded: {secure_name} by {current_user.email}")
    
    return {
        "id": str(document.id),
        "name": document.name,
        "size": document.file_size,
        "type": document.file_type.value,
        "message": "Document uploaded successfully",
    }


@router.get("/{document_id}", response_model=dict)
async def get_document_info(
    request: Request,
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get document information.
    """
    document = db.query(TenderDocument).filter(
        TenderDocument.id == document_id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    
    return {
        "id": str(document.id),
        "name": document.name,
        "original_filename": document.original_filename,
        "file_type": document.file_type.value,
        "mime_type": document.mime_type,
        "file_size": document.file_size,
        "uploaded_at": document.created_at.isoformat(),
        "uploaded_by": str(document.uploaded_by_id),
    }


@router.delete("/{document_id}")
async def delete_document(
    request: Request,
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Delete a document.
    """
    document = db.query(TenderDocument).filter(
        TenderDocument.id == document_id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    
    # Delete file from storage
    file_path = Path(document.storage_path)
    if file_path.exists():
        file_path.unlink()
    
    # Delete database record
    db.delete(document)
    db.commit()
    
    logger.info(f"Document deleted: {document.name} by {current_user.email}")
    
    return {"message": "Document deleted successfully"}
