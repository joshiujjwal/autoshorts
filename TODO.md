# AutoShorts — Task Breakdown

## How to Use This File

Work one task at a time:
1. Write failing tests FIRST (red phase)
2. Implement until tests pass (green phase)
3. Manually review the diff
4. Commit with a descriptive message
5. Update `CLAUDE.md` / `AGENTS.md` with anything you learned (compound loop)

Each phase is an **evidence gate** — do NOT advance to the next phase until all tasks are checked and tests pass.

---

## Phase 0: Foundation ⬜

- [ ] Create `pyproject.toml` with dependencies: `yt-dlp`, `openai-whisper`, `transformers`, `ffmpeg-python`, `typer`, `pydantic-settings`, `torch`
- [ ] Add dev extras: `pytest`, `pytest-cov`, `ruff`, `mypy`, `pytest-mock`
- [ ] Configure `ruff` (line-length 100, target py311) and `mypy` (strict mode) in `pyproject.toml`
- [ ] Write first smoke test `tests/unit/test_smoke.py` — just asserts `True` to validate the test runner works
- [ ] Create `.env.example` with configurable fields (`WHISPER_MODEL_SIZE`, `OUTPUT_DIR`, `MAX_CLIP_DURATION`)
- [ ] Add GitHub Actions CI: `.github/workflows/ci.yml` — lint, type-check, test on push/PR
- [ ] Review `CLAUDE.md`, `AGENTS.md`, `copilot-instructions.md` and update any wrong commands

**Evidence gate:** `pytest` passes, `ruff check .` clean, `mypy src/` clean.

---

## Phase 1: Downloader Module ⬜

- [ ] Write unit tests for `src/downloader/downloader.py`:
  - Test URL validation (valid YT URL, invalid URL, live stream rejection)
  - Test download returns expected file paths (mock `yt-dlp`)
  - Test audio-only extraction option
- [ ] Implement `Downloader` class using `yt-dlp` programmatic API
  - `download_video(url, output_dir) -> VideoMetadata`
  - `extract_audio(video_path) -> Path`
  - Returns `VideoMetadata(id, title, duration_s, video_path, audio_path)`
- [ ] Reject videos longer than configurable max duration (default: 3 hours)
- [ ] Handle yt-dlp errors gracefully with typed exceptions (`DownloadError`, `UnsupportedURLError`)

**Evidence gate:** All downloader unit tests pass. Manually test on one real YT URL.

---

## Phase 2: Transcriber Module ⬜

- [ ] Write unit tests for `src/transcriber/transcriber.py`:
  - Test transcription returns `list[Segment]` with `start`, `end`, `text` fields
  - Test model loading is lazy (not loaded until first call)
  - Test segments are non-overlapping and ordered by start time
  - Mock Whisper to avoid loading model in unit tests
- [ ] Implement `Transcriber` class wrapping `openai-whisper`
  - `transcribe(audio_path) -> list[Segment]`
  - Configurable model size via `WHISPER_MODEL_SIZE` env var (default: `base`)
  - Each `Segment` has: `start: float`, `end: float`, `text: str`
- [ ] Cache transcription results to JSON alongside audio file (skip re-transcription)

**Evidence gate:** Unit tests pass. Run on a real audio file and inspect segment output.

---

## Phase 3: Analyzer Module ⬜

- [ ] Write unit tests for `src/analyzer/scorer.py`:
  - Test `score_segment` returns a `SegmentScore` with `emotion_score`, `knowledge_score`, `composite_score`
  - Test composite score is weighted sum (configurable weights)
  - Test handles empty/whitespace text gracefully (score = 0.0)
  - Test batch scoring returns same count as input segments
- [ ] Implement emotion scoring using HuggingFace `j-hartmann/emotion-english-distilroberta-base`
  - Map emotions to excitement proxy: `joy` + `surprise` + `anger` → high score; `sadness` + `fear` → lower
- [ ] Implement knowledge density scoring using keyword/entity density heuristic:
  - Count named entities (spaCy or simple regex), technical terms, question words
  - Normalize by word count
- [ ] Combine scores: `composite = 0.6 * emotion + 0.4 * knowledge` (configurable weights)
- [ ] Expose `rank_segments(segments: list[Segment]) -> list[RankedSegment]` sorted descending by composite

