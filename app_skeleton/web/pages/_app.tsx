import type { AppProps } from 'next/app';
import Link from 'next/link';

export default function MyApp({ Component, pageProps }: AppProps) {
  return (
    <>
      <nav style={{ padding: '1rem', background: '#f5f5f5' }}>
        <Link href="/" style={{ marginRight: '1rem' }}>Dashboard</Link>
        <Link href="/jobs" style={{ marginRight: '1rem' }}>Jobs</Link>
        <Link href="/new">New Job</Link>
      </nav>
      <Component {...pageProps} />
    </>
  );
}