import { useEffect, useState } from 'react';

interface SystemStatus {
  resources: { cpu_pct: number; mem_pct: number; disk_pct: number };
  queue: { queue_length: number; running: number; max_concurrent_matlab: number };
  workers: { active: number; last_seen_sec: number };
  health: { overall: string };
  updated_at: number;
}

export default function Dashboard() {
  const [status, setStatus] = useState<SystemStatus | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const res = await fetch('http://localhost:8000/api/system/status');
        if (!res.ok) {
          throw new Error(await res.text());
        }
        const data: SystemStatus = await res.json();
        setStatus(data);
      } catch (err) {
        console.error(err);
      }
    }
    load();
    const timer = setInterval(load, 3000);
    return () => clearInterval(timer);
  }, []);

  return (
    <main style={{ padding: '2rem', fontFamily: 'sans-serif' }}>
      <h1>Matlab Analysis Portal</h1>
      <p>This dashboard shows mock system metrics and job queue information.</p>
      {status ? (
        <div style={{ marginTop: '1rem' }}>
          <h2>System Resources</h2>
          <ul>
            <li>CPU Usage: {status.resources.cpu_pct.toFixed(1)}%</li>
            <li>Memory Usage: {status.resources.mem_pct.toFixed(1)}%</li>
            <li>Disk Usage: {status.resources.disk_pct.toFixed(1)}%</li>
          </ul>
          <h2>Queue</h2>
          <ul>
            <li>Jobs Waiting: {status.queue.queue_length}</li>
            <li>Jobs Running: {status.queue.running}</li>
            <li>Max Concurrent Matlab: {status.queue.max_concurrent_matlab}</li>
          </ul>
          <h2>Health</h2>
          <p>Overall: {status.health.overall}</p>
        </div>
      ) : (
        <p>Loading system status…</p>
      )}
    </main>
  );
}