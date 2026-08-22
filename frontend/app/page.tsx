import { CollectorDashboard } from '../components/CollectorDashboard';

export default function Home() {
  return (
    <main className="layout-container">
      <header className="header">
        <h1>WEBMORPH</h1>
        <p className="mono">Infrastructure Intelligence / Web Compatibility Monitoring</p>
      </header>
      
      <CollectorDashboard />
    </main>
  );
}
