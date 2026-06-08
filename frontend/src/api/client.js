const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '');

function apiPath(path) {
  return `${API_BASE_URL}${path}`;
}

async function request(url, options) {
  try {
    const response = await fetch(url, options);
    return parseResponse(response);
  } catch (error) {
    if (error instanceof TypeError) {
      throw new Error('Cannot reach the backend API. Make sure FastAPI is running on http://localhost:8000.');
    }
    throw error;
  }
}

async function parseResponse(response) {
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(payload?.error?.message || 'Request failed');
  }
  return payload;
}

export async function getHealth() {
  return request(apiPath('/api/health'));
}

export async function listDocuments() {
  return request(apiPath('/api/documents'));
}

export async function uploadDocuments(files) {
  const body = new FormData();
  files.forEach((file) => body.append('files', file));
  return request(apiPath('/api/documents/upload'), {
    method: 'POST',
    body,
  });
}

export async function deleteDocument(documentId) {
  return request(apiPath(`/api/documents/${documentId}`), {
    method: 'DELETE',
  });
}

export async function sendChat(message, history, topK = 5) {
  return request(apiPath('/api/chat'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, history, top_k: topK }),
  });
}
