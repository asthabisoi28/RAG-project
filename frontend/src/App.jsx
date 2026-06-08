import { useEffect, useState } from 'react';
import { getHealth, listDocuments } from './api/client';
import ChatPanel from './components/ChatPanel';
import DocumentPanel from './components/DocumentPanel';

export default function App() {
  const [documents, setDocuments] = useState([]);
  const [status, setStatus] = useState({ documents: 0, chunks: 0 });
  const [uploadState, setUploadState] = useState({ loading: false, error: '' });

  async function refreshWorkspace() {
    const [docs, health] = await Promise.all([listDocuments(), getHealth()]);
    setDocuments(docs);
    setStatus({ documents: health.documents, chunks: health.chunks });
  }

  async function refreshStatus() {
    const health = await getHealth();
    setStatus({ documents: health.documents, chunks: health.chunks });
  }

  useEffect(() => {
    async function load() {
      try {
        await refreshWorkspace();
      } catch (error) {
        setUploadState({ loading: false, error: error.message });
      }
    }
    load();
  }, []);

  return (
    <div className="min-h-screen bg-[#eef3f1] text-ink md:h-screen md:overflow-hidden">
      <div className="grid min-h-screen grid-cols-1 border-slate-200 bg-white/70 shadow-soft md:m-4 md:h-[calc(100vh-2rem)] md:min-h-0 md:grid-cols-[360px_minmax(0,1fr)] md:overflow-hidden md:rounded-lg md:border">
        <DocumentPanel
          documents={documents}
          setDocuments={setDocuments}
          status={status}
          refreshStatus={refreshStatus}
          refreshWorkspace={refreshWorkspace}
          uploadState={uploadState}
          setUploadState={setUploadState}
        />
        <ChatPanel hasDocuments={documents.length > 0} />
      </div>
    </div>
  );
}
