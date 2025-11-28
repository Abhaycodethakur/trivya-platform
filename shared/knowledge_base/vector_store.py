import chromadb
from typing import List, Dict, Any, Optional
from chromadb.config import Settings
from shared.core_functions.config import Config
from shared.core_functions.logger import get_logger

class VectorStore:
    """
    Abstraction layer for interacting with the vector database (ChromaDB).
    Responsible for adding documents and performing similarity searches.
    """

    def __init__(self, config: Config):
        """
        Initialize the VectorStore with configuration.

        Args:
            config (Config): The main configuration object.
        """
        self.config = config
        self.logger = get_logger(self.config).get_logger("VectorStore")
        
        self.db_type = self.config.vector_db_config.VECTOR_DB_TYPE
        self.db_path = self.config.vector_db_config.VECTOR_DB_PATH
        self.collection_name = self.config.vector_db_config.COLLECTION_NAME

        self.logger.info(f"Initializing VectorStore with type={self.db_type}, path={self.db_path}")

        try:
            if self.db_type == "chromadb":
                self.client = chromadb.PersistentClient(path=self.db_path)
                self.collection = self.client.get_or_create_collection(name=self.collection_name)
                self.logger.info(f"Successfully connected to ChromaDB collection: {self.collection_name}")
            else:
                raise ValueError(f"Unsupported VECTOR_DB_TYPE: {self.db_type}")
        except Exception as e:
            self.logger.error(f"Failed to initialize VectorStore: {str(e)}")
            raise

    def add_documents(self, documents: List[Dict[str, Any]]) -> List[str]:
        """
        Add documents to the vector store.

        Args:
            documents (List[Dict[str, Any]]): List of documents. Each dict must have 'content' (str) and 'metadata' (dict).

        Returns:
            List[str]: List of IDs of the added documents.
        """
        if not documents:
            self.logger.warning("No documents provided to add_documents")
            return []

        try:
            ids = [str(i) for i in range(len(documents))] # Simple ID generation for now, can be improved
            # In a real app, we might want to generate UUIDs or use a hash of the content
            import uuid
            ids = [str(uuid.uuid4()) for _ in documents]
            
            contents = [doc['content'] for doc in documents]
            metadatas = [doc['metadata'] for doc in documents]

            self.collection.add(
                documents=contents,
                metadatas=metadatas,
                ids=ids
            )
            
            self.logger.info(f"Successfully added {len(documents)} documents to collection {self.collection_name}")
            return ids
        except Exception as e:
            self.logger.error(f"Failed to add documents: {str(e)}")
            raise

    def similarity_search(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Perform a similarity search against the collection.

        Args:
            query (str): The query string.
            n_results (int): Number of results to return.

        Returns:
            List[Dict[str, Any]]: List of documents with 'content' and 'metadata'.
        """
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            # ChromaDB returns a dict of lists, we need to restructure it
            # results = {'ids': [['id1']], 'documents': [['doc1']], 'metadatas': [[{'meta': 'data'}]]}
            
            formatted_results = []
            if results['documents']:
                num_results = len(results['documents'][0])
                for i in range(num_results):
                    formatted_results.append({
                        'content': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                        'id': results['ids'][0][i]
                    })
            
            self.logger.info(f"Similarity search for '{query}' returned {len(formatted_results)} results")
            return formatted_results
        except Exception as e:
            self.logger.error(f"Failed to perform similarity search: {str(e)}")
            raise

    def delete_collection(self):
        """
        Delete the entire collection.
        """
        try:
            self.client.delete_collection(name=self.collection_name)
            self.logger.warning(f"Deleted collection: {self.collection_name}")
            # Re-create it so the object is still usable
            self.collection = self.client.get_or_create_collection(name=self.collection_name)
        except Exception as e:
            self.logger.error(f"Failed to delete collection: {str(e)}")
            raise
