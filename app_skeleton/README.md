# Remote Matlab Analysis Portal Skeleton

This repository contains a minimal skeleton for a remote Matlab analysis portal
based on the design outlined in the requirements document.  The goal of this
project is to provide a starting point for a full‑featured web application that
allows users to submit image analysis tasks to a Matlab server, monitor their
progress and system status, and download results when they are complete.

The skeleton includes the following components:

* **`api/`** – A FastAPI service that exposes RESTful endpoints for creating jobs,
  listing jobs, retrieving job details, and reporting system status.  This
  initial implementation uses an in‑memory data store to track jobs and
  returns mock system metrics; replace these with your own database and
  monitoring code in a production deployment.
* **`worker/`** – A placeholder worker script that demonstrates where job
  execution logic will live.  In a full implementation this process would
  listen on a queue, run Matlab in batch mode, write logs and progress
  information, and update job status accordingly.
* **`web/`** – A Next.js application that provides a basic user interface for
  interacting with the API.  It includes pages for the dashboard, job
  submission, job listing, and job details.  The pages fetch data from the
  FastAPI service and render simple tables and forms.  Styling has been kept
  deliberately minimal; you can extend it with Tailwind CSS or another
  framework to match your needs.

## Prerequisites

This skeleton uses Python for the API and worker, and Node.js for the front end.
You will need the following installed on your development machine:

* **Python 3.10+** with `pip` and `virtualenv` for the API and worker.
* **Node.js 16+** and `npm` or `yarn` for the Next.js front end.

You can install backend dependencies with:

```bash
cd app_skeleton/api
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

And install front‑end dependencies with:

```bash
cd app_skeleton/web
npm install
```

## Running the development servers

### Start the API server

From the `api` directory, run:

```bash
uvicorn main:app --reload
```

This will start the FastAPI app on `http://localhost:8000`.  The API
documentation will be available at `http://localhost:8000/docs`.

### Start the Next.js front end

From the `web` directory, run:

```bash
npm run dev
```

This will start the development server on `http://localhost:3000`.  The
front‑end is configured to proxy API requests to the local FastAPI server.

## Extending the skeleton

This repository is intended to give you a head start on building the full
portal.  To build upon it:

* Replace the in‑memory job store with a proper database such as SQLite or
  PostgreSQL.
* Implement a task queue (e.g. Redis + RQ or Celery) and hook up the worker
  to process jobs concurrently with semaphore control.
* Write the Matlab wrapper script that reads configuration JSON, runs the
  analysis, writes progress to `progress.json` and logs to `run.log`, and
  generates result files.
* Build out the dashboard with CPU, memory and disk metrics, queue length,
  running jobs, and version information by querying your actual system.

Feel free to customise the structure, add Dockerfiles, environment
configuration, authentication and other features as needed for your use case.