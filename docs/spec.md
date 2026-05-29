# AutoShorts — Feature Specification

> **Status:** Draft — Pre-implementation  
> **Last updated:** 2025-07

---

## Overview

### Problem Statement

Long-form YouTube videos (podcasts, lectures, interviews, tutorials) contain 3–5 genuinely engaging moments that would perform well as short-form clips. Finding those moments manually is time-consuming and requires watching the full video. AutoShorts automates this by analyzing transcript emotion and knowledge density to surface the highest-value segments, then renders them as platform-ready vertical shorts.

### Goals

- Reduce time-to-clip from 2+ hours of manual watching to < 5 minutes of compute
- Produce clips that require zero manual trimming (watch once and post)
- Work fully offline — no cloud APIs required beyond initial video download

### Non-Goals (v0.1)

- No automatic posting to social platforms
- No A/B testing or analytics integration
- No multi-language support (English only for v0.1)
- No scene-cut detection (transcript-boundary clips only)

---

## Functional Requirements

### Core Pipeline

- [ ] **FR-01** Accept a YouTube URL and download the video and separate audio track
- [ ] **FR-02** Transcribe audio to timestamped text segments using Whisper (local, offline)
- [ ] **FR-03** Score each segment on emotional intensity using a pre-trained sentiment/emotion model
- [ ] **FR-04** Score each segment on knowledge density using entity/term heuristics
- [ ] **FR-05** Combine scores into a composite ranking (weighted, configurable)
- [ ] **FR-06** Select top-N clips with minimum spacing and duration constraints
- [ ] **FR-07** Render each clip as a 9:16 (1080×1920) MP4 with burned-in captions
- [ ] **FR-08** Output clips to a configurable directory with structured filenames

### CLI

- [ ] **FR-09** Provide `autoshorts run <url>` as the primary command
- [ ] **FR-10** Provide `autoshorts analyze <video>` to print ranked segments without rendering
- [ ] **FR-11** Support `--dry-run` flag to preview clip selections without rendering
- [ ] **FR-12** Support `--max-clips N` (default: 5) and `--output-dir DIR`
- [ ] **FR-13** Print a summary table at completion

### Configuration

- [ ] **FR-14** All thresholds configurable via `.env` or environment variables
- [ ] **FR-15** Whisper model size configurable (`tiny`, `base`, `small`, `medium`)

---

## Non-Functional Requirements

- [ ] **NFR-01** Process a 60-minute video in under 10 minutes on CPU (base Whisper model)
- [ ] **NFR-02** Output clips must be valid, playable H.264 MP4 files
- [ ] **NFR-03** No API keys required for core pipeline
- [ ] **NFR-04** Test coverage ≥ 80%
- [ ] **NFR-05** `ruff` lint-clean and `mypy` strict-clean

---

## Data Model

```python
@dataclass
class VideoMetadata:
    id: str              # YouTube video ID
    title: str
    duration_s: float    # total duration in seconds
    video_path: Path
    audio_path: Path

@dataclass
class Segment:
    start: float         # seconds from start
    end: float
    text: str

@dataclass
class SegmentScore:
    emotion_score: float    # 0.0 – 1.0
    knowledge_score: float  # 0.0 – 1.0
    composite_score: float  # weighted combination

@dataclass
class RankedSegment:
    segment: Segment
    score: SegmentScore
    rank: int

@dataclass
class Clip:
    start: float
    end: float
    score: float
    title_hint: str    # first 60 chars of highest-scoring sentence
    video_path: Path   # source video
```

---

## Module Interface Design

### `Downloader`

```python
class Downloader:
    def download_video(self, url: str, output_dir: Path) -> VideoMetadata: ...
    def extract_audio(self, video_path: Path) -> Path: ...
```

### `Transcriber`

```python
class Transcriber:
    def transcribe(self, audio_path: Path) -> list[Segment]: ...
    # Caches result as {audio_path}.transcript.json
```

### `Scorer`

```python
def score_segment(segment: Segment) -> SegmentScore: ...
def rank_segments(segments: list[Segment]) -> list[RankedSegment]: ...
```

### `ClipSelector`

```python
class ClipSelector:
    def select_clips(
        self,
        ranked: list[RankedSegment],
        video_duration: float,
        max_clips: int = 5,
    ) -> list[Clip]: ...
```

### `Renderer`

```python
class Renderer:
    def render_clip(
        self,
        video_path: Path,
        clip: Clip,
        output_dir: Path,
        burn_captions: bool = True,
    ) -> Path: ...
```

---

## Emotion Scoring Model

**Model:** `j-hartmann/emotion-english-distilroberta-base`  
**Classes:** anger, disgust, fear, joy, neutral, sadness, surprise

**Excitement Proxy Formula:**

```
emotion_score = (joy * 1.0) + (surprise * 0.9) + (anger * 0.6) - (sadness * 0.3) - (disgust * 0.5)
emotion_score = clamp(emotion_score, 0.0, 1.0)
```

Rationale: Joy and surprise drive shares. Anger is polarizing but engaging. Sadness/disgust reduce virality.

---

## Knowledge Density Heuristic

```
entities = count named entities (PERSON, ORG, GPE, PRODUCT using spaCy or regex)
questions = count question words (what, why, how, when, where)
numbers = count numeric tokens
word_count = len(segment.text.split())

knowledge_score = min(1.0, (entities * 2 + questions * 3 + numbers) / word_count)
```

---

## Clip Selection Rules

| Rule | Default | Config Key |
|---|---|---|
| Min clip duration | 30s | `MIN_CLIP_DURATION` |
| Max clip duration | 90s | `MAX_CLIP_DURATION` |
| Min gap between clips | 30s | `MIN_CLIP_GAP` |
| Max clips returned | 5 | `MAX_CLIPS` |

When a segment is shorter than `MIN_CLIP_DURATION`, expand symmetrically using surrounding segments until duration is met.

---

## Test Plan

### Unit Tests

| Module | Test Cases |
|---|---|
| downloader | URL validation, mock yt-dlp, error handling |
| transcriber | Segment ordering, caching, model lazy-load |
| analyzer | Score bounds (0–1), empty text, batch consistency |
| clipper | Duration rules, gap enforcement, max clips |
| exporter | File naming, ffmpeg call args, caption flag |

### Integration Tests

| Scenario | Input | Expected Output |
|---|---|---|
| Short pipeline | Local 60s test video | ≥1 clip MP4 in output dir |
| Dry run | `--dry-run` flag | No MP4 files, clip table printed |
| Cache hit | Run twice on same file | Second run skips transcription |

### Edge Cases

- Video with no speech (music only) → 0 clips, informative message
- Video shorter than `MIN_CLIP_DURATION` → 1 clip = entire video
- All segments score identically → return first N by time order
- yt-dlp rate-limited → retry 3 times, then `DownloadError`

---

## Open Questions

1. Should we use spaCy for NER or a simpler regex-based entity counter? (spaCy adds 500MB+ to install)
2. Whisper `base` is ~150MB and works on CPU. Should `tiny` be the default to reduce first-run latency?
3. For vertical crop: always center-crop, or use face detection to crop to speaker?
4. Caption font/style — hardcoded or user-configurable?
5. Should transcript caching be per-video-id or per-audio-hash?
