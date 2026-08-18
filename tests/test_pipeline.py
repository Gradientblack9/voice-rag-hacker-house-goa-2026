import pytest
from app.retrieval.hybrid import HybridStore
from app.chunking.router import chunk_document
from app.harness.pipeline import VoiceRAGPipeline
@pytest.fixture
def pipeline():
    # The store remains in-memory for deterministic, filesystem-free tests.
    store=HybridStore('unused-index.json'); store.add(chunk_document('1','Python is a programming language used for data analysis.', 'test')); return VoiceRAGPipeline(store)
@pytest.mark.asyncio
async def test_grounded_answer(pipeline):
    r=await pipeline.run_text('What is Python used for?'); assert r.status=='answered' and r.grounded
@pytest.mark.asyncio
async def test_off_topic_rejected(pipeline):
    r=await pipeline.run_text('What is the weather?'); assert r.status=='rejected'

@pytest.mark.asyncio
async def test_weak_partial_match_abstains(pipeline):
    r=await pipeline.run_text('What is the capital of India?')
    assert r.status == 'abstained' and r.reason == 'insufficient_context'
