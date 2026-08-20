import pytest
from app.retrieval.hybrid import HybridStore
from app.chunking.router import chunk_document
from app.harness.pipeline import VoiceRAGPipeline
from app.stt.sarvam import normalize_language_code
from scripts.ingest import _as_text_list, _usable_answer
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

@pytest.mark.asyncio
async def test_greeting_returns_question_guidance(pipeline):
    r=await pipeline.run_text('Hey model')
    assert r.status == 'answered'
    assert r.reason == 'assistant_help'
    assert 'Try asking' in r.answer

def test_sarvam_language_normalization():
    assert normalize_language_code('hi-IN') == 'hi-IN'
    assert normalize_language_code('unsupported') == 'unknown'

def test_ingest_normalizes_array_like_passages():
    class ArrayLike:
        def tolist(self): return ['first passage', 'second passage']
    assert _as_text_list(ArrayLike()) == ['first passage', 'second passage']
    assert _usable_answer('कोई उत्तर नहीं मिला।') == ''

def test_exact_source_question_is_prioritized():
    store=HybridStore('unused-index.json')
    store.add(chunk_document('wrong','A shareholder can own stock in a corporation.','test',{'english_query':'How do shareholders vote?'}))
    store.add(chunk_document('right','A corporation is a legal entity formed by a group of people.','test',{'english_query':'. What is a corporation?'}))
    assert store.search('What is a corporation?',1)[0]['document_id'] == 'right'
