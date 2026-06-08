import { useState } from 'react';
import { Upload, FileCheck2, AlertCircle, Loader2, Trash2, Database, Files } from 'lucide-react';
import { deleteDocument, uploadDocuments } from '../api/client';

export default function DocumentPanel({ documents, setDocuments, status, refreshStatus, refreshWorkspace, uploadState, setUploadState }) {
  const [deletingId, setDeletingId] = useState('');

  async function handleUpload(event) {
    const files = Array.from(event.target.files || []);
    if (!files.length) return;

    setUploadState({ loading: true, error: '' });
    try {
      await uploadDocuments(files);
      await refreshWorkspace();
      setUploadState({ loading: false, error: '' });
    } catch (error) {
      setUploadState({ loading: false, error: error.message });
    } finally {
      event.target.value = '';
    }
  }

  async function handleDelete(documentId, filename) {
    const shouldDelete = window.confirm(`Delete "${filename}" from the index?`);
    if (!shouldDelete) return;

    setDeletingId(documentId);
    setUploadState({ loading: false, error: '' });
    try {
      await deleteDocument(documentId);
      await refreshWorkspace();
    } catch (error) {
      setUploadState({ loading: false, error: error.message });
    } finally {
      setDeletingId('');
    }
  }

  return (
    <aside className="flex max-h-[42vh] flex-col border-r border-slate-200 bg-white md:h-full md:max-h-none">
      <div className="shrink-0 border-b border-slate-200 p-5">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded bg-pine text-white">
            <Database className="h-5 w-5" />
          </div>
          <div>
            <h1 className="text-lg font-semibold text-ink">Document Chat</h1>
            <p className="text-sm text-slate-500">PDF search workspace</p>
          </div>
        </div>
        <div className="mt-5 grid grid-cols-2 gap-2">
          <div className="rounded border border-slate-200 bg-slate-50 p-3">
            <p className="text-xs font-medium uppercase tracking-wide text-slate-500">Documents</p>
            <p className="mt-1 text-xl font-semibold text-ink">{status.documents}</p>
          </div>
          <div className="rounded border border-slate-200 bg-slate-50 p-3">
            <p className="text-xs font-medium uppercase tracking-wide text-slate-500">Chunks</p>
            <p className="mt-1 text-xl font-semibold text-ink">{status.chunks}</p>
          </div>
        </div>
      </div>

      <div className="shrink-0 p-5">
        <label className="flex cursor-pointer items-center justify-center gap-2 rounded border border-dashed border-pine bg-emerald-50 px-4 py-4 text-sm font-semibold text-pine transition hover:bg-emerald-100">
          {uploadState.loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Upload className="h-4 w-4" />}
          Upload PDFs
          <input type="file" accept="application/pdf" multiple className="hidden" onChange={handleUpload} disabled={uploadState.loading} />
        </label>
        {uploadState.error && (
          <div className="mt-3 flex gap-2 rounded border border-red-100 bg-red-50 p-3 text-sm text-red-700">
            <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
            {uploadState.error}
          </div>
        )}
      </div>

      <div className="min-h-0 flex-1 overflow-y-auto px-5 pb-5">
        <div className="mb-3 flex items-center justify-between">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">Indexed Files</h2>
          <Files className="h-4 w-4 text-slate-400" />
        </div>
        <div className="space-y-2">
          {documents.length === 0 ? (
            <p className="rounded border border-slate-200 bg-slate-50 p-4 text-sm leading-6 text-slate-500">Upload PDFs to start asking grounded questions.</p>
          ) : (
            documents.map((doc) => (
              <div key={doc.id} className="rounded border border-slate-200 bg-white p-3 shadow-sm transition hover:border-emerald-200 hover:bg-emerald-50/40">
                <div className="flex items-start gap-2">
                  <div className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded bg-emerald-50 text-pine">
                    <FileCheck2 className="h-4 w-4" />
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-medium text-ink">{doc.filename}</p>
                    <p className="text-xs text-slate-500">{doc.pages} pages - {doc.chunks} chunks</p>
                  </div>
                  <button
                    type="button"
                    onClick={() => handleDelete(doc.id, doc.filename)}
                    disabled={deletingId === doc.id}
                    className="inline-flex h-8 w-8 shrink-0 items-center justify-center rounded text-slate-400 transition hover:bg-red-50 hover:text-red-700 disabled:cursor-not-allowed disabled:opacity-60"
                    title={`Delete ${doc.filename}`}
                  >
                    {deletingId === doc.id ? <Loader2 className="h-4 w-4 animate-spin" /> : <Trash2 className="h-4 w-4" />}
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </aside>
  );
}
