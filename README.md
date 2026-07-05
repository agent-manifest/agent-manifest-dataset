![Status](https://img.shields.io/badge/status-public%20dataset-1a1917?style=flat-square)
![Schema](https://img.shields.io/badge/schema-v1.0-1a1917?style=flat-square)
![License](https://img.shields.io/badge/license-CC0--1.0-lightgrey?style=flat-square)

# Agent Manifest Dataset

Public dataset of submitted Agent Manifest declarations.

-----

## What this is

A public record of Agent Manifest declarations submitted through the Diplomat registration gateway. The dataset is append-only in normal operation; it underwent a one-time foundational cleanup that removed operational test artifacts and migrated pre-v1.0 declarations to the v1.0 schema.

Each entry is a single JSON file stored at:

```
manifests/YYYY/MM/<agent_id>.json
```

Example:

```
manifests/2026/03/the-diplomat.json
```

The dataset is intended as an audit surface and a research corpus, not as a runtime system.

All recorded manifests conform to the Agent Manifest v1.0 JSON Schema. Declarations that predated the v1.0 schema were migrated to conform to it; new submissions are required to conform to the v1.0 schema.

-----

## What this is not

- Not the normative specification. The spec lives at [agent-manifest-spec.org](https://agent-manifest-spec.org).
- Not a validator. Schema validation happens at submission time inside the Diplomat.
- Not a runtime enforcement layer. The dataset records declarations; it does not constrain behavior.
- Not an adoption claim. Inclusion in the dataset reflects a declaration, not endorsement of the declaring system.

-----

## How to submit

The intended path is the Ambassador generator, which produces a v1.0-compliant `manifest.json` and submits it to the Diplomat registration endpoint on your behalf:

- **Ambassador (generator):** https://agent-manifest.github.io/agent-manifest-ambassador/

For the full submission rules and the manual submission path, see:

- [`SUBMIT.md`](./SUBMIT.md)

-----

## How to consume

The repository's machine-readable index of recorded manifests:

- [`registry.json`](./registry.json) — the index built from `manifests/`

The canonical, host-stable discovery endpoint on the spec site:

- https://agent-manifest-spec.org/.well-known/agent-manifest-registry.json

The discovery endpoint points to this dataset and is the recommended entry point for external consumers.

-----

## Schema

All v1.0 entries conform to the published JSON Schema:

- https://agent-manifest-spec.org/spec/v1.0/schema.json

-----

## Purpose

This dataset provides:

- public transparency of declared agent identities and boundaries
- a historical record of declarations
- an auditable surface for research and governance review
- a research corpus for the study of agent declaration behavior — see [`studies/`](./studies/)

-----

## License

CC0-1.0 (Public Domain Dedication). See [`LICENSE`](./LICENSE).

The dataset license (CC0-1.0) applies to this repository's contents. The Agent Manifest specification itself is licensed CC BY 4.0 and lives in [`agent-manifest/agent-manifest`](https://github.com/agent-manifest/agent-manifest).

---

**Part of the [Agent Manifest](https://agent-manifest-spec.org) ecosystem**

[Spec](https://github.com/agent-manifest/agent-manifest) ·
[Registry](https://github.com/agent-manifest/agent-manifest-registry) ·
[Dataset](https://github.com/agent-manifest/agent-manifest-dataset) ·
[Ambassador](https://github.com/agent-manifest/agent-manifest-ambassador) ·
[Diplomat](https://github.com/agent-manifest/agent-manifest-diplomat) ·
[Boundary Handshake](https://github.com/agent-manifest/boundary-handshake) ·
[∈ Principle](https://github.com/agent-manifest/e-principle)

CC0-1.0
