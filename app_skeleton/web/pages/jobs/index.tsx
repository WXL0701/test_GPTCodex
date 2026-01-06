import { useEffect, useState } from 'react';
import Link from 'next/link';

interface JobSummary {
  job_id: string;
  job_name: string;
  status: string;
  created_at: number;
  started_at: number | null;
  finished_at: number | null;
}

export default function JobsList() {
  const [jobs, setJobs] = useState<JobSummary[]>([]);
  const [error, setError] = useState<string | null>(null);

  async function loadJobs() {
    try {
      const res = await fetch('http://localhost:8000/api/jobs');
      if (!res.ok) {
        throw new Error(await res.text());
      }
      const data = await res.json();
      setJobs(data);
    } catch (err: any) {
      setError(err.message);
    }
  }

  useEffect(() => {
    loadJobs();
    const timer = setInterval(loadJobs, 3000);
    return () => clearInterval(timer);
  }, []);

  return (
    <main style={{ padding: '2rem', fontFamily: 'sans-serif' }}>
      <h1>Jobs</h1>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <table style={{ borderCollapse: 'collapse', width: '100%' }}>
        <thead>
          <tr>
            <th style={{ textAlign: 'left', borderBottom: '1px solid #ccc', padding: '0.5rem' }}>ID</th>
            <th style={{ textAlign: 'left', borderBottom: '1px solid #ccc', padding: '0.5rem' }}>Name</th>
            <th style={{ textAlign: 'left', borderBottom: '1px solid #ccc', padding: '0.5rem' }}>Status</th>
            <th style={{ textAlign: 'left', borderBottom: '1px solid #ccc', padding: '0.5rem' }}>Created</th>
          </tr>
        </thead>
        <tbody>
          {jobs.map((job) => (
            <tr key={job.job_id}>
              <td style={{ padding: '0.5rem' }}>
                <Link href={`/jobs/${job.job_id}`}>{job.job_id}</Link>
              </td>
              <td style={{ padding: '0.5rem' }}>{job.job_name}</td>
              <td style={{ padding: '0.5rem' }}>{job.status}</td>
              <td style={{ padding: '0.5rem' }}>{new Date(job.created_at * 1000).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </main>
  );
}