# RAG Pipeline Guide

## Overview
The RAG (Retrieval-Augmented Generation) Pipeline is a core component of the Trivya platform's knowledge base system. It enables AI agents to provide accurate, context-aware responses by retrieving relevant information from the vector store and assembling it into prompts for language models.

## Architecture

### Component Hierarchy
```
KnowledgeBaseManager (High-level orchestration)
    ├── RAGPipeline (Context retrieval & prompt generation)
    │   └── VectorStore (Document storage & similarity search)
    └── Logger (Logging & monitoring)
```

### Data Flow
1. **Document Ingestion**: Documents are validated and added to the vector store
2. **Query Processing**: User queries trigger similarity search in the vector store
3. **Context Retrieval**: Relevant documents are retrieved and filtered by similarity threshold
4. **Prompt Assembly**: Retrieved context is formatted into a structured prompt for the LLM
5. **Response Generation**: The LLM uses the assembled prompt to generate accurate responses

## Components

### 1. RAGPipeline Class
Located in `shared/knowledge_base/rag_pipeline.py`

#### Initialization
```python
from shared.core_functions.config import Config
from shared.knowledge_base.vector_store import VectorStore
from shared.knowledge_base.rag_pipeline import RAGPipeline

config = Config()
vector_store = VectorStore(config)
rag_pipeline = RAGPipeline(
    config=config,
    vector_store=vector_store,
    top_k=5,  # Number of documents to retrieve
    similarity_threshold=0.7  # Minimum similarity score (0.0-1.0)
)
```

#### Key Methods

**`retrieve_context(query, top_k=None, filter_threshold=True)`**
- Retrieves relevant documents from the vector store
- Filters results by similarity threshold
- Returns list of context documents with metadata

**`generate_prompt(query, context, system_instruction=None)`**
- Assembles a formatted prompt for the LLM
- Includes document content, metadata, and relevance scores
- Supports optional system instructions

**`query(user_query, top_k=None, system_instruction=None)`**
- End-to-end RAG query processing
- Returns both the assembled prompt and raw context
- Combines retrieval and prompt generation

### 2. KnowledgeBaseManager Class
Located in `shared/knowledge_base/kb_manager.py`

#### Initialization
```python
from shared.knowledge_base.kb_manager import KnowledgeBaseManager

kb_manager = KnowledgeBaseManager(
    config=config,
    vector_store=vector_store,
    rag_pipeline=rag_pipeline
)
```

#### Key Methods

**`ingest_documents(documents, validate=True)`**
- Validates and ingests multiple documents
- Tracks ingestion metrics
- Returns summary with success/failure counts

**`update_document(doc_id, new_content, metadata=None)`**
- Updates an existing document
- Maintains version history in metadata
- Returns success status

**`search(query, top_k=5, system_instruction=None)`**
- High-level search interface
- Wrapper around RAG pipeline query
- Adds business logic and access control

**`get_stats()`**
- Returns knowledge base statistics
- Includes document count, query metrics, and system health

**`health_check()`**
- Performs system health check
- Validates vector store and RAG pipeline status
- Returns health status and diagnostics

## Usage Examples

### Basic Document Ingestion and Search
```python
from shared.core_functions.config import Config
from shared.knowledge_base.vector_store import VectorStore
from shared.knowledge_base.rag_pipeline import RAGPipeline
from shared.knowledge_base.kb_manager import KnowledgeBaseManager

# Initialize components
config = Config()
vector_store = VectorStore(config)
rag_pipeline = RAGPipeline(config=config, vector_store=vector_store)
kb_manager = KnowledgeBaseManager(
    config=config,
    vector_store=vector_store,
    rag_pipeline=rag_pipeline
)

# Ingest documents
documents = [
    {
        "content": "Trivya is an AI-powered customer support platform.",
        "metadata": {"source": "about.txt", "category": "product"}
    },
    {
        "content": "Mini Trivya costs $1,000/month and handles 2 concurrent calls.",
        "metadata": {"source": "pricing.txt", "category": "pricing"}
    }
]

result = kb_manager.ingest_documents(documents)
print(f"Ingested {result['successful']} documents")

# Search the knowledge base
search_result = kb_manager.search("What is Trivya?", top_k=3)
print(f"Query: {search_result['query']}")
print(f"Found {search_result['context_count']} relevant documents")
print(f"Generated Prompt:\n{search_result['prompt']}")
```

