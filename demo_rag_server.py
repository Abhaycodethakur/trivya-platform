"""
RAG Server Manual Test Script
Run this to manually test the RAG Server with the OpenRouter API.

Usage:
    python demo_rag_server.py
"""

import asyncio
import os

# Set required environment variables before importing Config
os.environ["DATABASE_URL"] = "postgresql://user:pass@localhost:5432/demo_db"
os.environ["JWT_SECRET_KEY"] = "demo-secret-key"
os.environ["OPENROUTER_API_KEY"] = "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"

from mcp_servers.knowledge.rag_server import RAGServer
from mcp_servers.base_server import MCPMessage, MCPMessageHeader, MessageType
from shared.core_functions.config import Config, VectorDBConfig


class DemoConfig(Config):
    """Demo configuration for manual testing"""
    def __init__(self):
        super().__init__()
        self.env.update({
            "VECTOR_DB_TYPE": "chromadb",
            "VECTOR_DB_PATH": "./data/demo_rag_db",
            "COLLECTION_NAME": "demo_rag_collection",
            "OPENROUTER_API_KEY": os.environ["OPENROUTER_API_KEY"],
            "RAG_MODEL": "google/gemma-3-27b-it:free",
        })
        self.vector_db_config = VectorDBConfig(
            VECTOR_DB_TYPE="chromadb",
            VECTOR_DB_PATH="./data/demo_rag_db",
            COLLECTION_NAME="demo_rag_collection"
        )


def setup_demo_knowledge_base(server: RAGServer):
    """Populate the vector store with demo knowledge"""
    documents = [
        {
            "id": "doc_1",
            "content": "Trivya is an AI-powered customer service platform that provides intelligent automation for businesses. It offers three variants: Mini Trivya, Trivya, and Trivya High.",
            "metadata": {"source": "product_overview", "topic": "trivya"}
        },
        {
            "id": "doc_2", 
            "content": "Mini Trivya focuses on FAQ automation, email handling, and basic chat support. It's ideal for small businesses looking to automate their customer service.",
            "metadata": {"source": "product_variants", "topic": "mini_trivya"}
        },
        {
            "id": "doc_3",
            "content": "Python was created by Guido van Rossum and first released in 1991. It is known for its simple syntax and readability.",
            "metadata": {"source": "tech_facts", "topic": "python"}
        },
        {
            "id": "doc_4",
            "content": "The speed of light in a vacuum is approximately 299,792 kilometers per second (about 186,282 miles per second).",
            "metadata": {"source": "physics_facts", "topic": "physics"}
        },
        {
            "id": "doc_5",
            "content": "Paris is the capital of France. It is known for the Eiffel Tower, the Louvre Museum, and its rich history and culture.",
            "metadata": {"source": "geography", "topic": "france"}
        }
    ]
    
    # Clear existing data and add fresh documents
    try:
        server.vector_store.delete_collection()
    except:
        pass
    
    server.vector_store.add_documents(documents)
    print(f"✅ Loaded {len(documents)} documents into the knowledge base\n")


async def test_query(server: RAGServer, query: str):
    """Send a query to the RAG server and display the response"""
    print(f"🔍 Query: {query}")
    print("-" * 50)
    
    request = MCPMessage(
        header=MCPMessageHeader(
            message_type=MessageType.REQUEST,
            source="manual_test"
        ),
        body={"query": query}
    )
    
    try:
        response = await server.handle_request(request)
        
        print(f"📝 Answer:\n{response['answer']}\n")
        print(f"📊 Confidence: {response['confidence']:.2f}")
        print(f"📚 Sources: {len(response['sources'])} document(s) used")
        
        for i, source in enumerate(response['sources'][:2], 1):
            print(f"   {i}. {source['title']} - {source['snippet'][:80]}...")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60 + "\n")


async def main():
    print("=" * 60)
    print("       RAG Server Manual Test")
    print("=" * 60)
    print()
    
    # Initialize the RAG Server
    print("🚀 Initializing RAG Server...")
    config = DemoConfig()
    server = RAGServer(config=config)
    print("✅ RAG Server initialized\n")
    
    # Setup demo knowledge base
    print("📚 Setting up demo knowledge base...")
    setup_demo_knowledge_base(server)
    
    # Test queries
    test_queries = [
        "What is Trivya and what does it offer?",
        "Who created Python and when?",
        "What is the capital of France?",
        "How fast is the speed of light?",
        "What is the recipe for chocolate cake?"  # Not in knowledge base
    ]
    
    for query in test_queries:
        await test_query(server, query)
    
    print("✅ All tests completed!")
    print("\n💡 Tip: You can modify the queries in this script to test other questions.")


if __name__ == "__main__":
    asyncio.run(main())
