"""Regression and adversarial tests for .github/workflows/register-manifest.yml.

The workflow runs on issues anyone can open, with contents: write and
issues: write. These tests run its shell steps for real, in a temporary
directory, the way the runner would: ${{ }} expressions are substituted
as text before the script runs, exactly as GitHub Actions does, so a
script that interpolates outside data into shell is caught here.

The schema validation step is not run (it needs npm and the registry).
Most adversarial cases below are inputs the schema rejects today; they
are fed straight to the later steps on purpose, to show that those steps
stay safe without relying on the schema.
"""

import json
import os
import re
import subprocess
import tempfile
import unittest
from pathlib import Path

import yaml

WORKFLOW = Path(__file__).resolve().parent.parent / ".github" / "workflows" / "register-manifest.yml"
EXPR = re.compile(r"\$\{\{\s*(.*?)\s*\}\}")


def load_workflow(path=WORKFLOW):
    with open(path, encoding="utf-8") as f:
        # PyYAML reads the bare key `on` as True.
        return yaml.safe_load(f)


def steps(workflow):
    return workflow["jobs"]["register"]["steps"]


def step(workflow, name):
    for s in steps(workflow):
        if s.get("name") == name:
            return s
    raise KeyError(name)


class Runner:
    """Runs workflow steps in a scratch checkout and keeps step outputs."""

    def __init__(self, workflow, issue_body, issue_number=7):
        self.workflow = workflow
        self.dir = Path(tempfile.mkdtemp())
        self.home = Path(tempfile.mkdtemp())
        (self.dir / "manifests").mkdir()
        self.outputs = {}
        self.context = {
            "github.event.issue.body": issue_body,
            "github.event.issue.number": str(issue_number),
        }

    def evaluate(self, text):
        def value(match):
            expr = match.group(1)
            m = re.fullmatch(r"steps\.(\w+)\.outputs\.(\w+)", expr)
            if m:
                return self.outputs.get(m.group(1), {}).get(m.group(2), "")
            return self.context[expr]

        return EXPR.sub(value, text)

    def run(self, name):
        s = step(self.workflow, name)
        script = self.evaluate(s["run"])
        out_file = self.dir / f".output-{len(self.outputs)}"
        out_file.write_text("", encoding="utf-8")
        env = {
            "PATH": os.environ["PATH"],
            "HOME": str(self.home),
            "GITHUB_OUTPUT": str(out_file),
        }
        for key, raw in (s.get("env") or {}).items():
            env[key] = self.evaluate(str(raw))
        proc = subprocess.run(
            ["bash", "--noprofile", "--norc", "-eo", "pipefail", "-c", script],
            cwd=self.dir,
            env=env,
            capture_output=True,
            text=True,
        )
        raw_out = out_file.read_text(encoding="utf-8")
        parsed = {}
        for line in raw_out.splitlines():
            if "=" in line:
                k, v = line.split("=", 1)
                parsed[k] = v
        if "id" in s:
            self.outputs[s["id"]] = parsed
        return proc, raw_out

    def files(self):
        return sorted(
            p.relative_to(self.dir).as_posix()
            for p in self.dir.rglob("*")
            if p.is_file() and not p.name.startswith(".output-")
        )


def issue(document):
    text = document if isinstance(document, str) else json.dumps(document)
    return f"## Manifest JSON\n\n```json\n{text}\n```\n"


def submit(agent_id, workflow=None, existing=()):
    """Run the steps from extraction to the move. Returns (runner, results)."""
    r = Runner(workflow or load_workflow(), issue({"manifest_version": "1.0", "agent_id": agent_id}))
    for path in existing:
        target = r.dir / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text('{"agent_id": "already-here"}', encoding="utf-8")
    results = {}
    for name in ("Extract JSON from issue", "Get date", "Get agent ID", "Move manifest"):
        proc, raw = r.run(name)
        results[name] = (proc, raw)
        if proc.returncode != 0:
            break
    return r, results


def ok(results):
    return all(proc.returncode == 0 for proc, _ in results.values()) and "Move manifest" in results