### Advanced: Custom Similarity Threshold
```python
# Create RAG pipeline with higher quality threshold
rag_pipeline = RAGPipeline(
    config=config,
    vector_store=vector_store,
    top_k=10,
    similarity_threshold=0.8  # Only return highly relevant results
)

# Retrieve context with custom parameters
context = rag_pipeline.retrieve_context(
    query="How much does Trivya High cost?",
    top_k=5,
    filter_threshold=True
)

for doc in context:
    print(f"Content: {doc['content']}")
    print(f"Similarity: {doc.get('similarity_score', 'N/A')}")
    print(f"Source: {doc['metadata'].get('source', 'Unknown')}\n")
```

### System Monitoring
```python
# Get knowledge base statistics
stats = kb_manager.get_stats()
print(f"Total documents: {stats['total_documents']}")
print(f"Total queries: {stats['total_queries']}")
print(f"Vector store documents: {stats['vector_store']['document_count']}")

# Perform health check
health = kb_manager.health_check()
print(f"System status: {health['status']}")
print(f"Vector store: {'✓' if health['checks']['vector_store'] else '✗'}")
print(f"RAG pipeline: {'✓' if health['checks']['rag_pipeline'] else '✗'}")
```

## Configuration

### Environment Variables
Configure via `.env` file or environment:

```bash
# Vector Database Configuration
VECTOR_DB_TYPE=chromadb
VECTOR_DB_PATH=./data/chroma
COLLECTION_NAME=trivya_kb

# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### RAG Pipeline Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `top_k` | int | 5 | Number of documents to retrieve |
| `similarity_threshold` | float | 0.0 | Minimum similarity score (0.0-1.0) |

### Similarity Threshold Guidelines

- **0.0-0.3**: Very permissive, may include loosely related content
- **0.4-0.6**: Balanced, good for general queries
- **0.7-0.8**: Strict, only highly relevant content
- **0.9-1.0**: Very strict, only near-exact matches

## Best Practices

### 1. Document Structure
```python
# Good: Well-structured document with metadata
{
    "content": "Clear, concise content that answers specific questions.",
    "metadata": {
        "source": "user_manual.pdf",
        "category": "documentation",
        "version": "1.0",
        "last_updated": "2024-01-15"
    }
}

# Avoid: Vague content without context
{
    "content": "It works.",
    "metadata": {}
}
```

### 2. Query Optimization
- Use specific, detailed queries for better results
- Include relevant keywords from your domain
- Avoid overly broad or vague questions

### 3. Similarity Threshold Tuning
- Start with default (0.0) and monitor result quality
- Increase threshold if getting too many irrelevant results
- Decrease threshold if missing relevant information

### 4. Performance Optimization
- Batch document ingestion when possible
- Use appropriate `top_k` values (5-10 for most cases)
- Monitor vector store size and performance

### 5. Error Handling
```python
from shared.knowledge_base.rag_pipeline import RAGPipelineError
from shared.knowledge_base.kb_manager import KnowledgeBaseError

try:
    result = kb_manager.search("query")
except KnowledgeBaseError as e:
    logger.error(f"Search failed: {e}")
    # Handle error gracefully
```

## Integration with Trivya Variants

### Mini Trivya
- Uses RAG for FAQ resolution
- Lower `top_k` (3-5) for faster responses
- Moderate similarity threshold (0.5-0.6)

### Trivya
- Enhanced RAG with learning capabilities
- Standard `top_k` (5-7)
- Adaptive similarity threshold based on query type

### Trivya High
- Advanced RAG with multi-source retrieval
- Higher `top_k` (7-10) for comprehensive context
- Dynamic threshold adjustment based on confidence

## Troubleshooting

### No Results Returned
- Check if documents are ingested: `kb_manager.get_stats()`
- Lower similarity threshold
- Verify query matches document content

### Poor Result Quality
- Increase similarity threshold
- Improve document quality and metadata
- Use more specific queries

### Slow Performance
- Reduce `top_k` value
- Optimize vector store configuration
- Consider caching frequent queries

## API Reference

### RAGPipeline
- `__init__(config, vector_store, logger, top_k, similarity_threshold)`
- `retrieve_context(query, top_k, filter_threshold) -> List[Dict]`
- `generate_prompt(query, context, system_instruction) -> str`
- `query(user_query, top_k, system_instruction) -> Dict`
- `get_pipeline_stats() -> Dict`

### KnowledgeBaseManager
- `__init__(config, vector_store, rag_pipeline, logger)`
- `validate_document(document) -> bool`
- `ingest_documents(documents, validate) -> Dict`
- `update_document(doc_id, new_content, metadata) -> bool`
- `search(query, top_k, system_instruction) -> Dict`
- `get_stats() -> Dict`
- `health_check() -> Dict`

## Next Steps

After implementing the RAG pipeline, you can:
1. Integrate with AI agents for automated responses
2. Implement caching for frequently asked questions
3. Add analytics for query patterns and performance
4. Build feedback loops for continuous improvement
