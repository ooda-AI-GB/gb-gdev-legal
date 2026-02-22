from datetime import date, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..auth import verify_api_key
from ..database import get_db
from ..models import ComplianceItem, ComplianceStatus, Contract, ContractStatus
from ..schemas import ComplianceBreakdown, DashboardResponse

router = APIRouter()

EXPIRING_SOON_DAYS = 30


@router.get("/dashboard", response_model=DashboardResponse)
def get_dashboard(
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    today = date.today()
    deadline_30 = today + timedelta(days=EXPIRING_SOON_DAYS)

    # Active contracts and their total value
    active_contracts = (
        db.query(Contract)
        .filter(Contract.status == ContractStatus.active)
        .all()
    )
    active_contracts_count = len(active_contracts)
    total_contract_value = sum(c.value or 0.0 for c in active_contracts)

    # Contracts expiring within 30 days (active only)
    expiring_soon_count = (
        db.query(func.count(Contract.id))
        .filter(
            Contract.status == ContractStatus.active,
            Contract.end_date.isnot(None),
            Contract.end_date >= today,
            Contract.end_date <= deadline_30,
        )
        .scalar()
        or 0
    )

    # Compliance status breakdown
    status_rows = (
        db.query(ComplianceItem.status, func.count(ComplianceItem.id))
        .group_by(ComplianceItem.status)
        .all()
    )
    counts = {row[0]: row[1] for row in status_rows}
    compliance_status = ComplianceBreakdown(
        compliant=counts.get(ComplianceStatus.compliant, 0),
        non_compliant=counts.get(ComplianceStatus.non_compliant, 0),
        pending=counts.get(ComplianceStatus.pending, 0),
        expiring=counts.get(ComplianceStatus.expiring, 0),
    )

    # Overdue compliance items: past due_date and not compliant
    overdue_compliance_items = (
        db.query(func.count(ComplianceItem.id))
        .filter(
            ComplianceItem.due_date.isnot(None),
            ComplianceItem.due_date < today,
            ComplianceItem.status != ComplianceStatus.compliant,
        )
        .scalar()
        or 0
    )

    return DashboardResponse(
        active_contracts_count=active_contracts_count,
        total_contract_value=total_contract_value,
        expiring_soon_count=expiring_soon_count,
        compliance_status=compliance_status,
        overdue_compliance_items=overdue_compliance_items,
    )
