from app.ai.config import ai_settings


def test_ai_settings_defaults():
    assert hasattr(ai_settings, "enabled")
    assert hasattr(ai_settings, "ollama_base_url")
    assert hasattr(ai_settings, "ollama_model")
    assert hasattr(ai_settings, "embedding_provider")
    assert hasattr(ai_settings, "embedding_model")
    assert hasattr(ai_settings, "vector_store")
    assert hasattr(ai_settings, "qdrant_url")
    assert hasattr(ai_settings, "qdrant_collection")
    assert hasattr(ai_settings, "retrieval_score_threshold")
