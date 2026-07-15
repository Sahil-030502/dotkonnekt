from langgraph.graph import StateGraph, START, END

from src.state import AgentState
from src.nodes.parser import parser_node
from src.nodes.chunker import chunker_node
from src.nodes.analyzer import analyzer_node
from src.nodes.mcp import mcp_node
from src.nodes.aggregator import aggregator_node
from src.nodes.report import report_node


# ----------------------------
# Router
# ----------------------------

def chunk_router(state: AgentState):

    total_chunks = len(state["chunks"])
    current_chunk = state["current_chunk"]

    if current_chunk < total_chunks:
        return "analyzer"

    return "aggregator"


# ----------------------------
# Move to Next Chunk
# ----------------------------

def next_chunk(state: AgentState):

    state["current_chunk"] += 1

    return state


# ----------------------------
# Build Graph
# ----------------------------

def build_graph():

    graph = StateGraph(AgentState)

    # Nodes
    graph.add_node("parser", parser_node)
    graph.add_node("chunker", chunker_node)
    graph.add_node("analyzer", analyzer_node)
    graph.add_node("mcp", mcp_node)
    graph.add_node("next_chunk", next_chunk)
    graph.add_node("aggregator", aggregator_node)
    graph.add_node("report", report_node)

    # Edges
    graph.add_edge(START, "parser")
    graph.add_edge("parser", "chunker")

    graph.add_conditional_edges(
        "chunker",
        chunk_router,
        {
            "analyzer": "analyzer",
            "aggregator": "aggregator"
        }
    )

    graph.add_edge("analyzer", "mcp")
    graph.add_edge("mcp", "next_chunk")

    graph.add_conditional_edges(
        "next_chunk",
        chunk_router,
        {
            "analyzer": "analyzer",
            "aggregator": "aggregator"
        }
    )

    graph.add_edge("aggregator", "report")
    graph.add_edge("report", END)

    return graph.compile()


# Module-level compiled agent (for direct import by routes)
agent = build_graph()
