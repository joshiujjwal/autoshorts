# Copilot Instructions — AutoShorts

## Project

AutoShorts is a Python CLI tool that downloads YouTube videos, transcribes them with Whisper, scores segments by emotion and knowledge density, then renders the top clips as 9:16 vertical shorts.

**Stack:** Python 3.11, yt-dlp, openai-whisper, transformers (HuggingFace), ffmpeg-python, typer, pydantic-settings, pytest

---

## Coding Conventions

- Use **dataclasses** for data containers (`Segment`, `Clip`, `SegmentScore`, `VideoMetadata`)
- Use **classes** for service objects (`Downloader`, `Transcriber`, `ClipSelector`, `Renderer`)
- All public functions and methods must have **type annotations**
- `mypy --strict` must pass — no `Any` unless unavoidable and annotated with `# type: ignore[reason]`
- Max line length: **100 characters**
- Use `pathlib.Path` — never `os.path` string manipulation
- Prefer `logging` over `print` in library code; only `typer.echo` in `cli.py`

---

## Testing Conventions

- **Write tests before implementation** — always red before green
- Unit tests live in `tests/unit/` — must mock all external I/O (network, subprocess, model loads)
- Integration tests live in `tests/integration/` — may use real files from `tests/fixtures/`
- Use `pytest-mock` (`mocker` fixture) for mocking
- Test file naming: `test_{module_name}.py`
- Test function naming: `test_{method_name}_{scenario}` (e.g., `test_select_clips_enforces_min_gap`)
- Every edge case in `docs/spec.md` must have a corresponding test

---

## Boundaries

- **Do NOT refactor** existing working code unless explicitly asked
- **Do NOT remove or skip tests** — if a test is wrong, fix the test AND the code
- **Do NOT add new dependencies** without updating `pyproject.toml`
- **Do NOT put business logic in `cli.py`** — it is a thin orchestration layer only
- **Do NOT load models at import time** — lazy-load on first use
- When unsure about an interface, refer to `docs/spec.md` — it is the source of truth

---

## Common Patterns

### Scoring a segment
```python
from autoshorts.analyzer.scorer import score_segment
score = score_segment(segment)  # returns SegmentScore
```

### Running the pipeline
```python
# See src/cli.py for the canonical pipeline order:
# download → transcribe → analyze → clip → export
```

### Mocking yt-dlp in tests
```python
def test_download(mocker):
    mock_ydl = mocker.patch("yt_dlp.YoutubeDL")
    mock_ydl.return_value.__enter__.return_value.extract_info.return_value = {...}
```
