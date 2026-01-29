from fastapi import FastAPI

from app.routers import projects, cabinets, skus, kb, events, settings, balance, xlsx, admin_metrics

app = FastAPI(title="mp_reviews_bot")

app.include_router(projects.router)
app.include_router(cabinets.router)
app.include_router(skus.router)
app.include_router(kb.router)
app.include_router(events.router)
app.include_router(settings.router)
app.include_router(balance.router)
app.include_router(xlsx.router)
app.include_router(admin_metrics.router)


@app.get("/health")
def health():
    return {"status": "ok"}
