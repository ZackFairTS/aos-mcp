from typing import Dict, List, Optional, Any
import json
from mcp.server.fastmcp import FastMCP

class DocumentTools:
    def __init__(self, aos_client):
        self.aos_client = aos_client

    def register_tools(self, mcp: FastMCP):
        @mcp.tool()
        async def search_documents(query: str, size: int = 10) -> Dict:
            """
            Search for documents in OpenSearch using the provided query.
            
            Args:
                query: The search query in OpenSearch DSL format
                size: Maximum number of results to return (default: 10)
                
            Returns:
                Dictionary containing search results or error information
            """
            return await self.aos_client.search_documents(query, size)
        
        @mcp.tool()
        async def get_document(document_id: str) -> Dict:
            """
            Retrieve a specific document by its ID.
            
            Args:
                document_id: The ID of the document to retrieve
                
            Returns:
                Dictionary containing the document or error information
            """
            query = {
                "query": {
                    "term": {
                        "_id": document_id
                    }
                }
            }
            result = await self.aos_client.search_documents(json.dumps(query), 1)
            
            if result["status"] == "success" and len(result["results"]["hits"]["hits"]) > 0:
                return {
                    "status": "success", 
                    "document": result["results"]["hits"]["hits"][0]
                }
            else:
                return {
                    "status": "error", 
                    "message": f"Document with ID {document_id} not found"
                }
        
        @mcp.tool()
        async def put(document_id: str, document: Dict) -> Dict:
            """
            Write or update a document in OpenSearch.

            Args:
                document_id: The ID for the document
                document: The document content to write

            Returns:
                Dictionary containing the response or error information
            """
            return await self.aos_client.write_document(document_id, document)
        
        @mcp.tool()
        async def delete_document(document_id: str) -> Dict:
            """
            Delete a document from OpenSearch.
            
            Args:
                document_id: The ID of the document to delete
                
            Returns:
                Dictionary containing the response or error information
            """
            return await self.aos_client.delete_document(document_id)
        
        @mcp.tool()
        async def bulk_index_documents(documents: List[Dict], generate_ids: bool = False) -> Dict:
            """
            Index multiple documents in a single bulk operation.
            
            Args:
                documents: List of documents to index
                generate_ids: If True, OpenSearch will generate IDs for documents
                
            Returns:
                Dictionary containing the bulk operation results
            """
            try:
                client = self.aos_client.get_client()
                bulk_data = []
                
                for doc in documents:
                    # If document has an ID and we're not generating IDs
                    if "_id" in doc and not generate_ids:
                        doc_id = doc.pop("_id")
                        bulk_data.append({"index": {"_index": self.aos_client._index_name, "_id": doc_id}})
                    else:
                        bulk_data.append({"index": {"_index": self.aos_client._index_name}})
                    bulk_data.append(doc)
                
                response = client.bulk(body=bulk_data, refresh=True)
                return {"status": "success", "response": response}
                
            except Exception as e:
                return {"status": "error", "message": f"Bulk indexing error: {str(e)}"}
