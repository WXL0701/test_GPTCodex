import { useRouter } from 'next/router';
import { useEffect, useState } from 'react';

interface JobDetailResponse {
  job: {
    job_id: string;
    job_name: string;
    status: string;
    created_at: number;
    started_at: number | null;
    finished_at: number | null;
    error_message?: string | null;
  };
  progress?: {
    stage: string;
    percent: number;
    message?: string | null;
  } | null;
  log_tail?: string | null;
}

export default function JobDetail() {
  const router = useRouter();
  const { id } = router.query;
  const [data, setData] = useState<JobDetailResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    if (!id) return;
    try {
      const res = await fetch(`http://localhost:8000/api/jobs/${id}`);
      if (!res.ok) {
        throw new Error(await res.text());
      }
      const json = await res.json();
      setData(json);
    } catch (err: any) {
      setError(err.message);
    }
  }

  useEffect(() => {
    load();
    const timer = setInterval(load, 2000);
    return () => clearInterval(timer);
  }, [id]);

  if (!id) return <p>Loading…</p>;

  return (
    <main style={{ padding: '2rem', fontFamily: 'sans-serif' }}>
      <h1>Job Details</h1>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {data ? (
        <>
          <h2>{data.job.job_name}</h2>
          <p>ID: {data.job.job_id}</p>
          <p>Status: {data.job.status}</p>
          <p>Created: {new Date(data.job.created_at * 1000).toLocaleString()}</p>
          {data.job.started_at && <p>Started: {new Date(data.job.started_at * 1000).toLocaleString()}</p>}
          {data.job.finished_at && <p>Finished: {new Date(data.job.finished_at * 1000).toLocaleString()}</p>}
          {data.job.error_message && <p>Error: {data.job.error_message}</p>}
          {data.progress && (
            <div style={{ marginTop: '1rem' }}>
              <h3>Progress</h3>
              <p>Stage: {data.progress.stage}</p>
              <p>Percent: {data.progress.percent.toFixed(1)}%</p>
              {data.progress.message && <p>Message: {data.progress.message}</p>}
            </div>
          )}
          {data.log_tail && (
            <div style={{ marginTop: '1rem' }}>
              <h3>Log</h3>
              <pre style={{ background: '#f9f9f9', padding: '1rem', whiteSpace: 'pre-wrap' }}>{data.log_tail}</pre>
            </div>
          )}
        </>
      ) : (
        <p>Loading job details…</p>
      )}
    </main>
  );
}