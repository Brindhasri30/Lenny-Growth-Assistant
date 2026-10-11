"""
Unit tests for configuration loading and validation.
"""
import unittest

from app.config import Settings, get_settings


class TestConfig(unittest.TestCase):
    def test_default_settings(self):
        settings = Settings()
        self.assertEqual(settings.app_name, "Lenny Growth Assistant")
        self.assertEqual(settings.app_version, "1.0.0")
        self.assertEqual(settings.active_provider, "ollama")
        self.assertEqual(settings.active_model, "llama3.2:3b")
        self.assertIn("postgresql", settings.database_url)

    def test_cors_origins_list(self):
        settings = Settings(cors_origins="http://localhost:5173,http://localhost:3000")
        origins = settings.cors_origins_list
        self.assertIn("http://localhost:5173", origins)
        self.assertIn("http://localhost:3000", origins)

    def test_provider_availability_flags(self):
        settings_no_keys = Settings(anthropic_api_key=None, openai_api_key=None)
        self.assertFalse(settings_no_keys.is_anthropic_available)
        self.assertFalse(settings_no_keys.is_openai_available)

        settings_with_keys = Settings(
            anthropic_api_key="sk-ant-test-12345",
            openai_api_key="sk-proj-test-12345",
        )
        self.assertTrue(settings_with_keys.is_anthropic_available)
        self.assertTrue(settings_with_keys.is_openai_available)


if __name__ == "__main__":
    unittest.main()
