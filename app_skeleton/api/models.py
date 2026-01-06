"""Pydantic models for the Matlab analysis portal API.

These data classes define the request and response bodies for the
FastAPI application.  They are intentionally simple and focus on the
fields needed for the basic skeleton.
"""

from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    """Enumeration of possible job states."""

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class JobCreate(BaseModel):
    """Schema for creating a new analysis job."""

    input_dir: str = Field(..., description="Path to the input images directory on the server")
    job_name: str = Field(..., description="Human readable name for the job")
    params: Dict[str, Any] = Field(default_factory=dict, description="Analysis parameters")


class Job(BaseModel):
    """Schema representing an analysis job persisted by the API."""

    job_id: str
    user_id: str
    input_dir: str
    job_name: str
    params: Dict[str, Any]
    status: JobStatus
    created_at: float
    started_at: Optional[float] = None
    finished_at: Optional[float] = None
    result_csv_path: Optional[str] = None
    error_message: Optional[str] = None


class JobSummary(BaseModel):
    """A lightweight view of a job for list endpoints."""

    job_id: str
    job_name: str
    status: JobStatus
    created_at: float
    started_at: Optional[float]
    finished_at: Optional[float]


class Progress(BaseModel):
    """Progress information returned by job detail endpoint."""

    stage: str
    percent: float
    message: Optional[str] = None
    updated_at: Optional[float] = None


class JobDetailResponse(BaseModel):
    """Wrapper for job detail including progress and log snippet."""

    job: Job
    progress: Optional[Progress] = None
    log_tail: Optional[str] = None


class SystemResources(BaseModel):
    cpu_pct: float
    mem_pct: float
    disk_pct: float


class QueueStatus(BaseModel):
    queue_length: int
    running: int
    max_concurrent_matlab: int


class WorkerStatus(BaseModel):
    active: int
    last_seen_sec: float


class HealthCheck(BaseModel):
    ok: bool
    message: Optional[str] = None
    latency_ms: Optional[int] = None


class SystemHealth(BaseModel):
    overall: str
    checks: Dict[str, HealthCheck]
    updated_at: float


class SystemStatusResponse(BaseModel):
    resources: SystemResources
    queue: QueueStatus
    workers: WorkerStatus
    health: SystemHealth
    updated_at: float


class VersionInfo(BaseModel):
    version: str
    detail: Optional[str] = None


class VersionsResponse(BaseModel):
    matlab: VersionInfo
    analysis_package: VersionInfo
    server_time: float