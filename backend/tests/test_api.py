"""
Integration tests for FastAPI endpoints using TestClient.
Uses an in-memory SQLite database to isolate tests.
"""
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db, init_db
from app.providers import BaseProvider
from main import app


class MockProvider(BaseProvider):
    name = "mock"

    def is_available(self) -> bool:
        return True

    def generate(self, messages, system=None) -> str:
        # Return a simulated grounded response with Ship 30 structure
        return (
            "# The PLG Retention Engine\n\n"
            "## 1. Why Acquisition Fails Without Retention\n"
            "As Elena Verna highlighted in Lenny's Podcast, scaling acquisition before fixing retention "
            "is like pouring water into a leaky bucket.\n\n"
            "## 2. Key Actionable Steps\n"
            "- Step 1: Track month-3 retention curves until they flatten.\n"
            "- Step 2: Define Product Qualified Leads (PQLs).\n"
            "- Step 3: Align sales with user aha moments."
        )


class TestAPIEndpoints(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create an in-memory SQLite engine that persists across the test session
        cls.engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        init_db(cls.engine)
        cls.TestingSessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=cls.engine
        )

        def override_get_db():
            db = cls.TestingSessionLocal()
            try:
                yield db
            finally:
                db.close()

        app.dependency_overrides[get_db] = override_get_db
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        app.dependency_overrides.clear()

    def test_root_endpoint(self):
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["app"], "Lenny Growth Assistant")
        self.assertEqual(data["status"], "online")

    def test_health_endpoint(self):
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["version"], "1.0.0")

    def test_ready_endpoint(self):
        resp = self.client.get("/ready")
        self.assertIn(resp.status_code, [200, 503])
        data = resp.json()
        self.assertIn("status", data)
        self.assertIn("database", data)
        self.assertIn("ollama", data)
        self.assertIn("knowledge_base", data)

    def test_get_config(self):
        resp = self.client.get("/api/config")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("active_provider", data)
        self.assertIn("available_providers", data)
        self.assertIn("ollama", data["available_providers"])

    def test_update_config_invalid_provider(self):
        resp = self.client.put("/api/config", json={"provider": "invalid_provider"})
        self.assertEqual(resp.status_code, 422)  # Pydantic regex validation rejection

    def test_create_and_list_sessions(self):
        # Create a session
        create_resp = self.client.post("/api/sessions", json={"title": "Test Chat"})
        self.assertEqual(create_resp.status_code, 201)
        session_data = create_resp.json()
        session_id = session_data["id"]
        self.assertEqual(session_data["title"], "Test Chat")
        self.assertEqual(session_data["message_count"], 0)

        # Retrieve session by ID
        get_resp = self.client.get(f"/api/sessions/{session_id}")
        self.assertEqual(get_resp.status_code, 200)
        self.assertEqual(get_resp.json()["id"], session_id)

        # List sessions
        list_resp = self.client.get("/api/sessions")
        self.assertEqual(list_resp.status_code, 200)
        sessions = list_resp.json()["sessions"]
        self.assertTrue(any(s["id"] == session_id for s in sessions))

    def test_session_messages(self):
        # Create session
        create_resp = self.client.post("/api/sessions", json={"title": "Message Test"})
        session_id = create_resp.json()["id"]

        # Post a message
        msg_resp = self.client.post(
            f"/api/sessions/{session_id}/messages",
            json={"content": "What is the North Star Metric for marketplaces?"},
        )
        self.assertEqual(msg_resp.status_code, 201)
        msg_data = msg_resp.json()
        self.assertEqual(msg_data["content"], "What is the North Star Metric for marketplaces?")
        self.assertEqual(msg_data["role"], "user")

        # Get messages
        msgs_resp = self.client.get(f"/api/sessions/{session_id}/messages")
        self.assertEqual(msgs_resp.status_code, 200)
        self.assertEqual(msgs_resp.json()["total"], 1)

    def test_knowledge_ingest_and_search(self):
        # Ingest sample Elena Verna transcript
        transcript_path = Path("transcripts/elena_verna_growth.txt")
        if not transcript_path.exists():
            transcript_path = Path("../transcripts/elena_verna_growth.txt")

        ingest_resp = self.client.post(
            "/api/knowledge/ingest",
            json={
                "file_path": str(transcript_path.resolve()),
                "title": "Elena Verna on PLG Loops",
                "source_url": "https://lennyspodcast.com/elena-verna",
                "source_type": "podcast",
                "force_reingest": True,
            },
        )
        self.assertEqual(ingest_resp.status_code, 201)
        data = ingest_resp.json()
        self.assertGreater(data["chunks_created"], 0)

        # Search knowledge base
        search_resp = self.client.get("/api/knowledge/search?q=retention")
        self.assertEqual(search_resp.status_code, 200)
        search_data = search_resp.json()
        self.assertGreater(search_data["count"], 0)
        self.assertIn("Elena Verna", search_data["results"][0]["source_title"])

    def test_ai_chat_flow_with_grounding_and_essay(self):
        # Create a session
        create_resp = self.client.post("/api/sessions", json={"title": "AI Grounding Test"})
        session_id = create_resp.json()["id"]

        # Ingest transcript for grounding
        transcript_path = Path("transcripts/elena_verna_growth.txt")
        if not transcript_path.exists():
            transcript_path = Path("../transcripts/elena_verna_growth.txt")

        self.client.post(
            "/api/knowledge/ingest",
            json={
                "file_path": str(transcript_path.resolve()),
                "title": "Elena Verna on PLG Loops",
                "source_url": "https://lennyspodcast.com/elena-verna",
                "source_type": "podcast",
            },
        )

        # Execute chat message with mock provider to verify orchestration without external API call
        with patch("app.routers.sessions.get_provider", return_value=MockProvider()):
            chat_resp = self.client.post(
                f"/api/sessions/{session_id}/chat",
                json={
                    "content": "Write an essay about Elena Verna's advice on PLG and retention loops",
                    "routing_hint": "essay",
                },
            )
            self.assertEqual(chat_resp.status_code, 200)
            chat_data = chat_resp.json()
            self.assertEqual(chat_data["role"], "assistant")
            self.assertEqual(chat_data["routing_type"], "essay")
            self.assertIsNotNone(chat_data["citations"])
            self.assertGreater(len(chat_data["citations"]), 0)
            self.assertEqual(chat_data["citations"][0]["title"], "Elena Verna on PLG Loops")

        # Verify artifacts were generated and persisted for the essay
        artifact_resp = self.client.get(f"/api/sessions/{session_id}/artifacts")
        self.assertEqual(artifact_resp.status_code, 200)
        artifacts = artifact_resp.json()
        self.assertGreater(artifacts["total"], 0)
        self.assertEqual(artifacts["artifacts"][0]["artifact_type"], "markdown")

    def test_session_isolation(self):
        # Create session 1
        s1 = self.client.post("/api/sessions", json={"title": "Session 1"}).json()["id"]
        # Create session 2
        s2 = self.client.post("/api/sessions", json={"title": "Session 2"}).json()["id"]

        # Post message to session 1
        self.client.post(f"/api/sessions/{s1}/messages", json={"content": "Secret note in S1"})

        # Verify session 2 messages is completely empty
        s2_msgs = self.client.get(f"/api/sessions/{s2}/messages").json()
        self.assertEqual(s2_msgs["total"], 0)

        # Verify session 1 contains only its message
        s1_msgs = self.client.get(f"/api/sessions/{s1}/messages").json()
        self.assertEqual(s1_msgs["total"], 1)
        self.assertEqual(s1_msgs["messages"][0]["content"], "Secret note in S1")


if __name__ == "__main__":
    unittest.main()
