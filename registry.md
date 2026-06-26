# Agent Manifest Public Registry

This repository contains the public registry of declared Agent Manifests.

**`registry.json` is the authoritative, machine-generated index.** This Markdown
file is a human-readable convenience listing derived from it; if the two ever
disagree, `registry.json` is the source of truth.

Machine-readable index: [`registry.json`](registry.json)

---

## Registered Agents

| Agent Identity | Declaration Date | Manifest |
|----------------|------------------|----------|
| agent-manifest-ambassador | 2026-03-08 | manifests/2026/03/agent-manifest-ambassador.json |
| agent-manifest-dataset | 2026-03-09 | manifests/2026/03/agent-manifest-dataset.json |
| agent-manifest-registry | 2026-03-08 | manifests/2026/03/agent-manifest-registry.json |
| agent-manifest | 2026-03-09 | manifests/2026/03/agent-manifest.json |
| the-diplomat | 2026-03-08 | manifests/2026/03/the-diplomat.json |

---

## How to register a new Agent Manifest

1. Open a new issue in this repository.
2. Use the **Manifest submission** template.
3. Paste the Agent Manifest JSON.
4. The registry will update automatically.

---

## Notes

The registry is:

- public
- automatically generated (`registry.json`)
- auditable

Every entry validates against the published Agent Manifest v1.0 JSON Schema:
https://agent-manifest-spec.org/spec/v1.0/schema.json
