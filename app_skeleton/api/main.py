"""FastAPI application for the remote Matlab analysis portal skeleton.

This module defines a handful of REST endpoints that conform loosely to the
design presented in the requirements.  The goal is to provide a running
service that the front end can interact with during development.  Job
tracking is done in memory and no real tasks are executed.
"""

import asyncio
import logging
import os
import random
import time
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from .database import InMemoryJobStore
from .models import (
    HealthCheck,
    Job,
    JobCreate,
    JobDetailResponse,
    JobStatus,
    JobSummary,
    Progress,
    QueueStatus,
    SystemHealth,
    SystemResources,
    SystemStatusResponse,
    VersionsResponse,
    VersionInfo,
    WorkerStatus,
)

logger = logging.getLogger(__name__)


def get_store() -> InMemoryJobStore:
    """Provide a singleton in‑memory job store."""
    # In a production app this would return a database session or other
    # resource tied to the request context.
    if not hasattr(get_store, "_store"):
        get_store._store = InMemoryJobStore()  # type: ignore
    return get_store._store  # type: ignore


app = FastAPI(title="Matlab Analysis Portal API", version="0.1.0")

# Allow CORS from the local front‑end by default
origins = [
    "http://localhost",
    "http://localhost:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.post("/api/jobs", response_model=Job)
async def create_job(job: JobCreate, store: InMemoryJobStore = Depends(get_store)) -> Job:
    """Create a new analysis job.

    In a real implementation the caller would be authenticated and the
    `user_id` would come from the auth context.  Here we use a fixed
    dummy value.
    """
    user_id = "demo-user"
    created = store.create_job(user_id=user_id, job_data=job)
    logger.info(f"Created job {created.job_id} for {user_id}")
    # Simulate asynchronous start of job after a short delay
    asyncio.create_task(_simulate_job_lifecycle(created.job_id, store))
    return created


@app.get("/api/jobs", response_model=List[JobSummary])
async def list_jobs(
    status: Optional[JobStatus] = Query(None, description="Filter by job status"),
    store: InMemoryJobStore = Depends(get_store),
) -> List[JobSummary]:
    """Return a list of jobs, optionally filtered by status."""
    return store.list_jobs(status=status)


@app.get("/api/jobs/{job_id}", response_model=JobDetailResponse)
async def job_detail(job_id: str, store: InMemoryJobStore = Depends(get_store)) -> JobDetailResponse:
    """Return detailed information about a single job."""
    job = store.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    # Return dummy progress for demonstration
    progress = None
    if job.status == JobStatus.RUNNING:
        progress = Progress(stage="PROCESSING", percent=random.random() * 100)
    # Return a fake log tail
    log_tail = f"Log output for job {job_id}\nThis is only a placeholder."
    return JobDetailResponse(job=job, progress=progress, log_tail=log_tail)


@app.get("/api/system/status", response_model=SystemStatusResponse)
async def system_status() -> SystemStatusResponse:
    """Return mock system metrics and health information."""
    now = time.time()
    resources = SystemResources(
        cpu_pct=random.uniform(0, 50),
        mem_pct=random.uniform(20, 80),
        disk_pct=random.uniform(30, 70),
    )
    queue = QueueStatus(
        queue_length=random.randint(0, 3),
        running=random.randint(0, 1),
        max_concurrent_matlab=1,
    )
    workers = WorkerStatus(active=1, last_seen_sec=random.uniform(0, 5))
    checks = {
        "redis": HealthCheck(ok=True),
        "db": HealthCheck(ok=True),
        "matlab_probe": HealthCheck(ok=True, latency_ms=100),
    }
    health = SystemHealth(overall="GREEN", checks=checks, updated_at=now)
    return SystemStatusResponse(
        resources=resources,
        queue=queue,
        workers=workers,
        health=health,
        updated_at=now,
    )


@app.get("/api/system/versions", response_model=VersionsResponse)
async def system_versions() -> VersionsResponse:
    """Return placeholder version information for Matlab and the analysis package."""
    now = time.time()
    matlab_version = VersionInfo(version="R2023a", detail="Mock version")
    package_version = VersionInfo(version="1.0.0", detail="Mock package version")
    return VersionsResponse(matlab=matlab_version, analysis_package=package_version, server_time=now)


async def _simulate_job_lifecycle(job_id: str, store: InMemoryJobStore) -> None:
    """Simulate progression of a job through RUNNING to SUCCEEDED after a delay."""
    # Wait briefly before marking as running
    await asyncio.sleep(1)
    store.update_job_status(job_id, JobStatus.RUNNING)
    # Simulate processing time
    await asyncio.sleep(3)
    # Randomly decide if the job succeeds or fails
    if random.random() < 0.9:
        store.update_job_status(job_id, JobStatus.SUCCEEDED)
    else:
        store.update_job_status(job_id, JobStatus.FAILED, error_message="Simulated failure")