"""RAG Knowledge Base — lets agents search books, filings, and trade history."""

import os
import chromadb
from chromadb.config import Settings

# Persistent vector DB stored in data/knowledge_base/
CHROMA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "knowledge_base")


def get_db():
    """Get or create the ChromaDB client."""
    return chromadb.PersistentClient(path=CHROMA_PATH)


def get_or_create_collection(name: str):
    """Get or create a named collection (e.g., 'books', 'filings', 'trade_journal')."""
    db = get_db()
    return db.get_or_create_collection(name=name)


def add_documents(collection_name: str, texts: list[str], metadatas: list[dict] = None,
                  ids: list[str] = None):
    """Add text chunks to a collection for RAG retrieval."""
    collection = get_or_create_collection(collection_name)
    if ids is None:
        ids = [f"{collection_name}_{i}" for i in range(len(texts))]
    collection.add(documents=texts, metadatas=metadatas, ids=ids)


def search(collection_name: str, query: str, n_results: int = 5) -> list[dict]:
    """Search the knowledge base — returns most relevant chunks."""
    collection = get_or_create_collection(collection_name)
    results = collection.query(query_texts=[query], n_results=n_results)
    return [
        {"text": doc, "metadata": meta}
        for doc, meta in zip(results["documents"][0], results["metadatas"][0])
    ]


def log_trade(trade_data: dict):
    """Log a completed trade to the trade journal collection for learning."""
    collection = get_or_create_collection("trade_journal")
    trade_id = f"trade_{trade_data.get('symbol', 'UNK')}_{trade_data.get('timestamp', '0')}"
    text = (
        f"Trade: {trade_data.get('side', '').upper()} {trade_data.get('symbol')} "
        f"at ${trade_data.get('price', 0):.2f}. "
        f"Reason: {trade_data.get('reason', 'N/A')}. "
        f"Agents agreed: {trade_data.get('agents_agreed', [])}. "
        f"Outcome: {trade_data.get('outcome', 'pending')}. "
        f"P/L: {trade_data.get('pnl', 0):.2f}. "
        f"Lesson: {trade_data.get('lesson', 'N/A')}"
    )
    collection.add(documents=[text], metadatas=[trade_data], ids=[trade_id])


def ingest_book(file_path: str, chunk_size: int = 1000):
    """Ingest a text file (book) into the 'books' collection, chunked for RAG."""
    with open(file_path, "r") as f:
        text = f.read()

    # Simple chunking by characters with overlap
    chunks = []
    for i in range(0, len(text), chunk_size - 200):
        chunk = text[i:i + chunk_size]
        if chunk.strip():
            chunks.append(chunk)

    book_name = os.path.basename(file_path).replace(".txt", "")
    ids = [f"book_{book_name}_{i}" for i in range(len(chunks))]
    metadatas = [{"source": book_name, "chunk": i} for i in range(len(chunks))]

    add_documents("books", chunks, metadatas, ids)
    return f"Ingested {len(chunks)} chunks from {book_name}"
