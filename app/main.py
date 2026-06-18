from fastapi import FastAPI
from app.routes import router
from app.retell_webhook import router as retell_router

app = FastAPI(title="Riverstone Pet Clinic Voice Agent")
app.include_router(router)
app.include_router(retell_router)


@app.get("/health")
def health():
    return {"status": "ok", "clinic": "Riverstone Pet Clinic"}
