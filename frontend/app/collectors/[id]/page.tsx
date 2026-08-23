import Link from 'next/link';
import { ContinuousIntelligence } from '../../../components/intelligence/ContinuousIntelligence';
import { PageHeader } from '@/components/ui/PageHeader';
import { ArrowLeft, Server } from 'lucide-react';
import { notFound } from 'next/navigation';

export default async function CollectorPage({ params }: { params: { id: string } }) {
  const collectorId = parseInt(params.id, 10);
  
  if (isNaN(collectorId)) {
    return notFound();
  }

  return (
    <>
      <div className="h-14 border-b border-gray-200 bg-white flex items-center px-6 sticky top-0 z-50 shadow-sm w-full">
        <Link href="/" className="flex items-center gap-2 text-[11px] font-bold uppercase tracking-widest text-gray-500 hover:text-gray-900 transition-colors group">
          <ArrowLeft className="w-3.5 h-3.5 group-hover:-translate-x-1 transition-transform" />
          Dashboard
        </Link>
        <div className="mx-4 h-4 w-px bg-gray-200" />
        <Link href="/collectors" className="flex items-center gap-2 text-[11px] font-bold uppercase tracking-widest text-gray-500 hover:text-gray-900 transition-colors">
          Collectors
        </Link>
        <div className="mx-4 h-4 w-px bg-gray-200" />
        <span className="text-[11px] font-bold uppercase tracking-widest text-gray-900 flex items-center gap-1.5">
          <Server className="w-3.5 h-3.5" />
          Collector-{collectorId}
        </span>
      </div>

      <div className="max-w-[1200px] w-full mx-auto p-6 md:p-8">
        <PageHeader 
          title={`Collector ${collectorId} Intelligence`}
          description="Real-time monitoring and schema validation metrics."
        />
        
        <div className="mt-8">
          <ContinuousIntelligence collectorId={collectorId} />
        </div>
      </div>
    </>
  );
}
