"""
RAG (Retrieval-Augmented Generation) Pipeline for Trivya Platform

This module provides intelligent document retrieval and context assembly
for AI agents to answer customer questions accurately using the vector store.
"""

from typing import List, Dict, Any, Optional
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from shared.core_functions.config import Config
from shared.core_functions.logger import get_logger
from shared.knowledge_base.vector_store import VectorStore


class RAGPipelineError(Exception):
    """Custom exception for RAG Pipeline errors"""
    pass


class RAGPipeline:
    """
    RAG Pipeline for retrieving relevant context and generating prompts.
    
    This class orchestrates the retrieval of relevant documents from the
    vector store and assembles them into context for LLM queries.
    """
    
    def __init__(
        self,
        config: Config,
        vector_store: VectorStore,
        logger: Optional[Any] = None,
        top_k: int = 5,
        similarity_threshold: float = 0.0
    ):
        """
        Initialize the RAG Pipeline.
        
        Args:
            config: Config object containing pipeline settings
            vector_store: VectorStore instance for document retrieval
            logger: Optional Logger instance
            top_k: Default number of documents to retrieve
            similarity_threshold: Minimum similarity score for results
            
        Raises:
            RAGPipelineError: If initialization fails
        """
        self.config = config
        self.vector_store = vector_store
        self.logger = logger or get_logger(config).get_logger("RAGPipeline")
        self.top_k = top_k
        self.similarity_threshold = similarity_threshold
        
        self.logger.info(
            "RAG Pipeline initialized",
            extra={
                "top_k": self.top_k,
                "similarity_threshold": self.similarity_threshold
            }
        )
    
    def retrieve_context(
        self,
        query: str,
        top_k: Optional[int] = None,
        filter_threshold: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant context documents for a query.
        
        Args:
            query: User query string
            top_k: Number of documents to retrieve (uses default if None)
            filter_threshold: Whether to filter by similarity threshold
            
        Returns:
            List of context documents with content and metadata
            
        Raises:
            RAGPipelineError: If retrieval fails
        """
        try:
            if not query or not query.strip():
                self.logger.warning("Empty query provided to retrieve_context")
                return []
            
            k = top_k if top_k is not None else self.top_k
            
            # Retrieve documents from vector store
            results = self.vector_store.similarity_search(query, n_results=k)
            
            # Filter by similarity threshold if enabled
            if filter_threshold and self.similarity_threshold > 0:
                filtered_results = []
                for result in results:
                    # Distance is inverse of similarity (lower is better)
                    # Convert to similarity score (higher is better)
                    if result.get('distance') is not None:
                        similarity = 1.0 - result['distance']
                        if similarity >= self.similarity_threshold:
                            result['similarity_score'] = similarity
                            filtered_results.append(result)
                    else:
                        # If no distance, include the result
                        filtered_results.append(result)
                
                results = filtered_results
            
            self.logger.info(
                f"Retrieved {len(results)} context documents",
                extra={
                    "query_length": len(query),
                    "results_count": len(results),
                    "top_k": k
                }
            )
            
            return results
            
        except Exception as e:
            error_msg = f"Failed to retrieve context: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise RAGPipelineError(error_msg) from e
    
    def generate_prompt(
        self,
        query: str,
        context: List[Dict[str, Any]],
        system_instruction: Optional[str] = None
    ) -> str:
        """
        Generate a prompt for the LLM by combining query with context.
        
        Args:
            query: User query string
            context: List of context documents
            system_instruction: Optional system-level instruction
            
        Returns:
            Formatted prompt string for LLM
        """
        try:
            if not context:
                self.logger.warning("No context provided for prompt generation")
                return f"Query: {query}\n\nNo relevant context found. Please answer based on general knowledge."
            
            # Build context section
            context_parts = []
            for idx, doc in enumerate(context, 1):
                content = doc.get('content', '')
                metadata = doc.get('metadata', {})
                similarity = doc.get('similarity_score')
                
                context_part = f"[Document {idx}]"
                if metadata:
                    context_part += f"\nSource: {metadata.get('source', 'Unknown')}"
                if similarity is not None:
                    context_part += f"\nRelevance: {similarity:.2%}"
                context_part += f"\nContent: {content}\n"
                
                context_parts.append(context_part)
            
            context_text = "\n".join(context_parts)
            
            # Assemble final prompt
            prompt_parts = []
            
            if system_instruction:
                prompt_parts.append(f"System: {system_instruction}\n")
            
            prompt_parts.append("Context Information:")
            prompt_parts.append(context_text)
            prompt_parts.append(f"\nUser Query: {query}")
            prompt_parts.append("\nPlease answer the query based on the context provided above.")
            
            prompt = "\n".join(prompt_parts)
            
            self.logger.info(
                "Generated prompt for LLM",
                extra={
                    "context_docs": len(context),
                    "prompt_length": len(prompt)
                }
            )
            
            return prompt
            
        except Exception as e:
            error_msg = f"Failed to generate prompt: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise RAGPipelineError(error_msg) from e
    
    def query(
        self,
        user_query: str,
        top_k: Optional[int] = None,
        system_instruction: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        End-to-end RAG query: retrieve context and generate prompt.
        
        Args:
            user_query: User's question
            top_k: Number of documents to retrieve
            system_instruction: Optional system instruction for LLM
            
        Returns:
            Dictionary with 'prompt' and 'context' keys
            
        Raises:
            RAGPipelineError: If query processing fails
        """
        try:
            # Retrieve relevant context
            context = self.retrieve_context(user_query, top_k=top_k)
            
            # Generate prompt
            prompt = self.generate_prompt(
                user_query,
                context,
                system_instruction=system_instruction
            )
            
            result = {
                "query": user_query,
                "prompt": prompt,
                "context": context,
                "context_count": len(context)
            }
            
            self.logger.info(
                "RAG query completed successfully",
                extra={
                    "query_length": len(user_query),
                    "context_count": len(context)
                }
            )
            
            return result
            
        except Exception as e:
            error_msg = f"RAG query failed: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise RAGPipelineError(error_msg) from e
    
    def get_pipeline_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the RAG pipeline configuration.
        
        Returns:
            Dictionary with pipeline statistics
        """
        try:
            vector_store_info = self.vector_store.get_collection_info()
            
            stats = {
                "top_k": self.top_k,
                "similarity_threshold": self.similarity_threshold,
                "vector_store": vector_store_info
            }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get pipeline stats: {str(e)}")
            return {
                "error": str(e),
                "top_k": self.top_k,
                "similarity_threshold": self.similarity_threshold
            }
