import { useRef, useState } from 'react';
import { AlertCircle, Bot, FileSearch, Loader2, MessageSquareText, Send, Sparkles, User } from 'lucide-react';
import { sendChat } from '../api/client';
import SourceList from './SourceList';

export default function ChatPanel({ hasDocuments }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const inputRef = useRef(null);

  async function handleSubmit(event) {
    event.preventDefault();
    const question = input.trim();
    if (!question || loading) return;

    const nextMessages = [...messages, { role: 'user', content: question }];
    setMessages(nextMessages);
    setInput('');
    setLoading(true);
    setError('');

    try {
      const history = messages.map(({ role, content }) => ({ role, content }));
      const response = await sendChat(question, history);
      setMessages([...nextMessages, { role: 'assistant', content: response.answer, sources: response.sources }]);
    } catch (err) {
      setError(err.message);
      setMessages(messages);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  }

  return (
    <main className="flex min-h-[60vh] flex-col bg-[#f7faf9] md:h-full md:min-h-0">
      <div className="shrink-0 border-b border-slate-200 bg-white px-5 py-4 sm:px-6">
        <div className="flex items-center justify-between gap-4">
          <div>
            <h2 className="text-lg font-semibold text-ink">Ask your documents</h2>
            <p className="mt-0.5 text-sm text-slate-500">Grounded answers with page-level citations.</p>
          </div>
          <div className="hidden items-center gap-2 rounded border border-emerald-100 bg-emerald-50 px-3 py-1.5 text-xs font-medium text-pine sm:flex">
            <Sparkles className="h-3.5 w-3.5" />
            RAG ready
          </div>
        </div>
      </div>

      <div className="min-h-0 flex-1 overflow-y-auto px-4 py-6 sm:px-6">
        <div className="mx-auto max-w-4xl space-y-5">
          {messages.length === 0 && (
            <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
              <div className="flex items-start gap-4">
                <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded bg-emerald-50 text-pine">
                  <FileSearch className="h-5 w-5" />
                </div>
                <div>
                  <p className="text-base font-semibold text-ink">Ready for document Q&A</p>
                  <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-600">
                    Ask for summaries, comparisons, clauses, risks, action items, or page-specific details from your indexed PDFs.
                  </p>
                  <div className="mt-4 flex flex-wrap gap-2">
                    {['Summarize the PDFs', 'Find key skills', 'Compare documents'].map((prompt) => (
                      <button
                        key={prompt}
                        type="button"
                        onClick={() => setInput(prompt)}
                        disabled={!hasDocuments}
                        className="rounded border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs font-medium text-slate-600 transition hover:border-pine hover:text-pine disabled:cursor-not-allowed disabled:opacity-50"
                      >
                        {prompt}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {messages.map((message, index) => (
            <div key={index} className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              {message.role === 'assistant' && <Avatar type="assistant" />}
              <div
                className={`max-w-3xl rounded-lg px-4 py-3 shadow-sm ${
                  message.role === 'user' ? 'bg-pine text-white' : 'border border-slate-200 bg-white text-ink'
                }`}
              >
                <p className="whitespace-pre-wrap text-sm leading-6">{message.content}</p>
                <SourceList sources={message.sources} />
              </div>
              {message.role === 'user' && <Avatar type="user" />}
            </div>
          ))}

          {loading && (
            <div className="flex items-center gap-3 rounded-lg border border-slate-200 bg-white p-4 text-sm text-slate-600 shadow-sm">
              <Loader2 className="h-4 w-4 animate-spin text-pine" />
              Searching documents and generating an answer...
            </div>
          )}

          {error && (
            <div className="flex gap-2 rounded-lg border border-red-100 bg-red-50 p-4 text-sm text-red-700">
              <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
              {error}
            </div>
          )}
        </div>
      </div>

      <form onSubmit={handleSubmit} className="sticky bottom-0 z-20 shrink-0 border-t border-slate-200 bg-white/95 p-4 shadow-[0_-10px_30px_rgba(23,33,38,0.08)] backdrop-blur">
        <div className="mx-auto flex max-w-4xl flex-col gap-3 sm:flex-row">
          <div className="relative min-w-0 flex-1">
            <MessageSquareText className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
            <input
              ref={inputRef}
              value={input}
              onChange={(event) => setInput(event.target.value)}
              disabled={!hasDocuments || loading}
              placeholder={hasDocuments ? 'Ask a question about your PDFs...' : 'Upload PDFs before chatting'}
              className="h-12 w-full rounded border border-slate-300 bg-white py-3 pl-10 pr-4 text-sm outline-none transition placeholder:text-slate-400 focus:border-pine focus:ring-2 focus:ring-emerald-100 disabled:bg-slate-100"
            />
          </div>
          <button
            type="submit"
            disabled={!hasDocuments || loading || !input.trim()}
            className="inline-flex h-12 shrink-0 items-center justify-center gap-2 rounded bg-pine px-6 text-sm font-semibold text-white transition hover:bg-emerald-800 disabled:cursor-not-allowed disabled:bg-slate-300"
            title="Ask question"
          >
            <Send className="h-4 w-4" />
            Ask
          </button>
        </div>
      </form>
    </main>
  );
}

function Avatar({ type }) {
  const Icon = type === 'assistant' ? Bot : User;
  return (
    <div className={`flex h-9 w-9 shrink-0 items-center justify-center rounded shadow-sm ${type === 'assistant' ? 'bg-white text-pine' : 'bg-slate-100 text-slate-600'}`}>
      <Icon className="h-4 w-4" />
    </div>
  );
}
