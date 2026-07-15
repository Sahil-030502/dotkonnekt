import json
from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters


class MCPClient:
    """
    Async client for the local MCP Risk Analysis Server.

    stdio_client is an async context manager — it must be used with
    `async with` directly. Awaiting it first and then entering it again
    is incorrect and raises a TypeError at runtime.
    """

    def _server_params(self) -> StdioServerParameters:
        return StdioServerParameters(
            command="python",
            args=["-m", "src.mcp.server"]
        )

    @staticmethod
    def _parse_result(result) -> dict:
        """
        MCP CallToolResult.content is a list of TextContent objects.
        Each has a .text attribute containing a JSON string.
        Parse and return the first one as a dict.
        """
        try:
            content_list = result.content
            if content_list:
                text = content_list[0].text
                return json.loads(text)
        except Exception:
            pass
        return {}

    async def lookup_clause(self, clause: str) -> dict:
        async with stdio_client(self._server_params()) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(
                    "lookup_clause",
                    {"clause": clause}
                )
                return self._parse_result(result)

    async def calculate_risk_score(self, matched_terms: list) -> dict:
        async with stdio_client(self._server_params()) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(
                    "calculate_risk_score",
                    {"matched_terms": matched_terms}
                )
                return self._parse_result(result)

    async def suggest_revision(self, clause: str) -> dict:
        async with stdio_client(self._server_params()) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(
                    "suggest_revision",
                    {"clause": clause}
                )
                return self._parse_result(result)
