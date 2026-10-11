"""
CLI script to ingest transcripts into PostgreSQL knowledge base.
Run from backend/ directory:
    python -m app.ingest "path/to/transcript.txt" --title "Episode Title" --url "https://..."
"""
import argparse
import sys
from pathlib import Path

from app.database import get_session_factory
from app.logging_config import get_logger
from app.retrieval import ingest_file

logger = get_logger("ingest_cli")


def main():
    parser = argparse.ArgumentParser(description="Ingest podcast transcript files into Lenny Knowledge Base.")
    parser.add_argument("file_path", help="Path to transcript file (.txt, .md, .json, .html)")
    parser.add_argument("--title", required=True, help="Title of the episode or source")
    parser.add_argument("--url", default=None, help="Source URL (e.g. https://lennyspodcast.com/...)")
    parser.add_argument("--type", default="podcast", choices=["podcast", "newsletter", "other"], help="Source type")
    parser.add_argument("--episode", default=None, help="Episode number (optional)")
    parser.add_argument("--date", default=None, help="Published date (optional)")
    parser.add_argument("--force", action="store_true", help="Force re-ingestion if already exists")

    args = parser.parse_args()

    file_p = Path(args.file_path)
    if not file_p.is_file():
        print(f"[ERROR] File does not exist: {args.file_path}")
        return 1

    SessionLocal = get_session_factory()
    db = SessionLocal()
    try:
        print(f"Ingesting: {args.title} from {args.file_path}...")
        result = ingest_file(
            file_path_str=str(file_p),
            title=args.title,
            db=db,
            source_url=args.url,
            source_type=args.type,
            episode_number=args.episode,
            published_date=args.date,
            force_reingest=args.force,
        )
        print("[SUCCESS]")
        print(f"  Source ID:      {result['source_id']}")
        print(f"  Title:          {result['title']}")
        print(f"  Chunks Created: {result['chunks_created']}")
        print(f"  Status:         {result['message']}")
        return 0
    except Exception as e:
        print(f"[FAIL] Ingestion error: {e}")
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
