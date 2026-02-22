from datetime import date, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..auth import verify_api_key
from ..database import get_db
from ..models import ComplianceItem, ComplianceStatus
from ..schemas import ComplianceItemCreate, ComplianceItemResponse, ComplianceItemUpdate

router = APIRouter()


def _get_or_404(db: Session, item_id: int) -> ComplianceItem:
    item = db.query(ComplianceItem).filter(ComplianceItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail=f"Compliance item {item_id} not found")
    return item


@router.get("/compliance", response_model=List[ComplianceItemResponse])
def list_compliance_items(
    status: Optional[str] = Query(None, description="Filter by compliance status"),
    due_within: Optional[int] = Query(None, description="Filter items due within N days"),
    category: Optional[str] = Query(None, description="Filter by category"),
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    query = db.query(ComplianceItem)

    if status:
        try:
            status_enum = ComplianceStatus(status)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status '{status}'. Must be one of: {[s.value for s in ComplianceStatus]}",
            )
        query = query.filter(ComplianceItem.status == status_enum)

    if due_within is not None:
        today = date.today()
        deadline = today + timedelta(days=due_within)
        query = query.filter(
            ComplianceItem.due_date.isnot(None),
            ComplianceItem.due_date >= today,
            ComplianceItem.due_date <= deadline,
        )

    if category:
        query = query.filter(ComplianceItem.category == category)

    return query.order_by(ComplianceItem.due_date.asc().nulls_last()).all()


@router.post("/compliance", response_model=ComplianceItemResponse, status_code=status.HTTP_201_CREATED)
def create_compliance_item(
    payload: ComplianceItemCreate,
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    item = ComplianceItem(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/compliance/{item_id}", response_model=ComplianceItemResponse)
def get_compliance_item(
    item_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    return _get_or_404(db, item_id)


@router.put("/compliance/{item_id}", response_model=ComplianceItemResponse)
def update_compliance_item(
    item_id: int,
    payload: ComplianceItemUpdate,
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    item = _get_or_404(db, item_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/compliance/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_compliance_item(
    item_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    item = _get_or_404(db, item_id)
    db.delete(item)
    db.commit()
