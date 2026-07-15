from src.tools.trace import create_trace


def aggregator_node(state):

    state["final_report"] = {
        "successful_chunks": len(state["partial_results"]),
        "failed_chunks": len(state["failed_chunks"]),
        "results": state["partial_results"]
    }

    state["trace"].append(
        create_trace(
            "Aggregator",
            "aggregator_node",
            "SUCCESS",
            f'{len(state["partial_results"])} processed | '
            f'{len(state["failed_chunks"])} failed'
        )
    )

    return state
