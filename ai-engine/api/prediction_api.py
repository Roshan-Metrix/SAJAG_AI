"""
SAJAG AI - Prediction API
FastAPI entry point for all ML model inference endpoints.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, BackgroundTasks
from loguru import logger

from utils.train_pipleline import registry

# WebSocket router (real-time updates)
from api.websocket_routes import router as ws_router

# Response schemas (used for type hints and docs)
from api.schemas import (
    FloodRiskResponse,
    LandslideRiskResponse,
    AccidentRiskResponse,
    CrowdPredictionResponse,
    PriorityResponse,
)


# ── Lifespan: load all models on startup ──────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Loading all SAJAG AI models on startup...")
    registry.load_all()
    logger.info(f"Models loaded: {registry.available_models}")
    yield
    logger.info("Shutting down SAJAG AI API")


# ── App ────────────────────────────────────────────────────────────────────────

app = FastAPI(title="SAJAG AI", lifespan=lifespan)
app.include_router(ws_router)


# ── Health ─────────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "ok", "models_loaded": registry.available_models}


# ── Flood ──────────────────────────────────────────────────────────────────────

@app.post("/predict/flood")
async def predict_flood(body: dict):
    name = "flood"
    if not registry.is_loaded(name):
        raise HTTPException(status_code=503, detail=f"Model {name} not loaded")
    try:
        result = registry.get(name).predict(body)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    return {"status": "success", "prediction": result}


# ── Landslide ─────────────────────────────────────────────────────────────────

@app.post("/predict/landslide")
async def predict_landslide(body: dict):
    name = "landslide"
    if not registry.is_loaded(name):
        raise HTTPException(status_code=503, detail=f"Model {name} not loaded")
    try:
        result = registry.get(name).predict(body)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    return {"status": "success", "prediction": result}


# ── Accident ──────────────────────────────────────────────────────────────────

@app.post("/predict/accident")
async def predict_accident(body: dict):
    name = "accident"
    if not registry.is_loaded(name):
        raise HTTPException(status_code=503, detail=f"Model {name} not loaded")
    try:
        result = registry.get(name).predict(body)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    return {"status": "success", "prediction": result}


# ── Crowd ─────────────────────────────────────────────────────────────────────

@app.post("/predict/crowd")
async def predict_crowd(body: dict):
    name = "crowd"
    if not registry.is_loaded(name):
        raise HTTPException(status_code=503, detail=f"Model {name} not loaded")
    try:
        result = registry.get(name).predict(body)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    return {"status": "success", "prediction": result}


# ── Priority ──────────────────────────────────────────────────────────────────

@app.post("/predict/priority")
async def predict_priority(body: dict):
    name = "priority"
    if not registry.is_loaded(name):
        raise HTTPException(status_code=503, detail=f"Model {name} not loaded")
    try:
        result = registry.get(name).predict(body)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    return {"status": "success", "prediction": result}


# ── Earthquake ────────────────────────────────────────────────────────────────

@app.post("/predict/earthquake")
async def predict_earthquake(body: dict):
    name = "earthquake"
    if not registry.is_loaded(name):
        raise HTTPException(status_code=503, detail=f"Model {name} not loaded")
    try:
        result = registry.get(name).predict(body)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    return {"status": "success", "prediction": result}