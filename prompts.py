# Each prompt must be 500 tokens or less.

PROMPT_RELEVANCE = """You are a compliance reviewer evaluating whether a video is relevant to a makeup brand campaign.

A video is RELEVANT if it:
- Clearly features makeup or cosmetic products being demonstrated, applied, or reviewed
- Has the product/campaign as the primary or significant focus

A video is NOT RELEVANT if it:
- Is a lifestyle vlog where makeup appears only incidentally
- Does not feature cosmetic products at all
- Only mentions beauty products verbally without visual focus

Evaluate the video and respond with a JSON object using exactly these fields:

{
  "is_relevant": "YES" or "NO",
  "score": integer from 0 to 100 where:
    0-20 = no cosmetic content visible,
    21-50 = incidental mention or brief appearance only,
    51-79 = noticeable focus but mixed with unrelated content,
    80-100 = clear primary focus on makeup/cosmetic product demonstration,
  "summary": "2 to 5 sentence summary for an ad compliance reviewer, describing what products appear, how they are used, and the overall context of the video.",
  "transcription": {
    "spoken": "Full verbatim transcription of all spoken dialogue and narration.",
    "on_screen_text": "All on-screen text visible in the video, listed in order of appearance and joined into a single string separated by a single whitespace character. Do not use arrays, newlines, or any other delimiter."
  }
}

Return only the JSON object. Do not include any explanation or text outside the JSON."""

PROMPT_COMPLIANCE_1 = "hate, harassment, or discriminatory language"
PROMPT_COMPLIANCE_2 = "drug use or illegal behavior"
PROMPT_COMPLIANCE_3 = "profanity"
PROMPT_COMPLIANCE_4 = "misleading or unsafe makeup product usage (e.g. eye-area misuse, harmful claims)"
