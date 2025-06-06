import logging
import sys
import os
from mcp.server.fastmcp import FastMCP
from common.aos_client import OpenSearchClient
from tools.cluster import ClusterTools
from tools.document import DocumentTools
from tools.embedding import EmbeddingTools

# set version
VERSION="1.0"

# Configure logging
def setup_logging(debug=False):
    """
    Configure logging with optional debug mode.

    Args:
        debug: If True, set log level to DEBUG, otherwise INFO
    """
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger()

class SearchMCPServer:
    def __init__(self, opensearch_host: str, opensearch_port: int, index_name: str,
                 username: str = None, password: str = None, debug: bool = False, 
                 embedding_api_token: str = None):
        """
        Initialize the Search MCP Server.

        Args:
            opensearch_host: OpenSearch host address
            opensearch_port: OpenSearch port number
            index_name: Default index name to use
            username: Optional username for authentication
            password: Optional password for authentication
            debug: Enable debug logging if True
            embedding_api_token: API token for the embedding service
        """
        self.name = "aos_mcp_server"
        self.mcp = FastMCP(self.name)
        self.logger = setup_logging(debug=False)
        self.logger.info(f"Initializing {self.name}, Version: {VERSION}")
        if debug:
            self.logger.debug("Debug logging enabled")

        # Create the OpenSearch client
        self.aos_client = OpenSearchClient(
            opensearch_host=opensearch_host,
            opensearch_port=opensearch_port,
            index_name=index_name,
            username=username,
            password=password,
            use_ssl=True,
            verify_certs=True,
            ssl_assert_hostname=False,
            ssl_show_warn=True
        )
        
        # Store embedding API token
        self.embedding_api_token = embedding_api_token

        # Initialize tools
        self._register_tools()

    def _register_tools(self):
        """Register all MCP tools."""
        self.logger.debug("Registering MCP tools")

        # tools
        # cluster_tools = ClusterTools(self.aos_client)
        # document_tools = DocumentTools(self.aos_client)
        embedding_tools = EmbeddingTools(self.aos_client, api_token=self.embedding_api_token)

        # # register tools
        # cluster_tools.register_tools(self.mcp)
        # document_tools.register_tools(self.mcp)
        embedding_tools.register_tools(self.mcp)

        self.logger.debug(f"Registered tool classes")

    def run(self):
        """Run the MCP server."""
        try:
            self.logger.debug("Starting MCP server")
            self.mcp.run()
        except Exception as e:
            self.logger.error(f"Error running MCP server: {e}")
            self.logger.debug(f"Exception details: {str(e)}", exc_info=True)
            raise

def run_search_server(host: str, port: int, index: str, username: str = None, password: str = None, 
                   debug: bool = False, embedding_api_token: str = None):
    """
    Run search server with specified parameters.

    Args:
        host: OpenSearch host address
        port: OpenSearch port number
        index: Default index name
        username: Optional username for authentication
        password: Optional password for authentication
        debug: Enable debug logging if True
        embedding_api_token: API token for the embedding service
    """
    logger = setup_logging(debug)
    try:
        logger.debug(f"Initializing server with host={host}, port={port}, index={index}")
        server = SearchMCPServer(
            opensearch_host=host,
            opensearch_port=port,
            index_name=index,
            username=username,
            password=password,
            debug=debug,
            embedding_api_token=embedding_api_token
        )
        server.run()
    except Exception as e:
        logger.error(f"Failed to run OpenSearch MCP server: {e}")
        if debug:
            logger.debug(f"Exception details: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    # Default values
    host = os.environ.get("OPENSEARCH_HOST", "search-demo-phujjhg6osxfiym6fmmddodscq.cn-north-1.es.amazonaws.com.cn")
    port = int(os.environ.get("OPENSEARCH_PORT", "443"))
    index = os.environ.get("OPENSEARCH_INDEX", "default-index")
    username = os.environ.get("OPENSEARCH_USERNAME", "")
    password = os.environ.get("OPENSEARCH_PASSWORD", "")
    debug = os.environ.get("DEBUG", "").lower() in ("true", "1", "yes")
    embedding_api_token = os.environ.get("EMBEDDING_API_TOKEN", "")

    server = SearchMCPServer(
                opensearch_host=host,
                opensearch_port=port,
                index_name=index,
                username=username,
                password=password,
                debug=True,
                embedding_api_token=embedding_api_token
            )
    server.run()

    # Override with command line arguments if provided
    if len(sys.argv) > 1:
        host = sys.argv[1]
    if len(sys.argv) > 2:
        port = int(sys.argv[2])
    if len(sys.argv) > 3:
        index = sys.argv[3]
    if len(sys.argv) > 4:
        username = sys.argv[4]
    if len(sys.argv) > 5:
        password = sys.argv[5]
    
    # Run the server
    run_search_server(host, port, index, username, password, debug)
