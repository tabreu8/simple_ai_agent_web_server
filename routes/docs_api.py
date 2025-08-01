from fastapi import APIRouter, UploadFile, File, HTTPException, Query, Form
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime
import logging
import json

from knowledge_base.chromadb import get_chromadb_manager
from knowledge_base.doc_parsing import get_document_parser

logger = logging.getLogger(__name__)

router = APIRouter()


# Pydantic models
class DocumentChunk(BaseModel):
    """Model for a document chunk with content and metadata."""
    content: str
    metadata: Optional[Dict[str, Any]] = None


class DocumentInsertRequest(BaseModel):
    """Model for inserting document chunks."""
    documents: Optional[List[DocumentChunk]] = None


class DocumentUpdateRequest(BaseModel):
    """Model for updating a document."""
    document: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class QueryResponse(BaseModel):
    """Model for query response."""
    results: List[Dict[str, Any]]
    total_results: int


class DocumentResponse(BaseModel):
    """Model for document response."""
    id: str
    document: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@router.post("/insert", response_model=Dict[str, Any])
async def insert_documents(
    documents: Optional[str] = Form(None, description="JSON string of document chunks"),
    files: List[UploadFile] = File(default=[])
):
    """
    Insert documents into the knowledge base.
    
    Accepts either:
    - JSON documents as form data (documents field)
    - Uploaded files (PDF, DOCX, etc.)
    - Both JSON documents and files
    
    Args:
        documents: Optional JSON string containing array of document chunks
        files: Optional list of files to upload and process
        
    Returns:
        Dictionary with inserted document IDs and status
    """
    try:
        all_documents = []
        all_metadatas = []
        processing_summary = {
            "json_documents": 0,
            "uploaded_files": 0,
            "total_chunks": 0,
            "processed_files": []
        }
        
        # Parse JSON documents if provided
        parsed_documents = []
        if documents and documents.strip():
            try:
                doc_data = json.loads(documents)
                if isinstance(doc_data, list):
                    parsed_documents = doc_data
                else:
                    parsed_documents = [doc_data]
            except json.JSONDecodeError as e:
                raise HTTPException(status_code=400, detail=f"Invalid JSON in documents field: {str(e)}")
        
        # Validate that at least one input is provided
        has_json_docs = len(parsed_documents) > 0
        has_files = files and len(files) > 0
        
        if not has_json_docs and not has_files:
            raise HTTPException(
                status_code=400, 
                detail="At least one of 'documents' (JSON) or 'files' must be provided"
            )
        
        # Process JSON documents if provided
        if has_json_docs:
            for doc_data in parsed_documents:
                if not isinstance(doc_data, dict) or "content" not in doc_data:
                    continue  # Skip invalid document entries
                    
                content = doc_data.get("content", "")
                if not content.strip():
                    continue  # Skip empty content
                    
                all_documents.append(content)
                
                # Prepare metadata
                metadata = doc_data.get("metadata", {})
                if not isinstance(metadata, dict):
                    metadata = {}
                    
                metadata.update({
                    "source_type": "json_input",
                    "created_at": str(datetime.now())
                })
                all_metadatas.append(metadata)
                processing_summary["json_documents"] += 1
        
        # Process uploaded files if provided
        if has_files:
            document_parser = get_document_parser()
            
            for file in files:
                if not file.filename:
                    continue  # Skip files without names
                
                if not document_parser.is_supported_file(file.filename):
                    supported_extensions = document_parser.get_supported_extensions()
                    raise HTTPException(
                        status_code=400,
                        detail=f"File '{file.filename}' type not supported. Supported types: {', '.join(supported_extensions)}"
                    )
                
                # Read and process file
                file_content = await file.read()
                if not file_content:
                    continue  # Skip empty files
                
                # Parse file and extract chunks
                chunks = document_parser.parse_file_content(file_content, file.filename)
                
                if chunks:
                    # Prepare metadata for each chunk
                    base_metadata = {
                        "source_filename": file.filename,
                        "source_type": "uploaded_file",
                        "file_size": len(file_content),
                        "content_type": file.content_type or "unknown",
                        "created_at": str(datetime.now())
                    }
                    
                    # Add chunks and their metadata
                    for i, chunk in enumerate(chunks):
                        all_documents.append(chunk)
                        
                        chunk_metadata = base_metadata.copy()
                        chunk_metadata.update({
                            "chunk_index": i,
                            "total_chunks": len(chunks)
                        })
                        all_metadatas.append(chunk_metadata)
                    
                    processing_summary["processed_files"].append({
                        "filename": file.filename,
                        "chunks_extracted": len(chunks),
                        "file_size": len(file_content)
                    })
                    processing_summary["uploaded_files"] += 1
        
        # Validate we have documents to insert
        if not all_documents:
            raise HTTPException(
                status_code=400, 
                detail="No valid content found to insert. Please check your documents and files."
            )
        
        # Insert all documents into ChromaDB
        chromadb_manager = get_chromadb_manager()
        doc_ids = chromadb_manager.insert_documents(
            documents=all_documents,
            metadatas=all_metadatas
        )
        
        processing_summary["total_chunks"] = len(doc_ids)
        
        return {
            "status": "success",
            "message": f"Successfully inserted {len(doc_ids)} documents",
            "document_ids": doc_ids,
            "processing_summary": processing_summary
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inserting documents: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to insert documents: {str(e)}")


@router.post("/upload", response_model=Dict[str, Any])
async def upload_file(file: UploadFile = File(...)):
    """
    DEPRECATED: Use POST /docs/insert instead.
    Upload and process a PDF or DOCX file.
    
    Args:
        file: UploadFile containing PDF or DOCX content
        
    Returns:
        Dictionary with inserted document IDs and processing status
    """
    # Redirect to the new combined endpoint
    return await insert_documents(documents=None, files=[file])


@router.get("/search", response_model=QueryResponse)
async def search_documents(
    query: str = Query(..., description="Search query text"),
    n_results: int = Query(10, ge=1, le=100, description="Number of results to return"),
    metadata_filter: Optional[str] = Query(None, description="JSON string for metadata filtering")
):
    """
    Search documents by query string.
    
    Args:
        query: Text to search for similar documents
        n_results: Number of results to return (1-100)
        metadata_filter: Optional JSON string for metadata filtering
        
    Returns:
        QueryResponse with search results
    """
    try:
        chromadb_manager = get_chromadb_manager()
        
        # Parse metadata filter if provided
        where_filter = None
        if metadata_filter:
            import json
            try:
                where_filter = json.loads(metadata_filter)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid JSON in metadata_filter parameter")
        
        # Perform search
        results = chromadb_manager.query_documents(
            query_text=query,
            n_results=n_results,
            where=where_filter
        )
        
        # Format results
        formatted_results = []
        for i in range(len(results["ids"])):
            formatted_results.append({
                "id": results["ids"][i],
                "document": results["documents"][i] if i < len(results["documents"]) else None,
                "metadata": results["metadatas"][i] if i < len(results["metadatas"]) else None,
                "similarity_score": 1 - results["distances"][i] if i < len(results["distances"]) else None,
                "distance": results["distances"][i] if i < len(results["distances"]) else None
            })
        
        return QueryResponse(
            results=formatted_results,
            total_results=len(formatted_results)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching documents: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to search documents: {str(e)}")


@router.put("/{doc_id}", response_model=Dict[str, Any])
async def update_document(doc_id: str, request: DocumentUpdateRequest):
    """
    Update a document by ID.
    
    Args:
        doc_id: Document ID to update
        request: DocumentUpdateRequest with new content and/or metadata
        
    Returns:
        Dictionary with update status
    """
    try:
        chromadb_manager = get_chromadb_manager()
        
        # Validate that at least one field is provided for update
        if request.document is None and request.metadata is None:
            raise HTTPException(
                status_code=400, 
                detail="At least one of 'document' or 'metadata' must be provided for update"
            )
        
        # Check if document exists
        existing_doc = chromadb_manager.get_document(doc_id)
        if not existing_doc:
            raise HTTPException(status_code=404, detail=f"Document with ID '{doc_id}' not found")
        
        # Perform update
        success = chromadb_manager.update_document(
            doc_id=doc_id,
            document=request.document,
            metadata=request.metadata
        )
        
        if success:
            return {
                "status": "success",
                "message": f"Successfully updated document '{doc_id}'",
                "document_id": doc_id
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to update document")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating document {doc_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update document: {str(e)}")


@router.delete("/{doc_id}", response_model=Dict[str, Any])
async def delete_document(doc_id: str):
    """
    Delete a document by ID.
    
    Args:
        doc_id: Document ID to delete
        
    Returns:
        Dictionary with deletion status
    """
    try:
        chromadb_manager = get_chromadb_manager()
        
        # Check if document exists
        existing_doc = chromadb_manager.get_document(doc_id)
        if not existing_doc:
            raise HTTPException(status_code=404, detail=f"Document with ID '{doc_id}' not found")
        
        # Perform deletion
        success = chromadb_manager.delete_document(doc_id)
        
        if success:
            return {
                "status": "success",
                "message": f"Successfully deleted document '{doc_id}'",
                "document_id": doc_id
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to delete document")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document {doc_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")


@router.get("/stats", response_model=Dict[str, Any])
async def get_collection_stats():
    """
    Get statistics about the document collection.
    
    Returns:
        Dictionary with collection statistics
    """
    try:
        chromadb_manager = get_chromadb_manager()
        stats = chromadb_manager.get_collection_stats()
        
        # Add additional information
        document_parser = get_document_parser()
        stats["supported_file_types"] = document_parser.get_supported_extensions()
        
        return {
            "status": "success",
            "stats": stats
        }
        
    except Exception as e:
        logger.error(f"Error getting collection stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get collection stats: {str(e)}")


@router.get("/{doc_id}", response_model=DocumentResponse)
async def get_document(doc_id: str):
    """
    Get a specific document by ID.
    
    Args:
        doc_id: Document ID to retrieve
        
    Returns:
        DocumentResponse with document content and metadata
    """
    try:
        chromadb_manager = get_chromadb_manager()
        
        # Get document
        doc = chromadb_manager.get_document(doc_id)
        
        if not doc:
            raise HTTPException(status_code=404, detail=f"Document with ID '{doc_id}' not found")
        
        return DocumentResponse(
            id=doc["id"],
            document=doc["document"],
            metadata=doc["metadata"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving document {doc_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve document: {str(e)}")
