import enum

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class ContractType(str, enum.Enum):
    nda = "nda"
    service_agreement = "service_agreement"
    employment = "employment"
    vendor = "vendor"
    lease = "lease"
    other = "other"


class ContractStatus(str, enum.Enum):
    draft = "draft"
    review = "review"
    active = "active"
    expired = "expired"
    terminated = "terminated"


class ClauseType(str, enum.Enum):
    termination = "termination"
    liability = "liability"
    ip = "ip"
    confidentiality = "confidentiality"
    non_compete = "non_compete"
    payment = "payment"
    other = "other"


class RiskLevel(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"


class ComplianceCategory(str, enum.Enum):
    license = "license"
    regulation = "regulation"
    policy = "policy"
    certification = "certification"


class ComplianceStatus(str, enum.Enum):
    compliant = "compliant"
    non_compliant = "non_compliant"
    pending = "pending"
    expiring = "expiring"


class ContactRole(str, enum.Enum):
    attorney = "attorney"
    paralegal = "paralegal"
    advisor = "advisor"
    notary = "notary"


class ReferenceType(str, enum.Enum):
    contract = "contract"
    compliance = "compliance"
    general = "general"


# ---------------------------------------------------------------------------
# ORM Models
# ---------------------------------------------------------------------------

class Contract(Base):
    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    type = Column(Enum(ContractType), nullable=False)
    status = Column(Enum(ContractStatus), nullable=False, default=ContractStatus.draft)
    counterparty = Column(String(255), nullable=False)
    counterparty_email = Column(String(255), nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    renewal_date = Column(Date, nullable=True)
    auto_renew = Column(Boolean, nullable=False, default=False)
    value = Column(Float, nullable=True)
    currency = Column(String(10), nullable=False, default="USD")
    summary = Column(Text, nullable=True)
    file_url = Column(String(512), nullable=True)
    signed_date = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    clauses = relationship("Clause", back_populates="contract", cascade="all, delete-orphan")


class Clause(Base):
    __tablename__ = "clauses"

    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.id", ondelete="CASCADE"), nullable=False)
    type = Column(Enum(ClauseType), nullable=False)
    summary = Column(String(512), nullable=True)
    text = Column(Text, nullable=False)
    risk_level = Column(Enum(RiskLevel), nullable=False, default=RiskLevel.low)
    notes = Column(Text, nullable=True)

    contract = relationship("Contract", back_populates="clauses")


class ComplianceItem(Base):
    __tablename__ = "compliance_items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(Enum(ComplianceCategory), nullable=False)
    status = Column(Enum(ComplianceStatus), nullable=False, default=ComplianceStatus.pending)
    due_date = Column(Date, nullable=True)
    responsible_person = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class LegalContact(Base):
    __tablename__ = "legal_contacts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    role = Column(Enum(ContactRole), nullable=False)
    firm = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    specialty = Column(String(255), nullable=True)
    hourly_rate = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)


class LegalNote(Base):
    __tablename__ = "legal_notes"

    id = Column(Integer, primary_key=True, index=True)
    reference_type = Column(Enum(ReferenceType), nullable=False)
    reference_id = Column(Integer, nullable=True)
    content = Column(Text, nullable=False)
    author = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
