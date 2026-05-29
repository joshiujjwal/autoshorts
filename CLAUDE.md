# CLAUDE.md — AutoShorts

> Context for AI coding agents. Keep this under 200 lines. Update when you learn something new.

---

## Commands

```bash
# Setup
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# Run tests
pytest                          # all tests
pytest tests/unit/              # unit only (fast, no models)
pytest tests/integration/       # requires ffmpeg + sample video
pytest --cov=src --cov-report=term-missing

# Lint & type check
ruff check .
ruff format .
mypy src/

# Run the CLI
autoshorts run <youtube-url>
autoshorts analyze <video-path>
autoshorts run <url> --dry-run --max-clips 3
```

---

## Workflow (Read This First)

1. **Run tests first**: `pytest tests/unit/` — understand what's passing before changing anything
2. **Write failing tests** before implementing any feature (red phase)
3. **Implement** until tests pass (green phase)
4. **Run full lint**: `ruff check . && mypy src/`
5. **Commit** with a descriptive message
6. **Update this file** if you discovered a non-obvious pattern or gotcha

---

## Directory Map

```
src/
  downloader/   # yt-dlp wrapper. VideoMetadata dataclass lives here.
  transcriber/  # Whisper wrapper. Segment dataclass + JSON cache logic.
  analyzer/     # HuggingFace emotion model + knowledge heuristic. RankedSegment here.
  clipper/      # Clip selection logic. Duration/gap enforcement. Clip dataclass.
  exporter/     # ffmpeg-python renderer. 9:16 crop + caption burn-in.
  cli.py        # typer CLI. Only wires modules together — no business logic here.
  config.py     # pydantic-settings Config class. Reads .env.

tests/
  unit/         # Mock all external calls (yt-dlp, whisper, ffmpeg). Fast.
  integration/  # Uses real files in tests/fixtures/. Slow, needs ffmpeg.
  fixtures/     # sample_10s.mp4 — a 10-second test video (committed to repo)

docs/
  spec.md       # Source of truth for data model and module interfaces
  adr/          # Architecture Decision Records
```

---

## Key Conventions

- **All public functions are type-annotated**. `mypy --strict` must pass.
- **Dataclasses for data, classes for services**. Don't put logic in dataclasses.
- **Lazy model loading**: Whisper and HuggingFace models are NOT loaded at import time. Load on first call and cache on the instance.
- **Transcript caching**: Check for `{audio_path}.transcript.json` before running Whisper. Write after transcription. Never re-transcribe.
- **ffmpeg subprocess errors**: Catch `ffmpeg.Error` and re-raise as `RenderError` with the stderr message included.
- **No global state**: Pass config explicitly. No module-level singletons.
- **Test isolation**: Unit tests MUST mock `subprocess`, `yt_dlp.YoutubeDL`, and `whisper.load_model`. Never make real network calls in unit tests.

---

## Gotchas

- `ffmpeg-python` uses a builder pattern — don't call `.run()` inside the builder chain. Build first, then call `.run(quiet=True)`.
- Whisper segments have a `no_speech_prob` field. Filter out segments where `no_speech_prob > 0.8` before scoring.
- yt-dlp `postprocessors` for audio extraction must be set at init time, not per-call.
- HuggingFace models print progress bars to stderr by default. Suppress with `transformers.logging.set_verbosity_error()`.
- The emotion model has a max token length of 512. Truncate long segments before scoring.
- On macOS, ffmpeg from Homebrew may not include libx264 — install with `brew install ffmpeg` (not `--without-extras`).

---

## Environment Variables (`.env`)

```
WHISPER_MODEL_SIZE=base         # tiny | base | small | medium
MAX_CLIPS=5
MIN_CLIP_DURATION=30            # seconds
MAX_CLIP_DURATION=90            # seconds
MIN_CLIP_GAP=30                 # seconds between clips
EMOTION_WEIGHT=0.6
KNOWLEDGE_WEIGHT=0.4
OUTPUT_DIR=./output
MAX_VIDEO_DURATION=10800        # 3 hours in seconds
```

---

## Adding a New Scoring Signal

1. Add the scorer function in `src/analyzer/`
2. Add a field to `SegmentScore`
3. Update the composite formula in `scorer.py::combine_scores()`
4. Update `docs/spec.md` — Data Model + Emotion Scoring sections
5. Write unit tests for the new signal first