**Evidence gate:** Unit tests pass. Run analyzer on a real transcript and inspect top-10 ranked segments.

---

## Phase 4: Clipper Module ⬜

- [ ] Write unit tests for `src/clipper/clipper.py`:
  - Test `select_clips` returns at most `max_clips` segments
  - Test minimum gap enforcement between clips (no two clips start within 30s of each other)
  - Test clips are expanded to `min_duration` if too short (default: 30s)
  - Test clips are clamped to `max_duration` (default: 90s)
  - Test no clip exceeds video duration
- [ ] Implement `ClipSelector`:
  - `select_clips(ranked: list[RankedSegment], video_duration: float) -> list[Clip]`
  - Enforce configurable min/max duration, min gap between clips, max clips returned
- [ ] Each `Clip` has: `start: float`, `end: float`, `score: float`, `title_hint: str`
- [ ] Generate a `title_hint` from the highest-scoring sentence in the segment (first 60 chars)

**Evidence gate:** Unit tests pass. Print selected clips from a real video's segments and verify they make intuitive sense.

---

## Phase 5: Exporter Module ⬜

- [ ] Write unit tests for `src/exporter/renderer.py`:
  - Test output file naming convention `{video_id}_clip_{n:02d}.mp4`
  - Test 9:16 crop logic for landscape input (center crop to vertical)
  - Test captions are burned in when `burn_captions=True`
  - Mock ffmpeg subprocess to avoid needing actual video in unit tests
- [ ] Implement `Renderer` using `ffmpeg-python`:
  - `render_clip(video_path, clip, output_dir, burn_captions=True) -> Path`
  - Crop to 1080x1920 (9:16) — center crop landscape video
  - Burn in subtitles from transcript text using `drawtext` filter
  - Output as H.264 MP4 with AAC audio
- [ ] Add progress bar via `tqdm` for batch renders
- [ ] Write integration test using a 10-second sample video fixture

**Evidence gate:** Unit tests pass. Render at least 2 clips from a real video and visually verify quality.

---

## Phase 6: CLI & Pipeline Wiring ⬜

- [ ] Write integration test `tests/integration/test_pipeline.py`:
  - Test end-to-end with a pre-downloaded short test video (< 60s)
  - Assert output directory contains at least 1 `.mp4` file
  - Assert all output clips are valid video files (check with ffprobe)
- [ ] Implement CLI in `src/cli.py` using `typer`:
  - `autoshorts run <url> [--max-clips N] [--output-dir DIR] [--model-size tiny|base|small]`
  - `autoshorts analyze <video-path>` — transcribe + score only, print ranked segments
  - `autoshorts version`
- [ ] Wire full pipeline: download → transcribe → analyze → clip → export
- [ ] Add `--dry-run` flag that prints selected clips without rendering
- [ ] Print summary table at end: clip index, time range, score, output path

**Evidence gate:** Integration test passes. Run `autoshorts run <real-url>` end-to-end and produce at least 3 clips.

---

## Phase 7: Polish & Harden ⬜

- [ ] Add retry logic with exponential backoff for download failures
- [ ] Validate ffmpeg is installed at startup, print helpful error if not
- [ ] Add `--verbose` / `--quiet` flags
- [ ] Write `docs/adr/0002-whisper-vs-cloud-transcription.md` (offline vs API tradeoff)
- [ ] Add `pytest-cov` coverage report — target 80%+ coverage
- [ ] Update README with real screenshots/GIF of output clips

---

## Phase 8: Ship ⬜

- [ ] Tag `v0.1.0`
- [ ] Write `CHANGELOG.md`
- [ ] Publish to PyPI (optional) or document manual install
- [ ] Write `docs/demo.md` with 3 example outputs (before/after video links)

---

## Parking Lot 🅿️

- Scene detection via `PySceneDetect` as alternative clip boundary method
- Audio energy spike detection as signal (loud audience, music drop)
- Web UI (FastAPI + HTMX) for non-CLI users
- Batch mode: process a YouTube playlist
- Custom branding overlay (logo, handle watermark)
- GPT-4o vision to score visual dynamism of frames

---

## Lessons Learned 📝

<!-- Update this as you build — patterns, gotchas, model performance notes -->
