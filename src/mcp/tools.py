from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Risk Analysis Server")


RISKY_TERMS = [
    "unlimited liability",
    "automatic renewal",
    "exclusive jurisdiction",
    "no termination",
    "sole discretion",
    "without notice",
    "non-refundable",
    "perpetual license"
]


# ----------------------------------------------------
# Tool 1 : Clause Lookup
# ----------------------------------------------------

@mcp.tool()
def lookup_clause(clause: str):
    """
    Check whether a clause contains risky terms.
    """

    clause = clause.lower()

    found = []

    for term in RISKY_TERMS:
        if term in clause:
            found.append(term)

    return {
        "matched_terms": found,
        "risk": "HIGH" if found else "LOW"
    }


# ----------------------------------------------------
# Tool 2 : Risk Score
# ----------------------------------------------------

@mcp.tool()
def calculate_risk_score(matched_terms: list):
    """
    Calculate risk score based on number of risky terms.
    """

    count = len(matched_terms)

    if count == 0:
        score = 10

    elif count <= 2:
        score = 40

    elif count <= 4:
        score = 70

    else:
        score = 95

    return {
        "risk_score": score
    }


# ----------------------------------------------------
# Tool 3 : Suggest Revision
# ----------------------------------------------------

@mcp.tool()
def suggest_revision(clause: str):
    """
    Suggest safer wording for risky clauses.
    """

    suggestions = []

    text = clause.lower()

    if "unlimited liability" in text:
        suggestions.append(
            "Replace 'unlimited liability' with 'liability limited to the contract value'."
        )

    if "automatic renewal" in text:
        suggestions.append(
            "Add an option for either party to opt out before renewal."
        )

    if "exclusive jurisdiction" in text:
        suggestions.append(
            "Consider allowing mutually agreed jurisdiction."
        )

    if "without notice" in text:
        suggestions.append(
            "Require reasonable prior written notice."
        )

    if "sole discretion" in text:
        suggestions.append(
            "Define objective criteria instead of sole discretion."
        )

    if "non-refundable" in text:
        suggestions.append(
            "Allow refunds under defined conditions."
        )

    if not suggestions:
        suggestions.append(
            "No risky wording detected."
        )

    return {
        "recommendations": suggestions
    }