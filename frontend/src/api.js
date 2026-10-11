/**
 * API client module for The Lenny Growth Assistant.
 * Uses relative paths so Vite development proxy routes seamlessly to FastAPI.
 */

const API_BASE = import.meta.env.VITE_API_URL || '';

export async function checkHealth() {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error(`Health check failed: ${res.status}`);
  return res.json();
}

export async function checkReadiness() {
  const res = await fetch(`${API_BASE}/ready`);
  return res.json();
}

export async function fetchConfig() {
  const res = await fetch(`${API_BASE}/api/config`);
  if (!res.ok) throw new Error(`Failed to load config: ${res.status}`);
  return res.json();
}

export async function updateConfig(provider, model) {
  const res = await fetch(`${API_BASE}/api/config`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ provider, model }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Failed to update config' }));
    throw new Error(err.detail || 'Failed to update config');
  }
  return res.json();
}

export async function fetchSessions() {
  const res = await fetch(`${API_BASE}/api/sessions`);
  if (!res.ok) throw new Error(`Failed to fetch sessions: ${res.status}`);
  return res.json();
}

export async function createSession(title = 'New Chat', provider = null, model = null) {
  const res = await fetch(`${API_BASE}/api/sessions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title, provider, model }),
  });
  if (!res.ok) throw new Error(`Failed to create session: ${res.status}`);
  return res.json();
}

export async function deleteSession(sessionId) {
  const res = await fetch(`${API_BASE}/api/sessions/${sessionId}`, {
    method: 'DELETE',
  });
  if (!res.ok) throw new Error(`Failed to delete session: ${res.status}`);
  return res.json();
}

export async function fetchMessages(sessionId) {
  const res = await fetch(`${API_BASE}/api/sessions/${sessionId}/messages`);
  if (!res.ok) throw new Error(`Failed to fetch messages: ${res.status}`);
  return res.json();
}

export async function sendChatMessage(sessionId, content, routingHint = null, providerOverride = null) {
  let url = `${API_BASE}/api/sessions/${sessionId}/chat`;
  if (providerOverride) {
    url += `?provider_override=${encodeURIComponent(providerOverride)}`;
  }
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content, routing_hint: routingHint }),
  });
  if (!res.ok) {
    const errorBody = await res.json().catch(() => ({ detail: 'Request failed' }));
    const message = typeof errorBody.detail === 'object' 
      ? errorBody.detail.message || JSON.stringify(errorBody.detail) 
      : errorBody.detail || errorBody.error || `HTTP ${res.status}`;
    throw new Error(message);
  }
  return res.json();
}

export async function fetchSessionArtifacts(sessionId) {
  const res = await fetch(`${API_BASE}/api/sessions/${sessionId}/artifacts`);
  if (!res.ok) return { artifacts: [] };
  return res.json();
}

export async function fetchKnowledgeStatus() {
  const res = await fetch(`${API_BASE}/api/knowledge/status`);
  if (!res.ok) return { total_sources: 0, total_chunks: 0, fts_ready: false };
  return res.json();
}
