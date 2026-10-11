import React, { useEffect, useRef, useState } from 'react';
import {
  checkReadiness,
  createSession,
  deleteSession,
  fetchConfig,
  fetchMessages,
  fetchSessionArtifacts,
  fetchSessions,
  sendChatMessage,
  updateConfig,
} from './api';
import ArtifactViewer from './components/ArtifactViewer';
import MessageBubble from './components/MessageBubble';

export default function App() {
  const [sessions, setSessions] = useState([]);
  const [activeSessionId, setActiveSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputContent, setInputContent] = useState('');
  const [activeRouteHint, setActiveRouteHint] = useState(null);
  const [loading, setLoading] = useState(false);
  const [errorBanner, setErrorBanner] = useState(null);

  // System & Model Status
  const [config, setConfig] = useState(null);
  const [readyStatus, setReadyStatus] = useState(null);
  const [activeArtifact, setActiveArtifact] = useState(null);

  const messagesEndRef = useRef(null);

  // Load initial environment state and sessions
  useEffect(() => {
    loadInitialData();
  }, []);

  async function loadInitialData() {
    try {
      // 1. Fetch system readiness
      const ready = await checkReadiness().catch(() => ({ status: 'not_ready' }));
      setReadyStatus(ready);

      // 2. Fetch active provider configuration
      const cfg = await fetchConfig().catch(() => null);
      if (cfg) setConfig(cfg);

      // 3. Fetch persistent sessions
      const res = await fetchSessions().catch(() => ({ sessions: [] }));
      setSessions(res.sessions || []);

      if (res.sessions && res.sessions.length > 0) {
        selectSession(res.sessions[0].id);
      } else {
        // Automatically create a starting session if none exist
        handleNewChat();
      }
    } catch (err) {
      console.error('Failed initialization:', err);
    }
  }

  async function selectSession(sessionId) {
    setActiveSessionId(sessionId);
    setErrorBanner(null);
    try {
      const msgRes = await fetchMessages(sessionId);
      setMessages(msgRes.messages || []);

      // Check for session artifacts
      const artRes = await fetchSessionArtifacts(sessionId);
      if (artRes.artifacts && artRes.artifacts.length > 0) {
        setActiveArtifact(artRes.artifacts[0]);
      } else {
        setActiveArtifact(null);
      }
    } catch (err) {
      setErrorBanner(`Failed to load conversation: ${err.message}`);
    }
  }

  async function handleNewChat() {
    try {
      const newSession = await createSession('New Chat');
      setSessions((prev) => [newSession, ...prev]);
      setActiveSessionId(newSession.id);
      setMessages([]);
      setActiveArtifact(null);
      setErrorBanner(null);
    } catch (err) {
      setErrorBanner(`Could not create session: ${err.message}`);
    }
  }

  async function handleDeleteSession(e, sessionId) {
    e.stopPropagation();
    if (!window.confirm('Delete this conversation?')) return;
    try {
      await deleteSession(sessionId);
      const remaining = sessions.filter((s) => s.id !== sessionId);
      setSessions(remaining);
      if (activeSessionId === sessionId) {
        if (remaining.length > 0) {
          selectSession(remaining[0].id);
        } else {
          handleNewChat();
        }
      }
    } catch (err) {
      setErrorBanner(`Could not delete session: ${err.message}`);
    }
  }

  async function handleProviderChange(e) {
    const newProvider = e.target.value;
    try {
      const updated = await updateConfig(newProvider);
      setConfig(updated);
      setErrorBanner(null);
    } catch (err) {
      setErrorBanner(err.message);
    }
  }

  async function handleSendMessage(e) {
    e?.preventDefault();
    if (!inputContent.trim() || loading || !activeSessionId) return;

    const userText = inputContent.trim();
    const hint = activeRouteHint;

    // Reset input
    setInputContent('');
    setActiveRouteHint(null);
    setLoading(true);
    setErrorBanner(null);

    // Optimistically render user message
    const tempUserMsg = {
      id: 'temp-' + Date.now(),
      role: 'user',
      content: userText,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, tempUserMsg]);

    try {
      const assistantMsg = await sendChatMessage(
        activeSessionId,
        userText,
        hint,
        config?.active_provider
      );

      // Replace and append real assistant message
      setMessages((prev) => [...prev, assistantMsg]);

      // If assistant produced an artifact or essay, open the viewer automatically
      if (
        assistantMsg.routing_type === 'essay' ||
        assistantMsg.routing_type === 'artifact' ||
        assistantMsg.content.includes('```html')
      ) {
        setActiveArtifact({
          title: `${assistantMsg.routing_type === 'essay' ? 'Ship 30 Essay' : 'Artifact'}: ${userText.slice(0, 32)}...`,
          artifact_type: assistantMsg.content.includes('```html') ? 'html' : 'markdown',
          content: assistantMsg.content,
        });
      }

      // Refresh session list to update titles
      const refreshedSessions = await fetchSessions();
      setSessions(refreshedSessions.sessions || []);
    } catch (err) {
      setErrorBanner(`AI generation error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  }

  // Auto-scroll to bottom of messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  return (
    <div className="app-container">
      {/* ── Sidebar ── */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <div className="brand">
            <div className="brand-icon">L</div>
            <span>Lenny Assistant</span>
          </div>
        </div>

        <button className="btn-new-chat" onClick={handleNewChat}>
          <span>+</span>
          <span>New Chat</span>
        </button>

        <ul className="session-list" aria-label="Conversation History">
          {sessions.map((s) => (
            <li
              key={s.id}
              className={`session-item ${s.id === activeSessionId ? 'active' : ''}`}
              onClick={() => selectSession(s.id)}
            >
              <span className="session-title">{s.title || 'Conversation'}</span>
              <button
                className="btn-delete-session"
                onClick={(e) => handleDeleteSession(e, s.id)}
                title="Delete chat"
              >
                ✕
              </button>
            </li>
          ))}
        </ul>

        {/* Provider & Model Selector */}
        <div className="sidebar-footer">
          <div className="provider-box">
            <label className="provider-label" htmlFor="provider-select">
              Active Provider
            </label>
            <select
              id="provider-select"
              className="provider-select"
              value={config?.active_provider || 'ollama'}
              onChange={handleProviderChange}
            >
              <option value="ollama">Ollama (llama3.2:3b)</option>
              {config?.available_providers?.includes('anthropic') && (
                <option value="anthropic">Anthropic Claude</option>
              )}
              {config?.available_providers?.includes('openai') && (
                <option value="openai">OpenAI GPT-4o-mini</option>
              )}
            </select>
          </div>
        </div>
      </aside>

      {/* ── Main Chat Panel ── */}
      <main className="main-content">
        <div className="chat-panel">
          <header className="chat-header">
            <h2 className="chat-header-title">
              {sessions.find((s) => s.id === activeSessionId)?.title || 'Grounded Growth Chat'}
            </h2>
            <div className="header-badges">
              {readyStatus?.status === 'ready' ? (
                <span className="badge badge-ready">System Ready</span>
              ) : (
                <span className="badge badge-degraded">
                  {readyStatus?.database === 'connected' ? 'DB Connected' : 'Local Mode'}
                </span>
              )}
            </div>
          </header>

          {/* Error Banner */}
          {errorBanner && (
            <div
              style={{
                backgroundColor: 'rgba(239, 68, 68, 0.15)',
                borderBottom: '1px solid rgba(239, 68, 68, 0.3)',
                color: '#fca5a5',
                padding: '10px 24px',
                fontSize: '13px',
                display: 'flex',
                justifyContent: 'space-between',
              }}
            >
              <span>{errorBanner}</span>
              <button
                onClick={() => setErrorBanner(null)}
                style={{ background: 'none', border: 'none', color: '#fca5a5', cursor: 'pointer' }}
              >
                ✕
              </button>
            </div>
          )}

          {/* Messages Area */}
          <div className="messages-container">
            {messages.length === 0 ? (
              <div className="empty-state">
                <div className="empty-icon">🎙️</div>
                <h3 className="empty-title">The Lenny Growth Assistant</h3>
                <p className="empty-subtitle">
                  Ask tactical questions about Product-Led Growth, Founder Mode, or product strategy.
                  All responses are grounded directly in real podcast transcripts.
                </p>
                <div className="prompt-suggestions">
                  <button
                    className="suggestion-btn"
                    onClick={() => {
                      setInputContent("What does Elena Verna recommend about PLG and fixing retention before acquisition?");
                      setActiveRouteHint(null);
                    }}
                  >
                    💬 "What does Elena Verna recommend about fixing retention before acquisition?"
                  </button>
                  <button
                    className="suggestion-btn"
                    onClick={() => {
                      setInputContent("Write an essay on why Brian Chesky eliminated traditional product management at Airbnb");
                      setActiveRouteHint("essay");
                    }}
                  >
                    ✍️ "Write a Ship 30 essay on Brian Chesky and Founder Mode at Airbnb"
                  </button>
                  <button
                    className="suggestion-btn"
                    onClick={() => {
                      setInputContent("Explain Shreyas Doshi's LNO framework and how to apply it to PM tasks");
                      setActiveRouteHint(null);
                    }}
                  >
                    🚀 "Explain Shreyas Doshi's LNO framework for PM prioritization"
                  </button>
                </div>
              </div>
            ) : (
              messages.map((m) => (
                <MessageBubble
                  key={m.id}
                  message={m}
                  onOpenArtifact={(art) => setActiveArtifact(art)}
                />
              ))
            )}

            {/* Loading Indicator */}
            {loading && (
              <div className="message-row assistant">
                <div className="avatar avatar-assistant">L</div>
                <div className="typing-indicator">
                  <div className="dot"></div>
                  <div className="dot"></div>
                  <div className="dot"></div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Composer Area */}
          <footer className="composer-area">
            <div className="composer-toolbar">
              <button
                type="button"
                className={`action-pill ${activeRouteHint === 'essay' ? 'active' : ''}`}
                onClick={() => setActiveRouteHint(activeRouteHint === 'essay' ? null : 'essay')}
                title="Format response as ~1,250-word Ship 30 for 30 atomic essay"
              >
                ✍️ Ship 30 Essay Skill {activeRouteHint === 'essay' ? '✓' : ''}
              </button>
              <button
                type="button"
                className={`action-pill ${activeRouteHint === 'artifact' ? 'active' : ''}`}
                onClick={() => setActiveRouteHint(activeRouteHint === 'artifact' ? null : 'artifact')}
                title="Generate standalone Markdown or HTML artifact"
              >
                📄 Generate Artifact {activeRouteHint === 'artifact' ? '✓' : ''}
              </button>
            </div>

            <form className="composer-form" onSubmit={handleSendMessage}>
              <textarea
                className="composer-input"
                rows={1}
                placeholder="Ask a question about growth, PLG, or write an essay..."
                value={inputContent}
                onChange={(e) => setInputContent(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSendMessage();
                  }
                }}
              />
              <button
                type="submit"
                className="btn-send"
                disabled={loading || !inputContent.trim()}
                title="Send message"
              >
                ➔
              </button>
            </form>
          </footer>
        </div>

        {/* ── Side-by-Side Artifact Viewer (Desktop & Responsive) ── */}
        <ArtifactViewer
          artifact={activeArtifact}
          onClose={() => setActiveArtifact(null)}
        />
      </main>
    </div>
  );
}
