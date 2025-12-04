"""
Demo script to run the FAQ Agent.
Run this from the project root: python demo_faq_agent.py
"""

import sys
import os

# Ensure project root is in path
sys.path.append(os.getcwd())

from variants.mini.agents.faq_agent import FAQAgent
from shared.knowledge_base.kb_manager import KnowledgeBaseManager
from shared.knowledge_base.vector_store import VectorStore
from shared.knowledge_base.rag_pipeline import RAGPipeline
from shared.core_functions.config import Config

def main():
    print("Initializing FAQ Agent Demo...")
    
    # Setup dependencies
    # Set dummy env vars for Config validation
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    config = Config()
    
    # Use a temporary collection for demo
    # We need to be careful not to mess up real data, but for demo we'll just use what's there
    # or rely on the fact that it's a demo.
    vector_store = VectorStore(config=config)
    rag_pipeline = RAGPipeline(config=config, vector_store=vector_store)
    kb_manager = KnowledgeBaseManager(config=config, vector_store=vector_store, rag_pipeline=rag_pipeline)
    
    agent = FAQAgent(kb_manager=kb_manager)
    
    # Test Question
    question = "What is the refund policy?"
    print(f"\nProcessing Question: '{question}'")
    
    # Note: If the KB is empty, this will escalate.
    result = agent.process_question(question, "demo_user", "console")
    
    print("\n--- Result ---")
    print(f"Status: {result['status']}")
    print(f"Response: {result['response']}")
    print(f"Escalated: {result['escalated']}")
    print("--------------\n")

if __name__ == "__main__":
    main()
