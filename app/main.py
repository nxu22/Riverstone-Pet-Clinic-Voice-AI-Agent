from fastapi import FastAPI
from app.routes import router

app = FastAPI(title="Riverstone Pet Clinic Voice Agent")
app.include_router(router)


@app.get("/health")
def health():
    return {"status": "ok", "clinic": "Riverstone Pet Clinic"}
