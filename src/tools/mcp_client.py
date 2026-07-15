from mcp import ClientSession


class MCPClient:

    def __init__(self):
        self.session = None

    async def connect(self):
        """
        Connect to the MCP server.
        """
        pass

    async def call_tool(self, tool_name, arguments):
        """
        Invoke an MCP tool.

        This will be implemented once the MCP server is configured.
        """
        pass