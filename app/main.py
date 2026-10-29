import logging
import os
import time
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db import Base, Operation, SessionLocal, engine, get_db
from app.logging_conf import setup_logging

setup_logging()
log = logging.getLogger("apex")

REQUESTS = Counter("http_requests_total", "Total requests", ["method", "path", "status"])
LATENCY = Histogram("http_request_duration_seconds", "Request latency", ["path"])


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        Base.metadata.create_all(engine)
        log.info("startup complete", extra={"fields": {"version": os.getenv("APP_VERSION", "dev")}})
    except Exception as exc:
        log.error("db init failed", extra={"fields": {"error": str(exc)}})
    yield


app = FastAPI(title="Apex Operations API", lifespan=lifespan)


@app.middleware("http")
async def observe(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - start
    route = request.scope.get("route")
    path = route.path if route else request.url.path
    REQUESTS.labels(request.method, path, response.status_code).inc()
    LATENCY.labels(path).observe(duration)
    log.info(
        "request",
        extra={"fields": {"method": request.method, "path": request.url.path,
                          "status": response.status_code,
                          "duration_ms": round(duration * 1000, 2)}},
    )
    return response


class OperationIn(BaseModel):
    name: str = Field(min_length=1, max_length=100)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/ready")
def ready():
    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception as exc:
        log.error("readiness failed", extra={"fields": {"error": str(exc)}})
        raise HTTPException(status_code=503, detail="database unavailable")


@app.get("/version")
def version():
    return {"version": os.getenv("APP_VERSION", "dev")}


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/operations", status_code=201)
def create_operation(body: OperationIn, db: Session = Depends(get_db)):
    op = Operation(name=body.name)
    db.add(op)
    db.commit()
    db.refresh(op)
    return {"id": op.id, "name": op.name, "status": op.status}


@app.get("/operations/{op_id}")
def get_operation(op_id: int, db: Session = Depends(get_db)):
    op = db.get(Operation, op_id)
    if not op:
        raise HTTPException(status_code=404, detail="operation not found")
    return {"id": op.id, "name": op.name, "status": op.status}
