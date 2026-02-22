from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..auth import verify_api_key
from ..database import get_db
from ..models import Clause, Contract
from ..schemas import ClauseCreate, ClauseResponse, ClauseUpdate

router = APIRouter()


def _get_or_404(db: Session, clause_id: int) -> Clause:
    clause = db.query(Clause).filter(Clause.id == clause_id).first()
    if not clause:
        raise HTTPException(status_code=404, detail=f"Clause {clause_id} not found")
    return clause


@router.get("/clauses", response_model=List[ClauseResponse])
def list_clauses(
    contract_id: Optional[int] = Query(None, description="Filter by contract ID"),
    risk_level: Optional[str] = Query(None, description="Filter by risk level"),
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    query = db.query(Clause)
    if contract_id is not None:
        query = query.filter(Clause.contract_id == contract_id)
    if risk_level:
        query = query.filter(Clause.risk_level == risk_level)
    return query.all()


@router.post("/clauses", response_model=ClauseResponse, status_code=status.HTTP_201_CREATED)
def create_clause(
    payload: ClauseCreate,
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    contract = db.query(Contract).filter(Contract.id == payload.contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail=f"Contract {payload.contract_id} not found")
    clause = Clause(**payload.model_dump())
    db.add(clause)
    db.commit()
    db.refresh(clause)
    return clause


@router.get("/clauses/{clause_id}", response_model=ClauseResponse)
def get_clause(
    clause_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    return _get_or_404(db, clause_id)


@router.put("/clauses/{clause_id}", response_model=ClauseResponse)
def update_clause(
    clause_id: int,
    payload: ClauseUpdate,
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    clause = _get_or_404(db, clause_id)
    update_data = payload.model_dump(exclude_unset=True)
    if "contract_id" in update_data:
        contract = db.query(Contract).filter(Contract.id == update_data["contract_id"]).first()
        if not contract:
            raise HTTPException(status_code=404, detail=f"Contract {update_data['contract_id']} not found")
    for field, value in update_data.items():
        setattr(clause, field, value)
    db.commit()
    db.refresh(clause)
    return clause


@router.delete("/clauses/{clause_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_clause(
    clause_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    clause = _get_or_404(db, clause_id)
    db.delete(clause)
    db.commit()
