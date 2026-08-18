from app.chunking.router import chunk_document, sliding_chunks
def test_sliding_has_overlap():
    pieces=sliding_chunks(" ".join(f"w{i}" for i in range(180)),100,20)
    assert "w80" in pieces[0] and "w80" in pieces[1]
def test_metadata_strategy():
    chunks=chunk_document("d","Sentence one. Sentence two.","source",{"language":"en"})
    assert chunks[0].metadata["chunk_strategy"] == "semantic" and chunks[0].metadata["language"] == "en"
