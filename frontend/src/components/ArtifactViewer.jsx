import React, { useState } from 'react';

export default function ArtifactViewer({ artifact, onClose }) {
  if (!artifact) return null;

  const [copied, setCopied] = useState(false);

  // Extract HTML if contained within markdown codeblock
  const isHtml = artifact.artifact_type === 'html' || artifact.content.includes('```html');
  let htmlContent = '';
  if (isHtml) {
    const match = artifact.content.match(/```html([\s\S]*?)```/);
    htmlContent = match ? match[1].trim() : artifact.content;
  }

  const handleCopy = () => {
    navigator.clipboard.writeText(artifact.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const ext = isHtml ? 'html' : 'md';
    const blob = new Blob([isHtml ? htmlContent : artifact.content], {
      type: isHtml ? 'text/html' : 'text/markdown',
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${artifact.title.replace(/[^a-z0-9]/gi, '_').toLowerCase()}.${ext}`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <aside className="artifact-viewer" aria-label="Artifact Preview Panel">
      <div className="artifact-header">
        <h3 className="artifact-title" title={artifact.title}>
          {artifact.title || 'Generated Artifact'}
        </h3>
        <div className="artifact-actions">
          <button className="btn-icon" onClick={handleCopy} title="Copy to clipboard">
            {copied ? '✓ Copied' : 'Copy'}
          </button>
          <button className="btn-icon" onClick={handleDownload} title="Download file">
            Download
          </button>
          <button className="btn-icon" onClick={onClose} title="Close Artifact Viewer">
            ✕
          </button>
        </div>
      </div>

      <div className="artifact-body">
        {isHtml ? (
          <iframe
            title="Safe HTML Sandboxed Artifact"
            className="artifact-iframe"
            sandbox="allow-scripts"
            srcDoc={htmlContent}
          />
        ) : (
          <div className="artifact-markdown">{artifact.content}</div>
        )}
      </div>
    </aside>
  );
}
