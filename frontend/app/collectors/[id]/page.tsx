import Link from 'next/link';
import { ContinuousIntelligence } from '../../../components/intelligence/ContinuousIntelligence';

export default async function CollectorPage({ params }: { params: { id: string } }) {
  const collectorId = parseInt(params.id, 10);
  
  if (isNaN(collectorId)) {
    return (
      <main className="layout-container">
        <div style={{ color: 'var(--accent-magenta)', padding: '24px', border: '1px solid rgba(255,0,85,0.2)', backgroundColor: 'rgba(255,0,85,0.05)', borderRadius: '4px' }}>
          <strong>ERROR:</strong> Invalid Collector ID
        </div>
      </main>
    );
  }

  return (
    <main className="layout-container">
      <header className="header" style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center', marginBottom: '16px' }}>
          <Link href="/" style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>← BACK TO DASHBOARD</Link>
        </div>
        <h1>COLLECTOR {collectorId} INTELLIGENCE</h1>
      </header>
      
      <ContinuousIntelligence collectorId={collectorId} />
    </main>
  );
}
