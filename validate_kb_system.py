"""
End-to-end validation script for the Knowledge Base system.
Tests VectorStore, RAGPipeline, and KnowledgeBaseManager integration.
"""

import sys
import os
import tempfile
import traceback

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from shared.core_functions.config import Config
from shared.core_functions.logger import TrivyaLogger, get_logger
from shared.knowledge_base.vector_store import VectorStore
from shared.knowledge_base.rag_pipeline import RAGPipeline
from shared.knowledge_base.kb_manager import KnowledgeBaseManager


def test_knowledge_base_system():
    """Run end-to-end tests for the Knowledge Base system."""
    try:
        print("\n[TEST] Starting Knowledge Base System Validation...")
        
        # Initialize configuration
        print("\n1. Testing Configuration...")
        config = Config()
        print("[OK] Configuration loaded successfully")
        
        # Initialize logger
        logger = get_logger(config)
        print("[OK] Logger initialized successfully")
        
        # Test Vector Store
        print("\n2. Testing Vector Store...")
        vector_store = VectorStore(config, logger)
        
        # Add test documents
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Trivya is a multi-tier AI phone agent platform supporting Mini, Pro, and Enterprise tiers.")
            temp_doc_path = f.name
        
        doc_ids = vector_store.add_documents([{
            "content": "Trivya is a multi-tier AI phone agent platform supporting Mini, Pro, and Enterprise tiers.",
            "metadata": {"source": "test_doc.txt"}
        }])
        print(f"[OK] Documents added to vector store with IDs: {doc_ids}")
        
        # Test similarity search
        results = vector_store.similarity_search("What is Trivya?", top_k=1)
        assert len(results) > 0, "No search results returned"
        print(f"[OK] Similarity search returned {len(results)} results")
        
        # Test RAG Pipeline
        print("\n3. Testing RAG Pipeline...")
        rag_pipeline = RAGPipeline(config, vector_store, logger)
        
        # Generate response using RAG
        query = "What is Trivya?"
        response = rag_pipeline.generate_response(query)
        assert "Trivya" in response, "Response doesn't contain expected information"
        print(f"[OK] RAG response: {response[:100]}...")
        
        # Test Knowledge Base Manager
        print("\n4. Testing Knowledge Base Manager...")
        kb_manager = KnowledgeBaseManager(config, vector_store, rag_pipeline, logger)
        
        # Test adding document through KB manager
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Trivya Mini is the basic tier that handles up to 2 concurrent calls.")
            temp_doc_path_2 = f.name
        
        doc_id_2 = kb_manager.add_document(temp_doc_path_2)
        print(f"[OK] Document added through KB manager with ID: {doc_id_2}")
        
        # Test query through KB manager
        response_2 = kb_manager.query("What is Trivya Mini?")
        assert "Trivya Mini" in response_2, "Response doesn't contain expected information"
        print(f"[OK] KB manager query response: {response_2[:100]}...")
        
        # Test document management
        docs = kb_manager.list_documents()
        assert len(docs) >= 2, "Expected at least 2 documents in KB"
        print(f"[OK] KB contains {len(docs)} documents")
        
        # Test knowledge base statistics
        stats = kb_manager.get_stats()
        assert stats is not None, "Stats returned None"
        print(f"[OK] KB stats retrieved successfully")
        
        # Clean up
        os.unlink(temp_doc_path)
        os.unlink(temp_doc_path_2)
        
        print("\n[SUCCESS] All Knowledge Base system tests passed!")
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Knowledge Base system validation failed: {str(e)}")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_knowledge_base_system()
    sys.exit(0 if success else 1)
