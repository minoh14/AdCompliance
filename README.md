# AdCompliance

Automated video ad compliance review pipeline powered by [Twelve Labs](https://twelvelabs.io) and [Anthropic Claude](https://www.anthropic.com).

## Overview

AdCompliance takes a folder of `.mp4` files and runs a fully automated, multi-stage review pipeline:

1. **Upload & Index** — Uploads each video to Twelve Labs and indexes it with Marengo 3.0 + Pegasus 1.2
2. **Relevance Check** — Determines whether the video is on-brief for a makeup/cosmetics campaign
3. **Compliance Scan** — Detects policy violations across five categories using both visual and audio signals
4. **Cross-Verification** — Re-evaluates flagged violations against the transcript using Claude to reduce false positives

Each video receives a structured `APPROVE / REVIEW / BLOCK` decision with timestamped evidence.

## Demo

> 📊 [**Live Dashboard**](https://minoh.kr/compliance/analysis_dashboard.html)

---

## Pipeline

```
MP4 files
    │
    ▼
┌──────────┐    ┌──────────┐    ┌─────────────────────────┐    ┌──────────────────┐
│  Upload  │───▶│  Index   │───▶│  Analyze                │───▶│  Cross-Verify    │
│  TL API  │    │  TL API  │    │  Relevance + Compliance │    │  Claude API      │
└──────────┘    └──────────┘    └─────────────────────────┘    │  (if violations) │
                                                               └──────────────────┘
```

All stages run **concurrently** across videos via `asyncio` + `ThreadPoolExecutor`.  
Upload and indexing are **idempotent** — re-running on the same folder skips already-processed assets.

---

## Compliance Categories

| Category               | Description                                          |
| ---------------------- | ---------------------------------------------------- |
| `hate_harassment`      | Hate speech, harassment, discriminatory language     |
| `drugs_illegal`        | Drug use, illegal behaviour, substance abuse         |
| `profanity`            | Explicit language, offensive slurs                   |
| `unsafe_product_usage` | Misleading or unsafe cosmetic application techniques |
| `medical_claims`       | Unsubstantiated medical or cosmetic claims           |

### Decision Rules

| Decision  | Condition                                 |
| --------- | ----------------------------------------- |
| `APPROVE` | No violations, or low-severity only       |
| `REVIEW`  | Any medium-severity violation (no high)   |
| `BLOCK`   | Any high-severity violation, or off-brief |

---

## Setup

### Requirements

- Python 3.10+
- [Twelve Labs API key](https://playground.twelvelabs.io)
- [Anthropic API key](https://console.anthropic.com)

### Install

```bash
git clone https://github.com/minoh14/AdCompliance.git
cd AdCompliance

python -m venv .venv
source .venv/bin/activate

pip install twelvelabs anthropic python-dotenv
```

### Configure

```bash
cp .env.example .env
```

Fill in `.env`:

```env
TL_API_KEY=your_twelve_labs_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
INDEX_NAME=your_index_name
VIDEO_FOLDER_PATH=/path/to/your/videos
MAX_WORKERS=5
```

### Run

```bash
python ad_compliance.py
```

Results are printed as JSON to stdout. To save:

```bash
python ad_compliance.py > results.json
```

---

## Output Format

```json
{
  "filename": "video.mp4",
  "asset_id": "...",
  "indexed_asset_id": "...",
  "campaign_relevance": "ON-BRIEF",
  "relevance_score": 92,
  "video_description": "...",
  "transcription": {
    "spoken": "...",
    "on_screen_text": "..."
  },
  "decision": "REVIEW",
  "decision_reason": "...",
  "violations": [
    {
      "category": "unsafe_product_usage",
      "severity": "medium",
      "timestamp_start": 158.0,
      "timestamp_end": 196.0,
      "evidence": "..."
    }
  ],
  "cross_verification": {
    "verified_violations": [
      {
        "category": "unsafe_product_usage",
        "severity": "medium",
        "verdict": "INSUFFICIENT",
        "reasoning": "..."
      }
    ],
    "overall_assessment": "..."
  }
}
```

---

## Project Structure

```
AdCompliance/
├── ad_compliance.py   # Pipeline entry point
├── prompts.py         # LLM prompt templates
├── .env.example       # Environment variable template
├── .gitignore
├── LICENSE
└── README.md
```

---

## Models

| Model             | Options       | Role                                      |
| ----------------- | ------------- | ----------------------------------------- |
| `pegasus1.2`      | visual, audio | Relevance detection + compliance scanning |
| `claude-opus-4-8` | —             | Cross-verification of flagged violations  |

---

## License

MIT
