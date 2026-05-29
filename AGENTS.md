# AGENTS.md — AutoShorts

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

**System requirement:** `ffmpeg` must be on PATH.  
```bash
# macOS
brew install ffmpeg
# Ubuntu
sudo apt install ffmpeg
```

---

## Running Tests

```bash
pytest tests/unit/              # fast, no models, no network
pytest tests/integration/       # requires ffmpeg and tests/fixtures/sample_10s.mp4
pytest --cov=src --cov-report=term-missing   # coverage report
```

**TDD rule:** Write tests FIRST. Never implement before a failing test exists.

---

## Code Style

- **Python 3.11+** — use `match`, `Self`, `TypeAlias` where appropriate
- **Type annotations everywhere** — `mypy --strict` must pass
- **Dataclasses** for data transfer objects (`Segment`, `Clip`, `SegmentScore`, etc.)
- **Classes** for services (`Downloader`, `Transcriber`, `ClipSelector`, `Renderer`)
- **No business logic in `cli.py`** — it only orchestrates module calls
- **No global state** — inject config via constructor or function parameter
- Line length: 100 characters (`ruff` enforced)

---

## Linting

```bash
ruff check .        # lint
ruff format .       # format
mypy src/           # type check (strict mode)
```

CI will fail if any of these fail. Fix before pushing.

---

## Module Responsibilities

| Module | Owns | Does NOT own |
|---|---|---|
| `downloader` | Video/audio fetch, `VideoMetadata` | Transcription |
| `transcriber` | Whisper calls, `Segment` list, JSON cache | Scoring |
| `analyzer` | Emotion + knowledge scoring, `RankedSegment` | Clip selection |
| `clipper` | Duration/gap rules, `Clip` selection | Rendering |
| `exporter` | ffmpeg rendering, 9:16 crop, captions | Scoring |
| `cli` | Argument parsing, pipeline wiring | Business logic |

---

## PR Instructions

Every PR must include:

1. **Test output**: paste `pytest` result showing all tests pass
2. **Coverage diff**: does coverage stay ≥ 80%?
3. **Lint output**: `ruff check .` and `mypy src/` both clean
4. **Evidence**: for exporter PRs, attach a screenshot or ffprobe output of a generated clip
5. **Description**: what does this PR do and why? Don't just describe *what* — explain *why*

**Never:**
- Skip or delete existing tests
- Merge with failing CI
- Add dependencies without updating `pyproject.toml`

---

## Adding a Dependency

1. Add to `pyproject.toml` under `[project.dependencies]`
2. Update `.github/workflows/ci.yml` cache key if needed
3. Document any system-level requirements in README Prerequisites
4. Note any model download sizes in `CLAUDE.md` Gotchas
