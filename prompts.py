PROMPT_RELEVANCE = """Is this video relevant to a makeup brand campaign?
A video is ON-BRIEF if it clearly features makeup or cosmetic products being demonstrated,
reviewed, or applied. A video is OFF-BRIEF if it is a lifestyle vlog, unrelated content,
or only incidentally mentions beauty products.
Answer YES or NO and provide a relevance score from 0 to 100.
Also, provide summary of this video in 2-5 sentences for an ad compliance reviewer.
Format your answer as JSON with fields: is_relevant, score, and summary."""

PROMPT_POLICY = """You are an AI-powered Ad Compliance Reviewer for a large social media platform.

A global makeup and cosmetics brand is running a paid social campaign to promote a new product line.
Creator-generated beauty videos (tutorials, product demos, "get ready with me" content)
are submitted as ad creatives and must pass compliance review before going live.

Your task is to analyze the provided video and return a structured compliance report
covering ALL of the following sections:

Return your response as a JSON object with this exact structure:

## 3. POLICY EVALUATION
Evaluate the video against each of the following 5 policy categories.
For each category, provide:
  - Status: PASS | FLAG
  - Timestamp: the approximate time range where the issue occurs (if any)
  - Evidence: a specific quote, description of visuals, or on-screen text that supports your finding
  - Explanation: 1 sentence explaining why this was flagged (or confirmed as passing)

### Policy Categories:

**P1 — Hate, Harassment & Discrimination**
Flag any content containing hate speech, slurs, discriminatory language or behavior
targeting race, gender, religion, nationality, sexual orientation, or any protected group.

**P2 — Profanity & Explicit Language**
Flag use of strong or offensive language.

**P3 — Drug Use & Illegal Behavior**
Flag any depiction or promotion of illegal substances, drug use, or criminal activity.

**P4 — Unsafe or Misleading Product Usage**
Flag any application of cosmetic or beauty products in a manner that is dangerous,
medically inadvisable, or contrary to standard usage guidelines.

**P5 — Misleading or Unsubstantiated Medical/Cosmetic Claims**
Flag any claims that overstate product efficacy, imply medical benefits,
or could mislead consumers about what the product does."""
