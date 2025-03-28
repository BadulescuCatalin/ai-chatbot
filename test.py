from qdrant_api import insert_text_chunks, query_similar_texts

# Insert text
doc_id = "doc1"
chunks = [
    "Qdrant is a vector database.",
    "A vector database is used for semantic search.",
    "Embeddings help find similar texts."
]
inserted = insert_text_chunks(doc_id, chunks)
print(f"Inserted {inserted} chunks.")

# Query text
results = query_similar_texts("What is a vector database?", threshold=0.5)
for r in results:
    print(f"> {r['text']} (score: {r['score']:.2f})")