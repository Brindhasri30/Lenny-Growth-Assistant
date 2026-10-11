"""
Unit tests for SQLAlchemy models and database operations.
Uses an isolated in-memory SQLite database.
"""
import unittest
import uuid

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.database import (
    AppConfig,
    Artifact,
    Base,
    ChatSession,
    Message,
    TranscriptChunk,
    TranscriptSource,
    init_db,
)


class TestDatabaseModels(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create an in-memory SQLite engine for testing
        cls.engine = create_engine("sqlite:///:memory:", echo=False)
        init_db(cls.engine)
        cls.Session = sessionmaker(bind=cls.engine)

    def setUp(self):
        self.session = self.Session()

    def tearDown(self):
        self.session.rollback()
        self.session.close()

    def test_create_chat_session(self):
        chat = ChatSession(title="Growth Strategy Chat", provider="ollama", model="llama3.2:3b")
        self.session.add(chat)
        self.session.commit()

        self.assertIsNotNone(chat.id)
        self.assertEqual(chat.title, "Growth Strategy Chat")
        self.assertTrue(chat.is_active)

    def test_message_relationship_and_cascade(self):
        chat = ChatSession(title="Cascade Test")
        self.session.add(chat)
        self.session.commit()

        msg1 = Message(session_id=chat.id, role="user", content="How do I find PMF?")
        msg2 = Message(session_id=chat.id, role="assistant", content="Focus on retention first.")
        self.session.add_all([msg1, msg2])
        self.session.commit()

        # Verify messages belong to session
        retrieved_chat = self.session.scalar(select(ChatSession).where(ChatSession.id == chat.id))
        self.assertEqual(len(retrieved_chat.messages), 2)
        self.assertEqual(retrieved_chat.messages[0].content, "How do I find PMF?")

        # Test cascade delete
        self.session.delete(retrieved_chat)
        self.session.commit()

        remaining_msgs = self.session.scalars(select(Message).where(Message.session_id == chat.id)).all()
        self.assertEqual(len(remaining_msgs), 0)

    def test_transcript_source_and_chunks(self):
        source = TranscriptSource(
            title="Lenny's Podcast — Elena Verna on Growth",
            source_url="https://lennyspodcast.com/elena-verna",
            source_type="podcast",
            episode_number="42",
        )
        self.session.add(source)
        self.session.commit()

        chunk1 = TranscriptChunk(
            source_id=source.id,
            chunk_index=0,
            content="B2B growth is fundamentally about product-led flywheels...",
        )
        chunk2 = TranscriptChunk(
            source_id=source.id,
            chunk_index=1,
            content="When you look at freemium versus free trial...",
        )
        self.session.add_all([chunk1, chunk2])
        self.session.commit()

        retrieved_source = self.session.scalar(select(TranscriptSource).where(TranscriptSource.id == source.id))
        self.assertEqual(len(retrieved_source.chunks), 2)
        self.assertEqual(retrieved_source.chunks[0].chunk_index, 0)

    def test_app_config(self):
        cfg = AppConfig(key="active_provider", value="ollama")
        self.session.add(cfg)
        self.session.commit()

        retrieved = self.session.scalar(select(AppConfig).where(AppConfig.key == "active_provider"))
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.value, "ollama")


if __name__ == "__main__":
    unittest.main()
