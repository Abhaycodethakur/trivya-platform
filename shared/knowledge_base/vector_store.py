import chromadb
from pathlib import Path
from typing import List, Dict, Any, Optional
from chromadb.config import Settings
from shared.core_functions.config import Config
from shared.core_functions.logger import get_logger, TrivyaLogger

class VectorStore:
    """
    Abstraction layer for interacting with the vector database (ChromaDB).
    Responsible for adding documents and performing similarity searches.
    """

    def __init__(self, config: Config, logger: Optional[TrivyaLogger] = None):
        """
        Initialize the VectorStore with configuration.

        Args:
            config (Config): The main configuration object.
        """
        self.config = config
        base_logger = logger or get_logger(self.config)
        self.logger = base_logger.get_logger("VectorStore")
        
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

    def add_document(self, file_path: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add a single document from a file path to the store."""
        try:
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(f"Document not found: {file_path}")

            content = path.read_text(encoding="utf-8")
            document = {
                "content": content,
                "metadata": metadata or {"source": path.name}
            }

            document_ids = self.add_documents([document])
            return document_ids[0] if document_ids else ""
        except Exception as e:
            self.logger.error(f"Failed to add document '{file_path}': {str(e)}")
            raise

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Convenience wrapper around similarity_search for readability."""
        return self.similarity_search(query, n_results=top_k)

    def get_collection_info(self) -> Dict[str, Any]:
        """Return high-level metadata about the underlying collection."""
        info = {
            "name": self.collection_name,
            "db_type": self.db_type,
            "path": self.db_path,
            "document_count": 0
        }
        try:
            info["document_count"] = self.collection.count()
        except Exception as e:
            self.logger.warning(f"Unable to fetch collection count: {str(e)}")
        return info

    def list_documents(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """List documents stored in the collection (best-effort)."""
        try:
            include = ["metadatas", "documents", "ids"]
            results = self.collection.get(limit=limit, include=include)
            documents = []
            ids = results.get("ids", []) or []
            contents = results.get("documents", []) or []
            metadatas = results.get("metadatas", []) or []

            for idx, doc_id in enumerate(ids):
                content = contents[idx] if idx < len(contents) else ""
                metadata = metadatas[idx] if idx < len(metadatas) else {}
                documents.append({
                    "id": doc_id,
                    "content": content,
                    "metadata": metadata
                })

            return documents
        except Exception as e:
            self.logger.error(f"Failed to list documents: {str(e)}")
            return []
