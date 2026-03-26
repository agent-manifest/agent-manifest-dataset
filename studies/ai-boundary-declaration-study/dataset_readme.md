# Dataset Description — AI Boundary Declaration Study

## Overview

This dataset contains raw responses from six AI systems collected under two experimental conditions designed to evaluate boundary awareness and epistemic limits.

Models included:
- Claude
- ChatGPT
- Gemini
- Grok
- Copilot
- Meta AI

## Experimental Design

The study is structured in two phases:

### Phase 1 — Spontaneous Self-Description
Models were prompted to describe their capabilities and limitations without explicit instruction to define boundaries.

### Phase 2 — Forced Boundary Declaration
Models were explicitly instructed to define:
- what they will not do
- when they should stop
- when to defer
- which outputs may be unreliable

## Data Collection Conditions

- Interfaces: consumer-facing interfaces (web/mobile)
- Sessions: stateless (no prior context)
- No system prompt modification
- Single prompt per condition per model

## File Structure

- `/phase1/` → spontaneous responses
- `/phase2/` → forced boundary declarations

Each file corresponds to a single model.

## Notes

- Responses are presented as raw text without post-processing
- Minor formatting differences reflect interface behavior
- This dataset is intended for qualitative and comparative analysis

## Related Work

Paper:
https://doi.org/10.5281/zenodo.19235116

Dataset:
https://doi.org/10.5281/zenodo.19235488

## License

CC BY 4.0
