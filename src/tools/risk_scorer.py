import json
import re


def _extract_risk_level(analysis: str) -> str:
    """
    Pull the risk level out of the LLM's JSON analysis string.
    The analyzer prompt asks for {"risk": "HIGH"|"MEDIUM"|"LOW"}.
    Falls back to "LOW" if the field can't be parsed.
    """
    try:
        # Strip markdown code fences if the LLM wrapped the JSON
        clean = re.sub(r"```(?:json)?", "", analysis).strip().rstrip("```").strip()
        data = json.loads(clean)
        return str(data.get("risk", "LOW")).upper()
    except Exception:
        # Plain-text fallback: look for the word anywhere in the response
        upper = analysis.upper()
        if "HIGH" in upper:
            return "HIGH"
        if "MEDIUM" in upper:
            return "MEDIUM"
        return "LOW"


def calculate_risk(results: list) -> float:
    """
    Compute an overall risk score (0–100) from per-chunk analysis results.

    Weights:
      HIGH   → 1.0
      MEDIUM → 0.5
      LOW    → 0.0

    Also factors in the MCP baseline risk_score when available.
    Returns a rounded percentage.
    """
    if not results:
        return 0.0

    weighted_sum = 0.0
    total_weight = 0.0

    for result in results:
        # --- LLM-derived risk level ---
        analysis = result.get("analysis", "")
        level = _extract_risk_level(analysis)

        if level == "HIGH":
            chunk_score = 100.0
        elif level == "MEDIUM":
            chunk_score = 50.0
        else:
            chunk_score = 0.0

        # --- MCP baseline risk score (0–100), blended in if present ---
        baseline = result.get("baseline", {})
        mcp_score = None
        if baseline:
            risk_score_block = baseline.get("risk_score", {})
            if isinstance(risk_score_block, dict):
                mcp_score = risk_score_block.get("risk_score")

        if mcp_score is not None:
            # Average LLM score and MCP score equally
            chunk_score = (chunk_score + float(mcp_score)) / 2.0

        weighted_sum += chunk_score
        total_weight += 1.0

    return round(weighted_sum / total_weight, 2)
