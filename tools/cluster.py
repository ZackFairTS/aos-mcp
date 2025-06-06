from typing import Dict

from mcp.server.fastmcp import FastMCP

class ClusterTools:
    def __init__(self, aos_client):
        self.aos_client = aos_client

    def register_tools(self, mcp: FastMCP):
        @mcp.tool()
        def get_cluster_health() -> Dict:
            """Returns basic information about the health of the cluster."""
            return self.aos_client.get_client().cluster.health()

        @mcp.tool()
        def get_cluster_stats() -> Dict:
            """Returns high-level overview of cluster statistics."""
            return self.aos_client.get_client().cluster.stats()