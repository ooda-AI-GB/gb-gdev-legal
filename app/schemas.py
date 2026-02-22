from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from .models import (
    ClauseType,
    ComplianceCategory,
    ComplianceStatus,
    ContactRole,
    ContractStatus,
    ContractType,
    ReferenceType,
    RiskLevel,
)


# ---------------------------------------------------------------------------
# Contract schemas
# ---------------------------------------------------------------------------

class ContractBase(BaseModel):
    title: str
    type: ContractType
    status: ContractStatus = ContractStatus.draft
    counterparty: str
    counterparty_email: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    renewal_date: Optional[date] = None
    auto_renew: bool = False
    value: Optional[float] = None
    currency: str = "USD"
    summary: Optional[str] = None
    file_url: Optional[str] = None
    signed_date: Optional[date] = None


class ContractCreate(ContractBase):
    pass


class ContractUpdate(BaseModel):
    title: Optional[str] = None
    type: Optional[ContractType] = None
    status: Optional[ContractStatus] = None
    counterparty: Optional[str] = None
    counterparty_email: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    renewal_date: Optional[date] = None
    auto_renew: Optional[bool] = None
    value: Optional[float] = None
    currency: Optional[str] = None
    summary: Optional[str] = None
    file_url: Optional[str] = None
    signed_date: Optional[date] = None


class ContractResponse(ContractBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Clause schemas
# ---------------------------------------------------------------------------

class ClauseBase(BaseModel):
    contract_id: int
    type: ClauseType
    summary: Optional[str] = None
    text: str
    risk_level: RiskLevel = RiskLevel.low
    notes: Optional[str] = None


class ClauseCreate(ClauseBase):
    pass


class ClauseUpdate(BaseModel):
    contract_id: Optional[int] = None
    type: Optional[ClauseType] = None
    summary: Optional[str] = None
    text: Optional[str] = None
    risk_level: Optional[RiskLevel] = None
    notes: Optional[str] = None


class ClauseResponse(ClauseBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


# ---------------------------------------------------------------------------
# Compliance item schemas
# ---------------------------------------------------------------------------

class ComplianceItemBase(BaseModel):
    title: str
    description: Optional[str] = None
    category: ComplianceCategory
    status: ComplianceStatus = ComplianceStatus.pending
    due_date: Optional[date] = None
    responsible_person: Optional[str] = None
    notes: Optional[str] = None


class ComplianceItemCreate(ComplianceItemBase):
    pass


class ComplianceItemUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[ComplianceCategory] = None
    status: Optional[ComplianceStatus] = None
    due_date: Optional[date] = None
    responsible_person: Optional[str] = None
    notes: Optional[str] = None


class ComplianceItemResponse(ComplianceItemBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Legal contact schemas
# ---------------------------------------------------------------------------

class LegalContactBase(BaseModel):
    name: str
    role: ContactRole
    firm: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    specialty: Optional[str] = None
    hourly_rate: Optional[float] = None
    notes: Optional[str] = None


class LegalContactCreate(LegalContactBase):
    pass


class LegalContactUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[ContactRole] = None
    firm: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    specialty: Optional[str] = None
    hourly_rate: Optional[float] = None
    notes: Optional[str] = None


class LegalContactResponse(LegalContactBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


# ---------------------------------------------------------------------------
# Legal note schemas
# ---------------------------------------------------------------------------

class LegalNoteBase(BaseModel):
    reference_type: ReferenceType
    reference_id: Optional[int] = None
    content: str
    author: str


class LegalNoteCreate(LegalNoteBase):
    pass


class LegalNoteUpdate(BaseModel):
    reference_type: Optional[ReferenceType] = None
    reference_id: Optional[int] = None
    content: Optional[str] = None
    author: Optional[str] = None


class LegalNoteResponse(LegalNoteBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


# ---------------------------------------------------------------------------
# Dashboard schema
# ---------------------------------------------------------------------------

class ComplianceBreakdown(BaseModel):
    compliant: int = 0
    non_compliant: int = 0
    pending: int = 0
    expiring: int = 0


class DashboardResponse(BaseModel):
    active_contracts_count: int
    total_contract_value: float
    expiring_soon_count: int
    compliance_status: ComplianceBreakdown
    overdue_compliance_items: int
