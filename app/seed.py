"""Seed data for Legal Pro — call seed_db(db) to populate an empty database."""

from datetime import date, timedelta

from sqlalchemy.orm import Session

from .models import (
    Clause,
    ComplianceItem,
    Contract,
    LegalContact,
    LegalNote,
)


def seed_db(db: Session) -> None:
    """Populate the database with sample records. Skips if data already exists."""
    if db.query(Contract).first():
        return

    today = date.today()

    # ------------------------------------------------------------------
    # Legal Contacts
    # ------------------------------------------------------------------
    contacts = [
        LegalContact(
            name="Sarah Johnson",
            role="attorney",
            firm="Johnson & Associates LLP",
            email="sarah.johnson@jassoc.com",
            phone="+1-555-0101",
            specialty="Contract Law",
            hourly_rate=350.0,
            notes="Primary corporate counsel. Specialises in technology and IP contracts.",
        ),
        LegalContact(
            name="Michael Chen",
            role="paralegal",
            firm="Chen Legal Support",
            email="m.chen@chenlegal.com",
            phone="+1-555-0102",
            specialty="Document Review",
            hourly_rate=95.0,
            notes="Available for document review, filing and due-diligence support.",
        ),
        LegalContact(
            name="Dr. Patricia Wells",
            role="advisor",
            firm="LegalEagle Consulting",
            email="p.wells@legaleagle.com",
            phone="+1-555-0103",
            specialty="Employment Law",
            hourly_rate=275.0,
            notes="Expert in employment contracts, non-compete enforceability and labour regulations.",
        ),
        LegalContact(
            name="Robert Martinez",
            role="notary",
            firm="Martinez Notary Services",
            email="r.martinez@mnotary.com",
            phone="+1-555-0104",
            specialty="Document Notarization",
            hourly_rate=75.0,
            notes="Certified for remote and in-person notarization across all states.",
        ),
    ]
    db.add_all(contacts)
    db.flush()

    # ------------------------------------------------------------------
    # Contracts
    # ------------------------------------------------------------------
    contracts = [
        # 0 — NDA expiring soon (15 days)
        Contract(
            title="Mutual NDA with TechCorp Solutions",
            type="nda",
            status="active",
            counterparty="TechCorp Solutions",
            counterparty_email="legal@techcorp.com",
            start_date=today - timedelta(days=350),
            end_date=today + timedelta(days=15),
            renewal_date=today + timedelta(days=15),
            auto_renew=True,
            value=0.0,
            currency="USD",
            summary=(
                "Mutual non-disclosure agreement covering technology development discussions "
                "and proprietary product roadmap information."
            ),
            signed_date=today - timedelta(days=350),
        ),
        # 1 — Service agreement active
        Contract(
            title="Software Development Services Agreement",
            type="service_agreement",
            status="active",
            counterparty="ConsultPro Ltd",
            counterparty_email="contracts@consultpro.com",
            start_date=today - timedelta(days=90),
            end_date=today + timedelta(days=60),
            auto_renew=False,
            value=125_000.0,
            currency="USD",
            summary=(
                "Agreement for software development consulting services covering UI/UX design, "
                "backend API development and QA across three project phases."
            ),
            signed_date=today - timedelta(days=90),
        ),
        # 2 — Employment agreement (no end date)
        Contract(
            title="Employment Agreement — VP of Engineering",
            type="employment",
            status="active",
            counterparty="John Smith",
            counterparty_email="j.smith@company.com",
            start_date=today - timedelta(days=180),
            auto_renew=False,
            value=185_000.0,
            currency="USD",
            summary=(
                "Executive employment agreement for the Vice President of Engineering position, "
                "including base salary, equity grant schedule and benefits package."
            ),
            signed_date=today - timedelta(days=180),
        ),
        # 3 — Vendor agreement under review
        Contract(
            title="Cloud Infrastructure Vendor Agreement",
            type="vendor",
            status="review",
            counterparty="SupplyChain Inc",
            counterparty_email="vendor@supplychain.com",
            start_date=today + timedelta(days=30),
            end_date=today + timedelta(days=395),
            auto_renew=True,
            value=48_000.0,
            currency="USD",
            summary=(
                "Annual vendor agreement for cloud infrastructure provisioning, managed hosting "
                "and 24/7 SLA-backed support services."
            ),
        ),
        # 4 — Lease agreement (long-term active)
        Contract(
            title="Office Space Lease Agreement",
            type="lease",
            status="active",
            counterparty="Prime Properties LLC",
            counterparty_email="leasing@primeprops.com",
            start_date=today - timedelta(days=365),
            end_date=today + timedelta(days=730),
            auto_renew=False,
            value=240_000.0,
            currency="USD",
            summary=(
                "Three-year commercial office lease for 5,000 sq ft at the downtown business "
                "district. Includes parking allocation and fit-out allowance."
            ),
            signed_date=today - timedelta(days=365),
        ),
        # 5 — SaaS agreement draft
        Contract(
            title="SaaS Platform License Agreement",
            type="service_agreement",
            status="draft",
            counterparty="CloudProvider Co",
            counterparty_email="sales@cloudprovider.com",
            start_date=today + timedelta(days=14),
            end_date=today + timedelta(days=379),
            auto_renew=True,
            value=36_000.0,
            currency="USD",
            summary=(
                "Annual SaaS licensing agreement for project management and team collaboration "
                "tooling, covering up to 200 seats with enterprise support."
            ),
        ),
    ]
    db.add_all(contracts)
    db.flush()

    # ------------------------------------------------------------------
    # Clauses
    # ------------------------------------------------------------------
    clauses = [
        # Contract 0 — NDA
        Clause(
            contract_id=contracts[0].id,
            type="confidentiality",
            summary="Mutual confidentiality obligations",
            text=(
                "Each party agrees to maintain the confidentiality of all proprietary information "
                "received from the other party and shall not disclose such information to any third "
                "party without prior written consent. Obligations survive termination for five years."
            ),
            risk_level="low",
            notes="Standard mutual NDA clause. Survival period is industry-standard.",
        ),
        Clause(
            contract_id=contracts[0].id,
            type="termination",
            summary="90-day notice with auto-renewal",
            text=(
                "Either party may terminate this Agreement with 90 days written notice. The Agreement "
                "shall automatically renew for successive one-year terms unless a party provides "
                "written notice of non-renewal at least 90 days before expiry."
            ),
            risk_level="medium",
            notes="Auto-renewal clause — expiry in 15 days. Decision required on scope expansion.",
        ),
        # Contract 1 — Service Agreement
        Clause(
            contract_id=contracts[1].id,
            type="liability",
            summary="Liability cap at 12-month fees",
            text=(
                "Neither party's aggregate liability under this Agreement shall exceed the total fees "
                "paid in the twelve months preceding the claim. Consequential, indirect, special or "
                "punitive damages are excluded in all circumstances."
            ),
            risk_level="high",
            notes="Cap may be insufficient for critical system failures. Escalate to legal for review.",
        ),
        Clause(
            contract_id=contracts[1].id,
            type="payment",
            summary="Net-30 payment terms with late fees",
            text=(
                "Payment is due within 30 days of invoice date. Late payments accrue interest at "
                "1.5% per month (18% per annum). Disputed invoices must be raised in writing within "
                "10 business days of receipt."
            ),
            risk_level="low",
            notes="Standard payment terms. Finance team notified of dispute window.",
        ),
        Clause(
            contract_id=contracts[1].id,
            type="termination",
            summary="Termination for cause — 30-day cure period",
            text=(
                "Either party may terminate this Agreement for material breach upon 30 days written "
                "notice, provided the breach is not remedied within such period. Immediate termination "
                "is permitted upon an insolvency event or willful misconduct by the other party."
            ),
            risk_level="medium",
            notes="Ensure breach notification workflow is documented and audit-trailed.",
        ),
        # Contract 2 — Employment
        Clause(
            contract_id=contracts[2].id,
            type="non_compete",
            summary="12-month non-compete in technology sector",
            text=(
                "For a period of 12 months following termination of employment, Employee shall not "
                "directly or indirectly engage in any competitive business activity within the technology "
                "sector in the continental United States, nor solicit the Company's clients or employees."
            ),
            risk_level="high",
            notes="Enforceability varies by state. Confirm applicability with employment counsel.",
        ),
        Clause(
            contract_id=contracts[2].id,
            type="ip",
            summary="Broad work product assignment to company",
            text=(
                "All inventions, developments, discoveries, designs and work product conceived, created "
                "or reduced to practice by Employee during the employment term — whether on or off "
                "company premises — shall be the sole and exclusive property of the Company."
            ),
            risk_level="medium",
            notes="Employee acknowledged in writing. Prior inventions list attached as Exhibit A.",
        ),
        # Contract 4 — Lease
        Clause(
            contract_id=contracts[4].id,
            type="termination",
            summary="Early termination — 6-month penalty",
            text=(
                "Tenant may terminate this lease before its natural expiry upon 180 days written notice "
                "and payment of an early termination fee equal to six months' base rent. Fit-out "
                "allowance must be repaid on a pro-rata basis if termination occurs within year one."
            ),
            risk_level="high",
            notes="Early termination cost is significant. Factor into any office relocation plans.",
        ),
    ]
    db.add_all(clauses)
    db.flush()

    # ------------------------------------------------------------------
    # Compliance Items
    # ------------------------------------------------------------------
    compliance_items = [
        ComplianceItem(
            title="State Business Operating License",
            description=(
                "Annual business license renewal required by the State Department of Business "
                "Regulation. Must be renewed before expiry to avoid fines."
            ),
            category="license",
            status="compliant",
            due_date=today + timedelta(days=90),
            responsible_person="Operations Manager",
            notes="Renewed successfully. Confirmation number #BL-2026-00421. Next renewal in 90 days.",
        ),
        ComplianceItem(
            title="GDPR Data Protection Compliance",
            description=(
                "Ensure all data processing activities comply with GDPR requirements including DPA "
                "updates, lawful basis documentation, and consent management for marketing."
            ),
            category="regulation",
            status="pending",
            due_date=today + timedelta(days=20),
            responsible_person="DPO — Legal Team",
            notes=(
                "DPA review in progress. Privacy policy update and cookie consent banner "
                "scheduled for deployment. Three new vendor DPAs outstanding."
            ),
        ),
        ComplianceItem(
            title="ISO 27001 Information Security Certification",
            description=(
                "Annual recertification audit for the ISO 27001 information security management "
                "system. External auditor engaged — evidence collection required."
            ),
            category="certification",
            status="expiring",
            due_date=today + timedelta(days=25),
            responsible_person="CISO",
            notes="Audit scheduled. Evidence collection 80% complete. Risk register review outstanding.",
        ),
        ComplianceItem(
            title="Employee Safety Training Policy",
            description=(
                "Mandatory annual safety training completion for all employees as required by OSHA "
                "regulations. Includes fire safety, emergency evacuation and workplace hazard modules."
            ),
            category="policy",
            status="non_compliant",
            due_date=today - timedelta(days=15),
            responsible_person="HR Director",
            notes=(
                "OVERDUE: Training completion rate is 67%. Department heads notified. "
                "Remedial sessions scheduled. Immediate management escalation required."
            ),
        ),
        ComplianceItem(
            title="PCI DSS Payment Security Compliance",
            description=(
                "Annual PCI DSS Level 1 assessment for payment card data security standards. "
                "Covers cardholder data environment scope, penetration testing and SAQ."
            ),
            category="certification",
            status="compliant",
            due_date=today + timedelta(days=180),
            responsible_person="Security Team",
            notes="Passed last audit with zero findings. QSA report filed. Next assessment in 6 months.",
        ),
    ]
    db.add_all(compliance_items)
    db.flush()

    # ------------------------------------------------------------------
    # Legal Notes
    # ------------------------------------------------------------------
    notes = [
        LegalNote(
            reference_type="contract",
            reference_id=contracts[0].id,
            content=(
                "NDA renewal approaching in 15 days. TechCorp has requested scope expansion to cover "
                "hardware and firmware discussions. Draft amendment prepared — awaiting partner sign-off "
                "before circulating. If not renewed, all active discussions must pause."
            ),
            author="Sarah Johnson",
        ),
        LegalNote(
            reference_type="contract",
            reference_id=contracts[1].id,
            content=(
                "ConsultPro has delivered Phase 1 on schedule and within budget. Phase 2 milestone "
                "review scheduled for next week. Engineering team is satisfied with deliverable quality. "
                "Consider extending contract for Phase 3 — budget approval needed from CFO."
            ),
            author="Legal Team",
        ),
        LegalNote(
            reference_type="contract",
            reference_id=contracts[3].id,
            content=(
                "Vendor agreement is under review. IT security team has flagged data residency concerns — "
                "vendor must confirm EU data remains within EU data centres. Awaiting vendor response to "
                "amended SLA and DPA clauses. Do NOT execute until data residency clause is resolved."
            ),
            author="Sarah Johnson",
        ),
        LegalNote(
            reference_type="compliance",
            reference_id=compliance_items[1].id,
            content=(
                "GDPR gap analysis complete. Key findings: (1) consent management for marketing emails "
                "lacks granular opt-in records, (2) data processing registry not updated for three new "
                "Q4 vendors, (3) data retention policy needs amendment for employee data. Action plan drafted."
            ),
            author="DPO",
        ),
        LegalNote(
            reference_type="compliance",
            reference_id=compliance_items[3].id,
            content=(
                "URGENT — Safety training non-compliance. HR has notified all department heads. "
                "Remedial sessions booked for next Tuesday and Wednesday. Non-compliant employees "
                "will be suspended from client-facing roles until training is completed."
            ),
            author="HR Director",
        ),
        LegalNote(
            reference_type="general",
            reference_id=None,
            content=(
                "Q1 Legal Review Meeting scheduled for next month. Agenda: (1) NDA renewal decisions, "
                "(2) GDPR compliance gaps, (3) ISO 27001 audit readiness, (4) pending employment "
                "contract amendments, (5) vendor agreement pipeline. All department heads to attend."
            ),
            author="General Counsel",
        ),
    ]
    db.add_all(notes)
    db.commit()
    print("Database seeded with sample data.")
