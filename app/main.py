from fastapi import FastAPI
import os

app = FastAPI()

@app.get("/")
def root():
    return {
        "message": "Hello from AKS demo app 👋",
        "env": os.getenv("APP_ENV", "unknown"),
        "version": os.getenv("APP_VERSION", "dev"),
    }

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.get("/info")
def info():
    return {"status": "This endpoint is the new endpoint"}

@app.get("/readyz")
def readyz():
    # In real apps you'd check DB/Redis connection here.
    return {"status": "ready"}
