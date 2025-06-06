from typing import Dict, List, Optional, Any, Union
import json
import requests
from mcp.server.fastmcp import FastMCP

class EmbeddingTools:
    def __init__(self, aos_client, api_token=None):
        self.aos_client = aos_client
        self.api_token = api_token
        self.embedding_api_url = "https://api.siliconflow.cn/v1/embeddings"
        self.default_model = "Pro/BAAI/bge-m3"
        self.vector_field = "dense_vector"
        self.vector_dimension = 1024

    async def generate_embedding(self, text: str, model: str = None) -> Dict:
        """
        Generate vector embedding for the provided text using Silicon Flow API.
        
        Args:
            text: The text to convert to a vector embedding
            model: The model to use for embedding (default: Pro/BAAI/bge-m3)
            
        Returns:
            Dictionary containing the embedding vector or error information
        """
        if not self.api_token:
            return {"status": "error", "message": "API token not configured for embedding service"}
        
        try:
            model_name = model if model else self.default_model
            
            payload = {
                "model": model_name,
                "input": text,
                "encoding_format": "float"
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(self.embedding_api_url, json=payload, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            return {
                "status": "success", 
                "embedding": result.get("data", [{}])[0].get("embedding", []),
                "model": model_name
            }
            
        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": f"API request failed: {str(e)}"}
        except Exception as e:
            return {"status": "error", "message": f"Unexpected error: {str(e)}"}

    async def knn_search(self, vector: List[float], k: int = 10) -> Dict:
        """
        Perform k-nearest neighbors search using a vector.
        
        Args:
            vector: The query vector to search with
            k: Number of nearest neighbors to return
            
        Returns:
            Dictionary containing search results or error information
        """
        try:
            # Validate vector dimension
            if len(vector) != self.vector_dimension:
                return {
                    "status": "error", 
                    "message": f"Vector dimension mismatch. Expected {self.vector_dimension}, got {len(vector)}"
                }
            
            # Construct kNN query
            query = {
                "size": k,
                "query": {
                    "knn": {
                        self.vector_field: {
                            "vector": vector,
                            "k": k
                        }
                    }
                },
                "_source": {
                    "excludes": [self.vector_field]  # Always exclude the vector field
                }
            }
            
            # Execute search
            result = await self.aos_client.search_documents(json.dumps(query), k)
            
            # Process results to extract only text content
            if result["status"] == "success" and "results" in result:
                hits = result["results"].get("hits", {}).get("hits", [])
                simplified_results = []
                
                for hit in hits:
                    source = hit.get("_source", {})
                    simplified_results.append({
                        "id": hit.get("_id"),
                        "score": hit.get("_score"),
                        "text": source.get("text", ""),
                        "metadata": {k: v for k, v in source.items() if k != "text" and k != self.vector_field}
                    })
                
                return {
                    "status": "success",
                    "results": simplified_results,
                    "total": len(simplified_results)
                }
            
            return result
            
        except Exception as e:
            return {"status": "error", "message": f"kNN search error: {str(e)}"}

    async def bulk_index_with_embeddings(self, documents: List[Dict], text_field: str = "text") -> Dict:
        """
        Generate embeddings for multiple documents and index them in bulk.
        
        Args:
            documents: List of documents to process and index
            text_field: The field name containing text to embed
            
        Returns:
            Dictionary containing the bulk operation results
        """
        try:
            processed_docs = []
            failed_docs = []
            
            for doc in documents:
                if text_field not in doc:
                    failed_docs.append({"doc": doc, "reason": f"Missing text field '{text_field}'"})
                    continue
                
                # Generate embedding
                embedding_result = await self.generate_embedding(doc[text_field])
                
                if embedding_result["status"] != "success":
                    failed_docs.append({"doc": doc, "reason": embedding_result["message"]})
                    continue
                
                # Add embedding to document
                doc_copy = doc.copy()
                doc_copy[self.vector_field] = embedding_result["embedding"]
                processed_docs.append(doc_copy)
            
            # If no documents were processed successfully
            if not processed_docs:
                return {
                    "status": "error", 
                    "message": "No documents were processed successfully", 
                    "failed_docs": failed_docs
                }
            
            # Bulk index the processed documents
            client = self.aos_client.get_client()
            bulk_data = []
            
            for doc in processed_docs:
                # If document has an ID
                if "_id" in doc:
                    doc_id = doc.pop("_id")
                    bulk_data.append({"index": {"_index": self.aos_client._index_name, "_id": doc_id}})
                else:
                    # Let OpenSearch generate an ID
                    bulk_data.append({"index": {"_index": self.aos_client._index_name}})
                bulk_data.append(doc)
            
            response = client.bulk(body=bulk_data, refresh=True)
            
            return {
                "status": "success", 
                "response": response, 
                "processed_count": len(processed_docs),
                "failed_count": len(failed_docs),
                "failed_docs": failed_docs if failed_docs else None
            }
            
        except Exception as e:
            return {"status": "error", "message": f"Bulk indexing error: {str(e)}"}

    def register_tools(self, mcp: FastMCP):
        @mcp.tool()
        async def index_text_with_embedding(text: str, document_id: str = None, metadata: Dict = None) -> Dict:
            """
            Ingest doc into Knowledge Base by convert text to embedding and then write text and embedding to OpenSearch vector database.
            
            Args:
                text: The text to convert and index
                document_id: Optional ID for the document (auto-generated if not provided)
                metadata: Optional metadata to store with the document
                
            Returns:
                Dictionary containing the response or error information
            """
            # Generate embedding
            embedding_result = await self.generate_embedding(text)
            
            if embedding_result["status"] != "success":
                return embedding_result
            
            # Prepare document with embedding vector
            document = metadata or {}
            document["text"] = text
            document[self.vector_field] = embedding_result["embedding"]
            
            # Index document with or without ID
            if document_id:
                return await self.aos_client.write_document(document_id, document)
            else:
                return await self.aos_client.index_document(document)
        
        @mcp.tool()
        async def text_similarity_search(text: str, k: int = 10) -> Dict:
            """
            Search in Knowledge Base by searching for similar documents by converting text to embedding and performing kNN search.
            
            Args:
                text: The text to search for similar documents
                k: Number of similar documents to return
                
            Returns:
                Dictionary containing search results or error information
            """
            # Generate embedding for query text
            embedding_result = await self.generate_embedding(text)
            
            if embedding_result["status"] != "success":
                return embedding_result
            
            # Perform kNN search with the generated embedding
            search_result = await self.knn_search(embedding_result["embedding"], k)
            
            if search_result["status"] == "success":
                return {
                    "status": "success",
                    "query_text": text,
                    "results": search_result["results"],
                    "total": search_result.get("total", 0)
                }
            else:
                return search_result

