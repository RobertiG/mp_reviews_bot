from fastapi import FastAPI

from app.db import Base, engine
from app.routers import (
    admin_metrics,
    balance,
    cabinets,
    events,
    kb_rules,
    projects,
    settings,
    skus,
    xlsx_upload,
)

app = FastAPI(title="MP Reviews Bot API")


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


app.include_router(projects.router)
app.include_router(cabinets.router)
app.include_router(skus.router)
app.include_router(kb_rules.router)
app.include_router(events.router)
app.include_router(settings.router)
app.include_router(balance.router)
app.include_router(admin_metrics.router)
app.include_router(xlsx_upload.router)
