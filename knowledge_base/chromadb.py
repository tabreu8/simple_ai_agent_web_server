import os
import chromadb
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
import logging
from agents import function_tool

logger = logging.getLogger(__name__)


class ChromaDBManager:
    """Manages ChromaDB operations for the knowledge base."""
    
    def __init__(self):
        """Initialize ChromaDB client and collection."""
        self.db_path = os.getenv("CHROMADB_PATH", "knowledge_base")
        self.collection_name = os.getenv("CHROMADB_COLLECTION", "standard_collection")
        
        # Ensure the database directory exists
        os.makedirs(self.db_path, exist_ok=True)
        
        # Initialize persistent client
        self.client = chromadb.PersistentClient(path=self.db_path)
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={
                "description": "Knowledge base collection for document storage and retrieval",
                "created": str(datetime.now())
            }
        )
        logger.info(f"ChromaDB initialized with collection '{self.collection_name}' at '{self.db_path}'")
    
    def insert_documents(self, documents: List[str], metadatas: Optional[List[Dict[str, Any]]] = None) -> List[str]:
        """
        Insert a list of document chunks into the collection.
        
        Args:
            documents: List of document strings (chunks)
            metadatas: Optional list of metadata dictionaries for each document
            
        Returns:
            List of generated document IDs
        """
        try:
            # Generate unique IDs for each document
            doc_ids = [str(uuid.uuid4()) for _ in documents]
            
            # Prepare metadata
            if metadatas is None:
                metadatas = [{"created_at": str(datetime.now())} for _ in documents]
            else:
                # Ensure each metadata has a created_at timestamp
                for metadata in metadatas:
                    if "created_at" not in metadata:
                        metadata["created_at"] = str(datetime.now())
            
            # Add documents to collection
            self.collection.add(
                ids=doc_ids,
                documents=documents,
                metadatas=metadatas
            )
            
            logger.info(f"Successfully inserted {len(documents)} documents")
            return doc_ids
            
        except Exception as e:
            logger.error(f"Error inserting documents: {str(e)}")
            raise
    
    def query_documents(self, query_text: str, n_results: int = 10, where: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Query documents by similarity to the query text.
        
        Args:
            query_text: Text to search for similar documents
            n_results: Number of results to return
            where: Optional metadata filter
            
        Returns:
            Dictionary containing query results
        """
        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results,
                where=where,
                include=["documents", "metadatas", "distances"]
            )
            
            # Flatten the results since we're only querying with one text
            flattened_results = {
                "ids": results["ids"][0] if results["ids"] else [],
                "documents": results["documents"][0] if results["documents"] else [],
                "metadatas": results["metadatas"][0] if results["metadatas"] else [],
                "distances": results["distances"][0] if results["distances"] else []
            }
            
            logger.info(f"Query returned {len(flattened_results['ids'])} results")
            return flattened_results
            
        except Exception as e:
            logger.error(f"Error querying documents: {str(e)}")
            raise
    
    def update_document(self, doc_id: str, document: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Update a document by ID.
        
        Args:
            doc_id: Document ID to update
            document: New document content (optional)
            metadata: New metadata (optional)
            
        Returns:
            True if update was successful, False if document not found
        """
        try:
            # First check if document exists
            existing = self.get_document(doc_id)
            if not existing:
                return False
            
            # Prepare update arguments
            update_kwargs = {"ids": [doc_id]}
            
            if document is not None:
                update_kwargs["documents"] = [document]
            
            if metadata is not None:
                # Add updated timestamp
                metadata["updated_at"] = str(datetime.now())
                update_kwargs["metadatas"] = [metadata]
            
            self.collection.update(**update_kwargs)
            logger.info(f"Successfully updated document {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating document {doc_id}: {str(e)}")
            raise
    
    def delete_document(self, doc_id: str) -> bool:
        """
        Delete a document by ID.
        
        Args:
            doc_id: Document ID to delete
            
        Returns:
            True if deletion was successful, False if document not found
        """
        try:
            # First check if document exists
            existing = self.get_document(doc_id)
            if not existing:
                return False
                
            self.collection.delete(ids=[doc_id])
            logger.info(f"Successfully deleted document {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting document {doc_id}: {str(e)}")
            raise
    
    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific document by ID.
        
        Args:
            doc_id: Document ID to retrieve
            
        Returns:
            Dictionary containing document data or None if not found
        """
        try:
            results = self.collection.get(
                ids=[doc_id],
                include=["documents", "metadatas"]
            )
            
            if results["ids"]:
                return {
                    "id": results["ids"][0],
                    "document": results["documents"][0] if results["documents"] else None,
                    "metadata": results["metadatas"][0] if results["metadatas"] else None
                }
            return None
            
        except Exception as e:
            logger.error(f"Error getting document {doc_id}: {str(e)}")
            raise
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the collection.
        
        Returns:
            Dictionary containing collection statistics
        """
        try:
            count = self.collection.count()
            return {
                "collection_name": self.collection_name,
                "document_count": count,
                "db_path": self.db_path
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {str(e)}")
            raise


# Global instance
_chromadb_manager = None


def get_chromadb_manager() -> ChromaDBManager:
    """Get or create the global ChromaDBManager instance."""
    global _chromadb_manager
    if _chromadb_manager is None:
        _chromadb_manager = ChromaDBManager()
    return _chromadb_manager


@function_tool
async def search_knowledge_base(query: str, max_results: int = 5) -> str:
    """
    Search the knowledge base for relevant documents.
    
    This tool searches through the stored documents to find information relevant 
    to the user's query. Use this when you need to find specific information 
    from the knowledge base or when answering questions that might be answered 
    by stored documents.
    
    Args:
        query: The search query to find relevant documents
        max_results: Maximum number of results to return (default: 5)
        
    Returns:
        A formatted string containing the search results with document content and metadata
    """
    try:
        manager = get_chromadb_manager()
        
        # Ensure max_results is within reasonable bounds
        max_results = max(1, min(max_results, 20))
        
        # Perform the search
        results = manager.query_documents(query, n_results=max_results)
        
        if not results["documents"]:
            return f"No documents found for query: '{query}'"
        
        # Format the results for the agent
        formatted_results = [f"Search Results for: '{query}'\n"]
        formatted_results.append(f"Found {len(results['documents'])} relevant document(s):\n")
        
        for i, (doc, metadata, distance) in enumerate(zip(
            results["documents"], 
            results["metadatas"], 
            results["distances"]
        )):
            formatted_results.append(f"--- Result {i+1} (Relevance Score: {1-distance:.3f}) ---")
            
            # Add metadata if available
            if metadata:
                if "filename" in metadata:
                    formatted_results.append(f"Source: {metadata['filename']}")
                if "created_at" in metadata:
                    formatted_results.append(f"Created: {metadata['created_at']}")
                if "page_number" in metadata:
                    formatted_results.append(f"Page: {metadata['page_number']}")
            
            # Add document content
            formatted_results.append("Content:")
            formatted_results.append(doc[:1000] + "..." if len(doc) > 1000 else doc)
            formatted_results.append("")  # Empty line for separation
        
        return "\n".join(formatted_results)
        
    except Exception as e:
        logger.error(f"Error searching knowledge base: {str(e)}")
        return f"Error searching knowledge base: {str(e)}"
