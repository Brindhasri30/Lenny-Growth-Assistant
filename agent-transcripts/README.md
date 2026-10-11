# Agent Transcripts — README

This folder contains the implementation log, demo script, and any supporting materials for the Lenny Growth Assistant project.

## Contents

| File | Description | Status |
|---|---|---|
| `implementation-log.md` | Honest record of decisions, failures, and corrections | Added in M12 |
| `demo-script.md` | 2–3 minute camera-on video demo script | Added in M12 |

## How to Add Transcript Files

Transcript files go in the project root's `transcripts/` directory (to be created in Milestone 5).

Supported formats: `.txt`, `.md`, `.json`, `.html`

**Do not add proprietary podcast transcripts without permission from Lenny's Podcast.**  
Use your own notes, publicly available summaries, or samples you have rights to use.

To ingest a transcript file once the backend is built (Milestone 5):

```bash
# Via CLI
backend\venv\Scripts\python.exe -m app.ingest "path\to\transcript.txt" --title "Episode Title" --url "https://example.com/episode"

# Via API
POST http://localhost:8000/api/knowledge/ingest
{
  "file_path": "path/to/transcript.txt",
  "title": "Episode Title",
  "source_url": "https://example.com/episode",
  "source_type": "podcast"
}
```
