# ADR 0001 — Template

**Status:** Template  
**Date:** YYYY-MM-DD  
**Deciders:** [names]

## Context

What is the issue we're seeing that is motivating this decision?

## Decision

What is the change we're making?

## Consequences

- ✅ Positive consequence
- ⚠️ Trade-off or risk
- ❌ Downside accepted

---

# ADR 0002 — Whisper vs Cloud Transcription

**Status:** Accepted  
**Date:** 2025-07

## Context

AutoShorts needs accurate timestamped transcription. Options:
1. **Local Whisper** (offline, free, CPU/GPU)
2. **OpenAI Whisper API** (cloud, fast, paid per minute)
3. **AssemblyAI / Deepgram** (cloud, fast, paid, better accuracy)

## Decision

Use **local Whisper** (`openai-whisper`) as the default transcription engine.

## Consequences

- ✅ No API key required — works fully offline
- ✅ No ongoing cost regardless of usage
- ✅ Data stays local (privacy-friendly)
- ⚠️ Slower on CPU — `base` model ~1× real-time on modern CPU
- ⚠️ Accuracy lower than cloud services for accented speech
- ❌ Requires 150MB+ model download on first run

Cloud transcription can be added as an optional backend in a future ADR.
