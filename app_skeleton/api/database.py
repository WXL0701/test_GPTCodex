"""Simple in‑memory job storage for the analysis portal.

This module implements a naive data store to keep track of job objects
while the API is running.  It is not persistent and is intended only for
demonstration purposes.  Replace this with a proper database layer in a
production application.
"""

import threading
import time
import uuid
from typing import Dict, List, Optional

from .models import Job, JobCreate, JobStatus, JobSummary


class InMemoryJobStore:
    """Thread‑safe in‑memory store for jobs."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._jobs: Dict[str, Job] = {}

    def create_job(self, user_id: str, job_data: JobCreate) -> Job:
        """Create a new job record and return it."""
        job_id = f"{int(time.time())}_{uuid.uuid4().hex[:8]}"
        now = time.time()
        job = Job(
            job_id=job_id,
            user_id=user_id,
            input_dir=job_data.input_dir,
            job_name=job_data.job_name,
            params=job_data.params,
            status=JobStatus.PENDING,
            created_at=now,
        )
        with self._lock:
            self._jobs[job_id] = job
        return job

    def list_jobs(self, user_id: Optional[str] = None, status: Optional[JobStatus] = None) -> List[JobSummary]:
        """Return a summary view of all jobs, optionally filtered by user or status."""
        with self._lock:
            jobs = list(self._jobs.values())
        filtered = []
        for job in jobs:
            if user_id and job.user_id != user_id:
                continue
            if status and job.status != status:
                continue
            filtered.append(
                JobSummary(
                    job_id=job.job_id,
                    job_name=job.job_name,
                    status=job.status,
                    created_at=job.created_at,
                    started_at=job.started_at,
                    finished_at=job.finished_at,
                )
            )
        # sort by creation time descending
        return sorted(filtered, key=lambda j: j.created_at, reverse=True)

    def get_job(self, job_id: str) -> Optional[Job]:
        """Return a job by ID or None if not found."""
        with self._lock:
            return self._jobs.get(job_id)

    def update_job_status(self, job_id: str, status: JobStatus, error_message: Optional[str] = None) -> None:
        """Update the status of a job."""
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return
            job.status = status
            if status in (JobStatus.SUCCEEDED, JobStatus.FAILED, JobStatus.CANCELLED):
                job.finished_at = time.time()
            if error_message:
                job.error_message = error_message