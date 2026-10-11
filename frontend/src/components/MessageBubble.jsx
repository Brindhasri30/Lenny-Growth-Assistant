import React, { useState } from 'react';

export default function MessageBubble({ message, onOpenArtifact }) {
  const isUser = message.role === 'user';
  const citations = message.citations || [];
  const [showCitations, setShowCitations] = useState(true);

  // Check if message generated an artifact or essay
  const hasArtifact = message.routing_type === 'essay' || 
                      message.routing_type === 'artifact' || 
                      message.content.includes('```html') ||
                      (message.content.length > 600 && message.content.includes('## '));

  return (
    <div className={`message-row ${isUser ? 'user' : 'assistant'}`}>
      <div className={`avatar ${isUser ? 'avatar-user' : 'avatar-assistant'}`}>
        {isUser ? 'U' : 'L'}
      </div>

      <div className="message-body">
        <div className="bubble">
          {message.content}

          {/* Artifact shortcut button */}
          {!isUser && hasArtifact && onOpenArtifact && (
            <div style={{ marginTop: '12px' }}>
              <button
                className="action-pill active"
                onClick={() => onOpenArtifact({
                  title: `${message.routing_type === 'essay' ? 'Ship 30 Essay' : 'Artifact'}: ${message.content.slice(0, 30)}...`,
                  artifact_type: message.content.includes('```html') ? 'html' : 'markdown',
                  content: message.content,
                })}
              >
                📄 Open in Artifact Viewer
              </button>
            </div>
          )}
        </div>

        {/* Citations Box for grounded answers */}
        {!isUser && citations.length > 0 && (
          <div className="citations-box">
            <div
              className="citations-header"
              onClick={() => setShowCitations(!showCitations)}
              style={{ cursor: 'pointer', userSelect: 'none' }}
            >
              <span>📚 {citations.length} Grounded Transcript Citation{citations.length > 1 ? 's' : ''}</span>
              <span style={{ fontSize: '10px', marginLeft: 'auto' }}>
                {showCitations ? '▲ Hide' : '▼ View'}
              </span>
            </div>

            {showCitations && (
              <div className="citations-list">
                {citations.map((c, idx) => (
                  <div key={idx} className="citation-item">
                    <div className="citation-title">
                      <span>{c.title || 'Transcript Source'} (Chunk #{c.chunk_index})</span>
                      {c.source_url && (
                        <a
                          href={c.source_url}
                          target="_blank"
                          rel="noreferrer"
                          style={{ color: 'var(--accent-primary)', fontSize: '11px', textDecoration: 'none' }}
                        >
                          Link ↗
                        </a>
                      )}
                    </div>
                    {c.excerpt && <p className="citation-excerpt">"{c.excerpt}"</p>}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        <div className="message-meta">
          <span>{new Date(message.created_at || Date.now()).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
          {!isUser && message.provider && (
            <span>• {message.provider} ({message.model || 'default'})</span>
          )}
        </div>
      </div>
    </div>
  );
}
