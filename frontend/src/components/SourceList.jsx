import { FileText } from 'lucide-react';

export default function SourceList({ sources }) {
  if (!sources?.length) return null;

  return (
    <div className="mt-4 space-y-2">
      {sources.map((source, index) => (
        <details key={source.chunk_id} className="rounded border border-slate-200 bg-slate-50 px-3 py-2">
          <summary className="flex cursor-pointer items-center gap-2 text-sm font-medium text-ink">
            <FileText className="h-4 w-4 shrink-0 text-pine" />
            <span className="min-w-0 truncate">
              [{index + 1}] {source.filename} - page {source.page} - score {source.score.toFixed(2)}
            </span>
          </summary>
          <p className="mt-2 text-sm leading-6 text-slate-600">{source.text}</p>
        </details>
      ))}
    </div>
  );
}
