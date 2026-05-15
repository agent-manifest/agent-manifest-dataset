# Submit an Agent Manifest

This repository maintains the public dataset of declared Agent Manifests.

Agent manifests can be submitted through GitHub Issues and will be automatically processed.

---

## Submission Process

1. Open a new issue in this repository.
2. Select the Manifest submission template.
3. Paste a valid Agent Manifest v1.0 JSON block into the issue body.
4. Submit the issue.

Once submitted:

- The manifest JSON is extracted automatically.
- The manifest is validated for all required v1.0 fields.
- The manifest is stored at `manifests/YYYY/MM/<agent_id>.json`.
- The registry index (`registry.json`) is rebuilt.

---

## Manifest Requirements

Submissions must conform to Agent Manifest v1.0.

Schema: `https://agent-manifest-spec.org/spec/v1.0/schema.json`

A valid v1.0 manifest must include all 13 required fields:

- `manifest_version` — must be exactly `"1.0"`
- `agent_id` — stable identifier, lowercase, no spaces
- `agent_name` — human-readable name
- `agent_version` — version of the agent (not the manifest)
- `owner` — object with `type` and `identifier`
- `purpose` — object with `primary_code` and `description`
- `forbidden_actions` — non-empty array of explicit prohibitions
- `autonomy` — object with `level` (integer 0–3)
- `risk_profile` — object with `level` (`low`, `medium`, or `high`)
- `data_handling` — object with `stores_personal_data` (boolean)
- `stopping_authority` — object with `stoppable_by` (array) and `mechanism`
- `audit_surface` — object with `logging` and `reconstructability`
- `contact` — object with `email`

---

## Example v1.0 Manifest

```json
{
  "$schema": "https://agent-manifest-spec.org/spec/v1.0/schema.json",
  "manifest_version": "1.0",
  "agent_id": "example-agent",
  "agent_name": "Example Agent",
  "agent_version": "1.0.0",
  "owner": {
    "type": "individual",
    "identifier": "your-name-or-org"
  },
  "purpose": {
    "primary_code": "assistant",
    "description": "Answers questions and routes requests within a defined scope."
  },
  "forbidden_actions": [
    "Access data outside declared scope",
    "Execute code without human review",
    "Retain personal data beyond session"
  ],
  "autonomy": {
    "level": 1
  },
  "risk_profile": {
    "level": "low"
  },
  "data_handling": {
    "stores_personal_data": false
  },
  "stopping_authority": {
    "stoppable_by": ["platform-admin"],
    "mechanism": "Disable via admin panel or API key revocation"
  },
  "audit_surface": {
    "logging": "basic",
    "reconstructability": "partial"
  },
  "contact": {
    "email": "you@example.com"
  }
}
```

---

## Registry

The registry is:

- public
- append-only
- automatically generated
- auditable

Manifests are stored at:

```
manifests/YYYY/MM/<agent_id>.json
```

The registry index (`registry.json`) lists all manifest paths in the dataset.

Historical manifests submitted before v1.0 remain preserved as historical records. New submissions require v1.0 format.

---

## Machine Access

Agents and systems can discover registered agents by reading:

```
registry.json
```

---

## Notes

This repository stores declarations only.

Validation, trust scoring, and compliance checks may be implemented in separate tools such as an Agent Manifest Validator.
