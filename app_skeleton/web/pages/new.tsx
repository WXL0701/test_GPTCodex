import { useState } from 'react';

export default function NewJob() {
  const [inputDir, setInputDir] = useState('');
  const [jobName, setJobName] = useState('');
  const [params, setParams] = useState('{}');
  const [message, setMessage] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setMessage(null);
    try {
      const body = {
        input_dir: inputDir,
        job_name: jobName,
        params: JSON.parse(params || '{}'),
      };
      const res = await fetch('http://localhost:8000/api/jobs', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      if (!res.ok) {
        throw new Error(await res.text());
      }
      const job = await res.json();
      setMessage(`Created job with ID: ${job.job_id}`);
      setInputDir('');
      setJobName('');
      setParams('{}');
    } catch (err: any) {
      setMessage(`Error creating job: ${err.message}`);
    }
  }

  return (
    <main style={{ padding: '2rem', fontFamily: 'sans-serif' }}>
      <h1>Submit New Job</h1>
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', maxWidth: '400px' }}>
        <label>
          Input Directory
          <input
            type="text"
            value={inputDir}
            onChange={(e) => setInputDir(e.target.value)}
            style={{ width: '100%', padding: '0.5rem', marginBottom: '1rem' }}
            required
          />
        </label>
        <label>
          Job Name
          <input
            type="text"
            value={jobName}
            onChange={(e) => setJobName(e.target.value)}
            style={{ width: '100%', padding: '0.5rem', marginBottom: '1rem' }}
            required
          />
        </label>
        <label>
          Parameters (JSON)
          <textarea
            value={params}
            onChange={(e) => setParams(e.target.value)}
            style={{ width: '100%', padding: '0.5rem', marginBottom: '1rem', fontFamily: 'monospace' }}
            rows={6}
          />
        </label>
        <button type="submit" style={{ padding: '0.75rem', cursor: 'pointer' }}>Create Job</button>
      </form>
      {message && <p style={{ marginTop: '1rem' }}>{message}</p>}
    </main>
  );
}