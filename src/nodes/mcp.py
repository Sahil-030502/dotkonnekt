import asyncio

from src.mcp.client import MCPClient
from src.tools.trace import create_trace


def mcp_node(state):
    """
    Run MCP risk tools against the most recently analyzed chunk.
    Results are merged back into partial_results[-1]["baseline"].

    If the MCP server is unavailable, the error is recorded in the
    trace and the node returns gracefully — it does not abort the run.
    """
    client = MCPClient()

    # Only proceed if there's a successfully analyzed chunk to work with
    if not state["partial_results"]:
        return state

    analysis = state["partial_results"][-1]["analysis"]

    try:
        # Each call returns a plain dict (already parsed from TextContent)
        lookup: dict = asyncio.run(client.lookup_clause(analysis))
        matched_terms: list = lookup.get("matched_terms", [])

        score: dict = asyncio.run(client.calculate_risk_score(matched_terms))
        suggestion: dict = asyncio.run(client.suggest_revision(analysis))

        state["partial_results"][-1]["baseline"] = {
            "lookup": lookup,
            "risk_score": score,
            "suggestion": suggestion
        }

        state["trace"].append(
            create_trace(
                "MCP",
                "mcp_node",
                "SUCCESS",
                f"Risk validation completed — {len(matched_terms)} risky terms found"
            )
        )

    except Exception as e:
        # MCP failure is non-fatal: record it and continue
        state["partial_results"][-1]["baseline"] = {}

        state["trace"].append(
            create_trace(
                "MCP",
                "mcp_node",
                "FAILED",
                str(e)
            )
        )

    return state
