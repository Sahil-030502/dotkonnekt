import os
import json

from src.library.llm import llm
from src.library.prompts import REPORT_PROMPT
from src.tools.risk_scorer import calculate_risk
from src.tools.trace import create_trace
from src.utils.config import REPORT_DIR, TRACE_DIR


def report_node(state):

    prompt = f"""
{REPORT_PROMPT}

Analysis:

{state["partial_results"]}
"""

    response = llm.invoke(prompt)

    state["final_report"] = {
        "run_id": state["run_id"],
        "risk_score": calculate_risk(state["partial_results"]),
        "successful_chunks": len(state["partial_results"]),
        "failed_chunks": len(state["failed_chunks"]),
        "report": response.content
    }

    state["trace"].append(
        create_trace(
            "Report",
            "report_node",
            "SUCCESS",
            "Final report generated"
        )
    )

    # ---------------------------------
    # Save Report
    # ---------------------------------

    os.makedirs(REPORT_DIR, exist_ok=True)

    report_path = os.path.join(REPORT_DIR, f"{state['run_id']}.json")

    with open(report_path, "w") as file:
        json.dump(state["final_report"], file, indent=4)

    # ---------------------------------
    # Save Trace
    # ---------------------------------

    os.makedirs(TRACE_DIR, exist_ok=True)

    trace_path = os.path.join(TRACE_DIR, f"{state['run_id']}.json")

    with open(trace_path, "w") as file:
        json.dump(state["trace"], file, indent=4)

    return state
