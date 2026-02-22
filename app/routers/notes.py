from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..auth import verify_api_key
from ..database import get_db
from ..models import LegalNote
from ..schemas import LegalNoteCreate, LegalNoteResponse, LegalNoteUpdate

router = APIRouter()


def _get_or_404(db: Session, note_id: int) -> LegalNote:
    note = db.query(LegalNote).filter(LegalNote.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail=f"Legal note {note_id} not found")
    return note


@router.get("/notes", response_model=List[LegalNoteResponse])
def list_notes(
    reference_type: Optional[str] = Query(None, description="Filter by reference type"),
    reference_id: Optional[int] = Query(None, description="Filter by reference ID"),
    author: Optional[str] = Query(None, description="Filter by author (partial match)"),
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    query = db.query(LegalNote)
    if reference_type:
        query = query.filter(LegalNote.reference_type == reference_type)
    if reference_id is not None:
        query = query.filter(LegalNote.reference_id == reference_id)
    if author:
        query = query.filter(LegalNote.author.ilike(f"%{author}%"))
    return query.order_by(LegalNote.created_at.desc()).all()


@router.post("/notes", response_model=LegalNoteResponse, status_code=status.HTTP_201_CREATED)
def create_note(
    payload: LegalNoteCreate,
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    note = LegalNote(**payload.model_dump())
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


@router.get("/notes/{note_id}", response_model=LegalNoteResponse)
def get_note(
    note_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    return _get_or_404(db, note_id)


@router.put("/notes/{note_id}", response_model=LegalNoteResponse)
def update_note(
    note_id: int,
    payload: LegalNoteUpdate,
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    note = _get_or_404(db, note_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(note, field, value)
    db.commit()
    db.refresh(note)
    return note


@router.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(
    note_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    note = _get_or_404(db, note_id)
    db.delete(note)
    db.commit()
