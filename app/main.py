from contextlib import asynccontextmanager

from fastapi import FastAPI

from .database import SessionLocal, engine
from . import models
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
