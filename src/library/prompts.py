CLAUSE_PROMPT = """
Extract all important clauses and obligations from the document chunk below.

Return ONLY valid JSON — no markdown, no explanation — with this structure:
{
  "clauses": [
    {"id": 1, "text": "...", "type": "obligation|right|condition|definition|other"}
  ]
}
"""


ENTITY_PROMPT = """
Extract all named entities from the document chunk below.

Return ONLY valid JSON — no markdown, no explanation — with this structure:
{
  "entities": {
    "parties": [],
    "dates": [],
    "amounts": [],
    "locations": [],
    "organizations": []
  }
}
"""


RISK_PROMPT = """
Identify risky or ambiguous clauses in the document chunk below.

Return ONLY valid JSON — no markdown, no explanation — with this structure:
{
  "risk": "HIGH",
  "risky_terms": ["term 1", "term 2"],
  "reason": "brief explanation"
}

Use "HIGH" if there are clearly dangerous or one-sided clauses,
"MEDIUM" if there are ambiguous or potentially unfair terms,
"LOW" if the chunk appears balanced and clear.
"""


REPORT_PROMPT = """
You are a document intelligence assistant reviewing a contract or policy document.

You will be given per-chunk analysis results that include:
- Extracted clauses and obligations
- Named entities (parties, dates, amounts)
- Risk assessments with flagged terms
- MCP baseline risk scores and suggested revisions
- Descriptions of any embedded images (charts, tables, signature blocks)

Generate a comprehensive, structured report with these sections:

1. EXECUTIVE SUMMARY
   - Document type and parties involved
   - Overall risk rating (HIGH / MEDIUM / LOW)
   - Top 3 concerns

2. KEY CLAUSES & OBLIGATIONS
   - List the most important clauses with their risk level

3. NAMED ENTITIES
   - Parties, dates, financial amounts, locations

4. RISK FINDINGS
   - Each risky term with the relevant clause and suggested revision

5. OVERALL RISK SCORE
   - Numeric score 0–100 with brief justification

6. RECOMMENDATIONS
   - Actionable steps before signing or approving

Be concise, professional, and factual. Do not fabricate information not present in the analysis.
"""


QA_PROMPT = """
You are a document intelligence assistant. Answer the question below using ONLY the provided context.

Rules:
- Cite the chunk number for every claim you make, e.g. [Chunk 3]
- If the answer is not in the context, say "This information is not present in the document."
- Do not fabricate or infer beyond what the context states

Question:
{question}

Context:
{context}
"""
