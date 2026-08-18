GROUNDING_VALIDATION_PROMPT = """Analyze whether the candidate AI answer is factual and strictly grounded in the provided retrieved context.

RETRIEVED CONTEXT:
{context_text}

CANDIDATE ANSWER:
{candidate_answer}

INSTRUCTIONS:
Determine if every factual claim in the CANDIDATE ANSWER is fully supported by the RETRIEVED CONTEXT.
Respond in JSON format with two fields:
- "grounded": true or false
- "reason": brief string explanation if ungrounded, otherwise "supported"
"""
