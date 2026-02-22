from datetime import date, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..auth import verify_api_key
from ..database import get_db
from ..models import Clause, Contract, ContractStatus
from ..schemas import (
    ClauseResponse,
    ContractCreate,
    ContractResponse,
    ContractUpdate,
)

router = APIRouter()


def _get_or_404(db: Session, contract_id: int) -> Contract:
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail=f"Contract {contract_id} not found")
    return contract


@router.get("/contracts", response_model=List[ContractResponse])
def list_contracts(
    status: Optional[str] = Query(None, description="Filter by contract status"),
    expiring_within: Optional[int] = Query(None, description="Filter contracts expiring within N days"),
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    query = db.query(Contract)

    if status:
        try:
            status_enum = ContractStatus(status)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status '{status}'. Must be one of: {[s.value for s in ContractStatus]}",
            )
        query = query.filter(Contract.status == status_enum)

    if expiring_within is not None:
        today = date.today()
        deadline = today + timedelta(days=expiring_within)
        query = query.filter(
            Contract.end_date.isnot(None),
            Contract.end_date >= today,
            Contract.end_date <= deadline,
        )

    return query.order_by(Contract.created_at.desc()).all()


@router.post("/contracts", response_model=ContractResponse, status_code=status.HTTP_201_CREATED)
def create_contract(
    payload: ContractCreate,
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    contract = Contract(**payload.model_dump())
    db.add(contract)
    db.commit()
    db.refresh(contract)
    return contract


@router.get("/contracts/{contract_id}", response_model=ContractResponse)
def get_contract(
    contract_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    return _get_or_404(db, contract_id)


@router.put("/contracts/{contract_id}", response_model=ContractResponse)
def update_contract(
    contract_id: int,
    payload: ContractUpdate,
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    contract = _get_or_404(db, contract_id)
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(contract, field, value)
    db.commit()
    db.refresh(contract)
    return contract


@router.delete("/contracts/{contract_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contract(
    contract_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    contract = _get_or_404(db, contract_id)
    db.delete(contract)
    db.commit()


@router.get("/contracts/{contract_id}/clauses", response_model=List[ClauseResponse])
def list_contract_clauses(
    contract_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    _get_or_404(db, contract_id)
    clauses = db.query(Clause).filter(Clause.contract_id == contract_id).all()
    return clauses
