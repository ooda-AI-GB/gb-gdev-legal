from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import func as sqlfunc

from .database import SessionLocal, engine, get_db
from . import models
from .models import Contract, Clause, ComplianceItem, LegalContact, LegalNote
from .routers import clauses, compliance, contacts, contracts, dashboard, notes


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Auto-create all tables on startup
    models.Base.metadata.create_all(bind=engine)

    # Seed sample data if the database is empty
    db = SessionLocal()
    try:
        from .seed import seed_db
        seed_db(db)
    finally:
        db.close()

    yield


app = FastAPI(
    title="Legal Pro API",
    description=(
        "Contract and document management platform for business legal operations. "
        "Manage contracts, clauses, compliance obligations, legal contacts and notes "
        "from a single API. Authenticate with the X-API-Key header."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

from viv_auth import init_auth
init_auth(app, engine, models.Base, get_db, app_name="Legal Pro")


# ---------------------------------------------------------------------------
# Root dashboard — no auth required
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def root_dashboard(db: Session = Depends(get_db)):
    contract_count = db.query(sqlfunc.count(Contract.id)).scalar() or 0
    active = db.query(sqlfunc.count(Contract.id)).filter(Contract.status == "active").scalar() or 0
    draft = db.query(sqlfunc.count(Contract.id)).filter(Contract.status == "draft").scalar() or 0
    expired = db.query(sqlfunc.count(Contract.id)).filter(Contract.status == "expired").scalar() or 0
    clause_count = db.query(sqlfunc.count(Clause.id)).scalar() or 0
    compliance_count = db.query(sqlfunc.count(ComplianceItem.id)).scalar() or 0
    contact_count = db.query(sqlfunc.count(LegalContact.id)).scalar() or 0
    note_count = db.query(sqlfunc.count(LegalNote.id)).scalar() or 0
    recent = db.query(Contract).order_by(Contract.created_at.desc()).limit(8).all()
    status_colors = {"draft": "#f5a623", "review": "#4f8ef7", "active": "#34c759", "expired": "#e74c3c", "terminated": "#7f8c9b"}
    rows = ""
    for c in recent:
        sc = status_colors.get(c.status.value if hasattr(c.status, 'value') else str(c.status), "#7f8c9b")
        st = c.status.value if hasattr(c.status, 'value') else str(c.status)
        val = f"${c.value:,.2f}" if c.value else "—"
        end = str(c.end_date) if c.end_date else "—"
        rows += f'<tr><td>{c.title}</td><td>{c.counterparty}</td><td><span style="color:{sc};font-weight:600">{st}</span></td><td>{val}</td><td>{end}</td></tr>'
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>Legal Pro</title>
<style>
:root{{--primary:#4f8ef7;--success:#34c759;--warning:#f5a623;--danger:#e74c3c;--bg:#1a1f36;--bg-light:#f5f7fa;--card:#fff;--text:#2c3e50;--muted:#7f8c9b;--border:#e1e5eb}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:system-ui,-apple-system,sans-serif;background:var(--bg-light);color:var(--text);display:flex;min-height:100vh}}
.sidebar{{width:240px;background:var(--bg);color:#fff;display:flex;flex-direction:column;flex-shrink:0}}
.logo{{padding:1.5rem;font-size:1.4rem;font-weight:700}}
.nav-links{{flex:1;padding:0 1rem}}
.nav-link{{display:block;padding:.75rem 1rem;color:#cbd5e1;text-decoration:none;border-radius:6px;margin-bottom:.25rem}}
.nav-link:hover,.nav-link.active{{background:rgba(255,255,255,.15);color:#fff}}
.main{{flex:1;padding:2rem;overflow-y:auto}}
h1{{font-size:1.8rem;margin-bottom:1.5rem}}
.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:1rem;margin-bottom:2rem}}
.card{{background:var(--card);border-radius:10px;padding:1.5rem;border:1px solid var(--border)}}
.card .label{{font-size:.85rem;color:var(--muted);margin-bottom:.25rem}}
.card .value{{font-size:1.6rem;font-weight:700}}
.card .value.blue{{color:var(--primary)}} .card .value.green{{color:var(--success)}} .card .value.orange{{color:var(--warning)}} .card .value.red{{color:var(--danger)}}
table{{width:100%;border-collapse:collapse;background:var(--card);border-radius:10px;overflow:hidden;border:1px solid var(--border)}}
th,td{{padding:.75rem 1rem;text-align:left;border-bottom:1px solid var(--border)}}
th{{background:var(--bg);color:#fff;font-weight:600;font-size:.85rem;text-transform:uppercase;letter-spacing:.5px}}
tr:last-child td{{border-bottom:none}}
.section-title{{font-size:1.1rem;font-weight:600;margin-bottom:1rem}}
a.api-link{{display:inline-block;margin-top:1rem;padding:.5rem 1rem;background:var(--primary);color:#fff;border-radius:6px;text-decoration:none;font-size:.9rem}}
</style></head><body>
<div class="sidebar">
  <div class="logo">Legal Pro</div>
  <div class="nav-links">
    <a href="/" class="nav-link active">Dashboard</a>
    <a href="/docs" class="nav-link">API Docs</a>
  </div>
</div>
<div class="main">
  <h1>Dashboard</h1>
  <div class="cards">
    <div class="card"><div class="label">Contracts</div><div class="value blue">{contract_count}</div></div>
    <div class="card"><div class="label">Active</div><div class="value green">{active}</div></div>
    <div class="card"><div class="label">Draft</div><div class="value orange">{draft}</div></div>
    <div class="card"><div class="label">Expired</div><div class="value red">{expired}</div></div>
    <div class="card"><div class="label">Clauses</div><div class="value">{clause_count}</div></div>
    <div class="card"><div class="label">Compliance</div><div class="value">{compliance_count}</div></div>
    <div class="card"><div class="label">Contacts</div><div class="value">{contact_count}</div></div>
    <div class="card"><div class="label">Notes</div><div class="value">{note_count}</div></div>
  </div>
  <div class="section-title">Recent Contracts</div>
  <table><thead><tr><th>Title</th><th>Counterparty</th><th>Status</th><th>Value</th><th>End Date</th></tr></thead><tbody>{rows if rows else '<tr><td colspan="5" style="text-align:center;color:var(--muted)">No contracts yet</td></tr>'}</tbody></table>
  <a href="/docs" class="api-link">API Documentation &rarr;</a>
</div></body></html>"""


# ---------------------------------------------------------------------------
# Health check — no auth required
# ---------------------------------------------------------------------------

@app.get("/health", tags=["Health"], include_in_schema=True)
def health():
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# API v1 routers
# ---------------------------------------------------------------------------

app.include_router(contracts.router, prefix="/api/v1", tags=["Contracts"])
app.include_router(clauses.router,   prefix="/api/v1", tags=["Clauses"])
app.include_router(compliance.router, prefix="/api/v1", tags=["Compliance"])
app.include_router(contacts.router,  prefix="/api/v1", tags=["Legal Contacts"])
app.include_router(notes.router,     prefix="/api/v1", tags=["Legal Notes"])
app.include_router(dashboard.router, prefix="/api/v1", tags=["Dashboard"])
