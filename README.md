# AOS MCP Server

A Model Context Protocol (MCP) based Amazon OpenSearch vector search server that provides text embedding and similarity search functionality.

## Project Overview

AOS MCP Server is an MCP server implementation that connects to Amazon OpenSearch service, providing the following key features:

- **Text Embedding Generation**: Uses Silicon Flow API to convert text into vector embeddings
- **Vector Similarity Search**: Performs similar document retrieval in OpenSearch based on k-NN algorithm
- **Document Indexing and Management**: Supports adding, retrieving, and deleting documents

This project serves as a knowledge base backend for AI applications, supporting semantic search and document retrieval functionality.

## Features

- Integration with Amazon OpenSearch Service
- Vector embedding generation via Silicon Flow API
- k-NN similarity search for semantic document retrieval
- Document management (add, search, delete)
- MCP protocol support for easy integration with AI applications

## Environment Variables

The server can be configured using the following environment variables:

- `OPENSEARCH_HOST`: OpenSearch server address
- `OPENSEARCH_PORT`: OpenSearch server port (default: 443)
- `OPENSEARCH_INDEX`: Default index name
- `OPENSEARCH_USERNAME`: OpenSearch username (optional)
- `OPENSEARCH_PASSWORD`: OpenSearch password (optional)
- `EMBEDDING_API_TOKEN`: Access token for Silicon Flow API
- `DEBUG`: Enable debug logging (set to "true", "1", or "yes")

## Installation Steps

1. Clone the repository
2. Create and activate a virtual environment
3. Install dependencies

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Starting the Server

```bash
{
  "mcpServers": {
    "aosmcp": {
      "command": "uv",
      "args": [
        "--directory",
        "project_dir",
        "run",
        "server.py"
      ],
      "env": {
        "OPENSEARCH_HOST": "xxxx",
        "OPENSEARCH_PORT": "xxx",
        "OPENSEARCH_INDEX": "xxx",
        "OPENSEARCH_USERNAME": "xxx",
        "OPENSEARCH_PASSWORD": "xxxx",
        "EMBEDDING_API_TOKEN": "xxx"
      },
      "transportType": "stdio"
    }
  }
}
```

### Available MCP Tools

The server provides the following MCP tools:

#### Text Embedding and Indexing

```python
index_text_with_embedding(text: str, document_id: str = None, metadata: Dict = None) -> Dict
```

Converts text to vector embeddings and stores it in OpenSearch.

- `text`: Text to convert and index
- `document_id`: Document ID (optional, auto-generated if not provided)
- `metadata`: Metadata to store with the document (optional)

#### Similarity Search

```python
text_similarity_search(text: str, k: int = 10) -> Dict
```

Finds similar documents by converting text to embeddings and performing k-NN search.

- `text`: Text to search for similar documents
- `k`: Number of similar documents to return

## Project Structure

```
aos_mcp/
├── common/
│   └── aos_client.py       # OpenSearch client implementation
├── res/                    # Resource files
├── tools/
│   ├── cluster.py          # Cluster management tools
│   ├── document.py         # Document management tools
│   └── embedding.py        # Embedding and vector search tools
├── .venv/                  # Virtual environment
├── requirements.txt        # Project dependencies
├── server.py               # MCP server main program
└── .env.example            # Example environment variables
```

## Embedding Tools

The `EmbeddingTools` class provides text embedding and vector search functionality:

- Generate text embeddings using Silicon Flow API
- k-NN similarity search with configurable parameters
- Bulk indexing of documents with embeddings

## Example Use Cases

1. **Knowledge Base for AI Applications**: Store and retrieve documents semantically
2. **Semantic Search Engine**: Build search applications that understand meaning, not just keywords
3. **Document Recommendation**: Find similar documents based on content
4. **Content Organization**: Automatically categorize and organize documents

## Security Considerations

- Do not hardcode sensitive information (such as passwords, API tokens) in the code
- Use environment variables or secure configuration management solutions
- Ensure OpenSearch instances have appropriate access control and network security settings
- Implement proper authentication for production deployments

## License

[MIT License](LICENSE)


## Acknowledgements

- This project uses the [Model Context Protocol (MCP)](https://github.com/mcp-foundation/mcp) for AI application integration
- Vector embeddings are generated using Silicon Flow API
- Document storage and retrieval is powered by Amazon OpenSearch Service
