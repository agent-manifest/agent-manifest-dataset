#!/usr/bin/env python3
"""Generate registry.json from what is in the repository.

Run from the repository root:

    python3 scripts/generate-registry.py

Every value it writes is derived from files that are already committed, so
running it twice on the same commit produces the same file except for
``generated_at``. Nothing is invented: a field that cannot be derived is left
out rather than filled in with a plausible value.

Two fields deserve a note, because getting either wrong would make the registry
a witness to something it did not see.

``registered_at`` is the moment **the registry incorporated** a manifest, taken
from the git commit that added the file. It is deliberately not the manifest's
own ``declaration_date``, which is what the operator asserted. Where the file is
not yet committed, the field is omitted.

``index`` is an array, not an object keyed by ``agent_id``. No document in this
ecosystem declares ``agent_id`` unique — the schema pattern is
``^[a-zA-Z0-9._-]+$``, with no namespace and no issuing authority — so a lookup
by id can legitimately return more than one entry, and the shape has to be able
to say so instead of silently picking one.
"""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

REGISTRY_VERSION = "1.1"
BASE_URL = "https://raw.githubusercontent.com/agent-manifest/agent-manifest-dataset/main/"
SOURCE = "https://github.com/agent-manifest/agent-manifest-dataset"
MANIFESTS_DIR = Path("manifests")
OUTPUT = Path("registry.json")


def manifest_paths() -> list[str]:
    """Every manifest in the dataset, in a stable order."""
    return sorted(p.as_posix() for p in MANIFESTS_DIR.rglob("*.json"))


def added_at(path: str) -> str | None:
    """The author date of the commit that added ``path``, or None.

    Returns None for a file that is not committed yet. The caller omits the
    field in that case; the next run fills it in from history.
    """
    try:
        out = subprocess.run(
            ["git", "log", "--diff-filter=A", "--follow", "--format=%aI", "--", path],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.split()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    return out[-1] if out else None


def agent_id_of(path: str) -> str | None:
    """The ``agent_id`` a manifest declares, or None if it declares none."""
    try:
        with open(path, encoding="utf-8") as handle:
            document = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return None
    value = document.get("agent_id")
    return value if isinstance(value, str) else None


def build() -> dict:
    paths = manifest_paths()

    index = []
    for path in paths:
        agent_id = agent_id_of(path)
        if agent_id is None:
            # A file that declares no agent_id cannot be indexed by one. It stays
            # in `agents`, where it is still reachable by path.
            continue
        entry = {
            "agent_id": agent_id,
            "manifest_path": path,
            "manifest_url": BASE_URL + path,
        }
        registered = added_at(path)
        if registered is not None:
            entry["registered_at"] = registered
        entry["source"] = SOURCE
        index.append(entry)

    index.sort(key=lambda entry: (entry["agent_id"], entry["manifest_path"]))

    return {
        "registry_version": REGISTRY_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "base_url": BASE_URL,
        "agents": paths,
        "index": index,
    }


def main() -> None:
    registry = build()
    with open(OUTPUT, "w", encoding="utf-8") as handle:
        json.dump(registry, handle, indent=2)
        handle.write("\n")
    missing = [e["agent_id"] for e in registry["index"] if "registered_at" not in e]
    print(f"{OUTPUT}: {len(registry['agents'])} manifests, {len(registry['index'])} indexed")
    if missing:
        print(f"  registered_at omitted (not committed yet): {', '.join(missing)}")


if __name__ == "__main__":
    main()
