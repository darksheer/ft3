import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


class CIRevisionTests(unittest.TestCase):
    def test_revision_log_retains_parents_in_shallow_checkout(self):
        workflow = yaml.safe_load((ROOT / ".github/workflows/catalog.yml").read_text())
        script = next(step["run"] for step in workflow["jobs"]["validate"]["steps"]
                      if step.get("name") == "Record tested revision")
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "source"
            shallow = Path(temp) / "shallow"
            source.mkdir()

            def git(*args):
                return subprocess.check_output(["git", *args], cwd=source, text=True).strip()

            git("init", "-q", "-b", "main")
            for value in ("base", "head"):
                (source / "record").write_text(value)
                git("add", "record")
                git("-c", "user.name=Test", "-c", "user.email=test@example.invalid",
                    "-c", "core.hooksPath=/dev/null", "commit", "-q", "-m", value)
                if value == "base":
                    base = git("rev-parse", "HEAD")
            head = git("rev-parse", "HEAD")
            subprocess.run(["git", "clone", "-q", "--depth", "1", source.as_uri(), str(shallow)], check=True)
            environment = os.environ.copy()
            environment.update(CI_EVENT="pull_request", CI_EVENT_SHA=head,
                               CI_HEAD_SHA=head, CI_BASE_SHA=base)
            result = subprocess.run(["bash", "-e", "-c", script], cwd=shallow,
                                    env=environment, check=True, capture_output=True, text=True)
            receipt = json.loads(result.stdout)
            self.assertEqual(receipt["checkout_sha"], head)
            self.assertEqual(receipt["checkout_parents"], [base])
            self.assertEqual(receipt["base_sha"], base)
