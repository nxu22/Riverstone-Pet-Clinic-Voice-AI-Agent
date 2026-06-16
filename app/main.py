from fastapi import FastAPI

app = FastAPI(title="Riverstone Pet Clinic Voice Agent")


@app.get("/health")
def health():
    return {"status": "ok", "clinic": "Riverstone Pet Clinic"}
