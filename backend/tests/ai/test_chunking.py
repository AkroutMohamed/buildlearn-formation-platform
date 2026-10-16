from app.ai.chunking.chunker import BaseChunker


def test_chunker_is_abstract():
    assert hasattr(BaseChunker, "chunk")