class ExternalDataNeverReachesShellAsCode(unittest.TestCase):
    """Static checks over the workflow text."""

    def test_no_expression_inside_any_script(self):
        for s in steps(load_workflow()):
            for key in ("run",):
                if key in s:
                    self.assertNotIn("${{", s[key], f"step {s.get('name')!r} interpolates into its script")
            script = (s.get("with") or {}).get("script")
            if script is not None:
                self.assertNotIn("${{", script, f"step {s.get('name')!r} interpolates into its script")

    def test_issue_body_only_enters_through_env(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        uses = [line.strip() for line in text.splitlines() if "github.event.issue.body" in line]
        self.assertEqual(uses, ["ISSUE_BODY: ${{ github.event.issue.body }}"])

    def test_trigger_permissions_and_gate_are_unchanged(self):
        wf = load_workflow()
        job = wf["jobs"]["register"]
        self.assertEqual(wf[True], {"issues": {"types": ["opened"]}})
        self.assertEqual(job["permissions"], {"contents": "write", "issues": "write"})
        self.assertEqual(job["if"], "contains(github.event.issue.labels.*.name, 'manifest-submission')")
        self.assertEqual(job["concurrency"], {"group": "registry-sync", "cancel-in-progress": False})

    def test_validation_still_uses_the_shared_validator_before_any_write(self):
        names = [s.get("name") for s in steps(load_workflow())]
        validate = names.index("Validate manifest against the v1.0 schema")
        self.assertIn("@agent-manifest/client@0.1.0", step(load_workflow(), "Install the shared validator")["run"])
        for later in ("Get agent ID", "Move manifest", "Commit the manifest", "Commit the registry index"):
            self.assertGreater(names.index(later), validate, later)


class Registration(unittest.TestCase):
    """Behaviour that must stay as it was."""

    def test_valid_agent_id_is_registered_under_its_lower_case_name(self):
        r, results = submit("Example-Agent.v2_1")
        self.assertTrue(ok(results), results)
        date = r.outputs["date"]
        expected = f"manifests/{date['year']}/{date['month']}/example-agent.v2_1.json"
        self.assertEqual(r.files(), [expected])
        self.assertEqual(json.loads((r.dir / expected).read_text())["agent_id"], "Example-Agent.v2_1")

    def test_manifest_bytes_are_moved_unchanged(self):
        body = '{"manifest_version": "1.0",\n  "agent_id": "byte-check"}'
        r = Runner(load_workflow(), issue(body))
        for name in ("Extract JSON from issue", "Get date", "Get agent ID", "Move manifest"):
            proc, _ = r.run(name)
            self.assertEqual(proc.returncode, 0, proc.stderr)
        (path,) = r.files()
        self.assertEqual((r.dir / path).read_text(encoding="utf-8"), body)

    def test_append_only_rejects_a_registered_agent_id(self):
        existing = "manifests/2026/03/example.json"
        r, results = submit("example", existing=[existing])
        proc, _ = results["Move manifest"]
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("append-only", proc.stdout)
        self.assertEqual(r.files(), ["manifest.json", existing])
        self.assertEqual((r.dir / existing).read_text(), '{"agent_id": "already-here"}')

    def test_append_only_is_case_insensitive_as_before(self):
        existing = "manifests/2026/03/example.json"
        r, results = submit("EXAMPLE", existing=[existing])
        self.assertNotEqual(results["Move manifest"][0].returncode, 0)
        self.assertEqual((r.dir / existing).read_text(), '{"agent_id": "already-here"}')

    def test_agent_ids_that_look_like_echo_options_keep_their_name(self):
        # Valid under the schema. The previous step piped the id through
        # `echo`, which read "-ne" as options, printed nothing, and filed the
        # manifest as manifests/<y>/<m>/.json.
        for agent_id in ("-ne", "-nE", "-eee", "-abc"):
            with self.subTest(agent_id=agent_id):
                r, results = submit(agent_id)
                self.assertTrue(ok(results), results)
                date = r.outputs["date"]
                self.assertEqual(
                    r.files(), [f"manifests/{date['year']}/{date['month']}/{agent_id.lower()}.json"]
                )


class AdversarialAgentId(unittest.TestCase):
    """Inputs that must be refused before anything is written, schema or not."""

    PAYLOADS = [
        'x"; touch PWNED; echo "',
        "$(touch PWNED)",
        "`touch PWNED`",
        "a;touch PWNED",
        "a\nname=evil",
        "a\r\nname=evil",
        "../../PWNED",
        "a/b",
        "*",
        "a[b]",
        "",
        "ünïcode",
        "K-kelvin",  # KELVIN SIGN lower-cases to ASCII "k"
        "a\u0000b",
        123,
        None,
        ["list"],
    ]

    def test_payloads_are_refused_without_side_effects(self):
        for payload in self.PAYLOADS:
            with self.subTest(payload=payload):
                r, results = submit(payload)
                proc, raw = results["Get agent ID"]
                self.assertNotEqual(proc.returncode, 0, f"accepted {payload!r}")
                self.assertNotIn("Move manifest", results)
                self.assertEqual(raw, "", "nothing may be written to GITHUB_OUTPUT")
                self.assertEqual(r.files(), ["manifest.json"])
                self.assertFalse(list(r.dir.rglob("PWNED")))
                self.assertFalse(Path("PWNED").exists())

    def test_issue_body_outside_the_json_block_is_inert(self):
        body = '$(touch PWNED) `touch PWNED` "; touch PWNED; "\n```json\n{"agent_id": "inert"}\n```\n'
        r = Runner(load_workflow(), body)
        for name in ("Extract JSON from issue", "Get date", "Get agent ID", "Move manifest"):
            proc, _ = r.run(name)
            self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertFalse(list(r.dir.rglob("PWNED")))


if __name__ == "__main__":
    unittest.main()
