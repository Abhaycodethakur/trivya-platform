# VectorStore Guide

## Overview
The `VectorStore` module provides an abstraction layer for interacting with the vector database (ChromaDB). It serves as the long-term memory for the Trivya platform, allowing for the storage and semantic retrieval of documents.

## Class: `VectorStore`
Located in `shared/knowledge_base/vector_store.py`.

### Initialization
```python
from shared.core_functions.config import Config
from shared.knowledge_base.vector_store import VectorStore

config = Config()
vector_store = VectorStore(config)
```

### Methods

#### `add_documents(documents: List[Dict[str, Any]]) -> List[str]`
Adds a list of documents to the vector store.
- **documents**: A list of dictionaries. Each dictionary must contain:
    - `content` (str): The text content of the document.
    - `metadata` (dict): Arbitrary metadata associated with the document.
- **Returns**: A list of generated IDs for the added documents.

#### `similarity_search(query: str, n_results: int = 5) -> List[Dict[str, Any]]`
Performs a semantic search against the stored documents.
- **query**: The search query string.
- **n_results**: The number of results to return (default: 5).
- **Returns**: A list of matching documents, including their content, metadata, and ID.

#### `delete_collection()`
Deletes the entire collection. Use with caution!

## Configuration
The `VectorStore` is configured via `shared/core_functions/config.py` and environment variables:
- `VECTOR_DB_TYPE`: Type of vector DB (default: "chromadb")
- `VECTOR_DB_PATH`: Path to store the database (default: "./data/chroma")
- `COLLECTION_NAME`: Name of the collection (default: "trivya_kb")

## Example Usage

```python
from shared.core_functions.config import Config
from shared.knowledge_base.vector_store import VectorStore

# Initialize
config = Config()
vs = VectorStore(config)

# Add documents
docs = [
    {"content": "Trivya is a luxury AI platform.", "metadata": {"category": "product"}},
    {"content": "The platform uses advanced RAG.", "metadata": {"category": "tech"}}
]
ids = vs.add_documents(docs)
print(f"Added documents with IDs: {ids}")

# Search
results = vs.similarity_search("What is Trivya?")
for res in results:
    print(f"Found: {res['content']} (Metadata: {res['metadata']})")
```
