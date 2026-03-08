# Submit an Agent Manifest

This repository maintains the public registry of declared Agent Manifests.

Agent manifests can be submitted through GitHub Issues and will be automatically processed.

---

## Submission Process

1. Open a new issue in this repository.
2. Select the Manifest submission template.
3. Provide the agent identity and manifest JSON.
4. Submit the issue.

Once submitted:

- The manifest JSON is extracted automatically.
- The manifest is validated for required fields.
- The manifest is stored in the dataset.
- The global registry (registry.json) is rebuilt.

---

## Manifest Requirements

A valid manifest must include the following fields:

- $schema
- specVersion
- identity
- purpose
- capabilities
- boundaries
- autonomy_level
- declaration_date

Example structure:

{
  "$schema": "https://agent-manifest-spec.org/schema/v1/manifest.schema.json",
  "specVersion": "1.0.0",
  "identity": "example-agent",
  "purpose": "Describe the agent purpose",
  "capabilities": ["analysis"],
  "boundaries": ["read-only"],
  "autonomy_level": "supervised",
  "declaration_date": "2026-03-08"
}

---

## Registry Properties

The registry is:

- public
- append-only
- automatically generated
- auditable

All submitted manifests remain permanently recorded in the dataset.

---

## Machine Access

Agents and systems can discover registered agents by reading:

registry.json

Each registry entry includes:

- agent identity
- declaration date
- manifest path
- manifest URL

---

## Notes

This repository stores declarations only.

Validation, trust scoring, and compliance checks may be implemented in separate tools such as an Agent Manifest Validator.
