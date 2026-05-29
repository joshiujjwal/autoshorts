# AutoShorts

> Automatically identify the most engaging moments in long-form YouTube videos and generate short clips for TikTok/Reels/Shorts.

![Status](https://img.shields.io/badge/status-🚧_Early_Development-orange)
![Python](https://img.shields.io/badge/python-3.11+-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## What it does

AutoShorts downloads a YouTube video, transcribes it, scores each segment by **emotional intensity** and **knowledge density**, then clips and exports the top moments as vertical 9:16 shorts ready for TikTok, Reels, or YouTube Shorts.

```
YouTube URL → Download → Transcribe → Analyze → Rank → Clip → Export
```

---

## Tech Stack

| Layer | Tool |
|---|---|
| Video download | `yt-dlp` |
| Transcription | `openai-whisper` (local) |
| Emotion / scoring | `transformers` (HuggingFace) + `nltk` |
| Video processing | `ffmpeg-python` |
| CLI | `typer` |
| Config | `pydantic-settings` |
| Testing | `pytest` + `pytest-cov` |
| Linting | `ruff` + `mypy` |

---

## Getting Started

```bash
# Clone
git clone <repo-url>
cd autoshorts

# Create virtual env
python -m venv .venv && source .venv/bin/activate

# Install dependencies
pip install -e ".[dev]"

# Run on a YouTube URL
autoshorts run https://www.youtube.com/watch?v=<VIDEO_ID>
```

### Prerequisites

- Python 3.11+
- `ffmpeg` installed and on `PATH` (`brew install ffmpeg`)
- At least 8 GB RAM (Whisper model)

---

## Project Structure

```
autoshorts/
├── src/
│   ├── downloader/     # yt-dlp wrapper — fetch video + audio
│   ├── transcriber/    # Whisper transcription → timestamped segments
│   ├── analyzer/       # Emotion + knowledge scoring per segment
│   ├── clipper/        # Select top-N segments, apply duration rules
│   └── exporter/       # ffmpeg render → 9:16 crop, captions, branding
├── tests/
│   ├── unit/           # Per-module unit tests with fixtures
│   └── integration/    # End-to-end pipeline tests (uses sample video)
├── docs/
│   ├── spec.md         # Feature specification
│   └── adr/            # Architecture Decision Records
├── .github/
│   ├── copilot-instructions.md
│   └── instructions/
├── README.md
├── TODO.md
├── CLAUDE.md
├── AGENTS.md
└── pyproject.toml      # TODO: create
```

---

## Contributing

1. **Always write tests first** (red → green)
2. Keep PRs small and focused on one concern
3. Include evidence in PR descriptions: test output, sample clip screenshot
4. Run `ruff check . && mypy src/` before opening a PR
5. Never remove or skip existing tests
