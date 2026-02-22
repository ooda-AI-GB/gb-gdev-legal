from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..auth import verify_api_key
from ..database import get_db
from ..models import LegalContact
from ..schemas import LegalContactCreate, LegalContactResponse, LegalContactUpdate

router = APIRouter()


def _get_or_404(db: Session, contact_id: int) -> LegalContact:
    contact = db.query(LegalContact).filter(LegalContact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail=f"Legal contact {contact_id} not found")
    return contact


@router.get("/contacts", response_model=List[LegalContactResponse])
def list_contacts(
    role: Optional[str] = Query(None, description="Filter by contact role"),
    specialty: Optional[str] = Query(None, description="Filter by specialty (partial match)"),
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    query = db.query(LegalContact)
    if role:
        query = query.filter(LegalContact.role == role)
    if specialty:
        query = query.filter(LegalContact.specialty.ilike(f"%{specialty}%"))
    return query.order_by(LegalContact.name.asc()).all()


@router.post("/contacts", response_model=LegalContactResponse, status_code=status.HTTP_201_CREATED)
def create_contact(
    payload: LegalContactCreate,
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    contact = LegalContact(**payload.model_dump())
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


@router.get("/contacts/{contact_id}", response_model=LegalContactResponse)
def get_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    return _get_or_404(db, contact_id)


@router.put("/contacts/{contact_id}", response_model=LegalContactResponse)
def update_contact(
    contact_id: int,
    payload: LegalContactUpdate,
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    contact = _get_or_404(db, contact_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(contact, field, value)
    db.commit()
    db.refresh(contact)
    return contact


@router.delete("/contacts/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    contact = _get_or_404(db, contact_id)
    db.delete(contact)
    db.commit()
