"""CLI validation and retention tests against a temporary copy of real assets."""

import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
ASSETS = Path(__file__).resolve().parents[1] / "StructCodebase"


class EntrypointTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.project = self.root / "project with spaces"
        shutil.copytree(ASSETS, self.project, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo", ".git"))
        self.config = self.project / "config.yaml"
        self.config.write_text("TRAINER:\n  NAME: YamlTrainer\nENV:\n  OUTPUT_DIR: runtime-output\n", encoding="utf-8")

    def run_cli(self, *arguments, isolated=False):
        environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        for key in ("WORLD_SIZE", "LOCAL_RANK", "RANK"):
            environment.pop(key, None)
        command = [sys.executable]
        if isolated:
            command.append("-S")
        command.extend([str(self.project / "main.py"), *arguments])
        return subprocess.run(command, cwd=self.root, env=environment, capture_output=True, text=True)

    def test_help_does_not_require_training_dependencies(self):
        result = self.run_cli("--help", isolated=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--config-file", result.stdout)
        self.assertFalse((self.project / "runtime-output").exists())

    def test_config_precedence_and_safe_defaults_without_training_imports(self):
        result = self.run_cli("--config-file", "config.yaml", "--trainer", "NamedTrainer", "--check-config",
                              "TRAINER.NAME", "FinalTrainer", "TRAIN.MAX_EPOCHS", "3")
        self.assertEqual(result.returncode, 0, result.stderr)
        import yaml
        cfg = yaml.safe_load(result.stdout)
        self.assertEqual(cfg["TRAINER"]["NAME"], "FinalTrainer")
        self.assertEqual(cfg["TRAIN"]["MAX_EPOCHS"], 3)
        self.assertEqual(cfg["TRAIN"]["SAVE_FREQ"], 1)
        self.assertFalse(cfg["ENV"]["USE_WANDB"])
        self.assertEqual(cfg["ENV"]["WANDB"]["ENTITY"], "")
        self.assertFalse((self.project / "runtime-output").exists())
        self.assertFalse(list(self.project.rglob("__pycache__")))

    def test_nonempty_output_is_refused_before_trainer_construction(self):
        output = self.project / "runtime-output"
        output.mkdir()
        keep = output / "keep.txt"
        keep.write_bytes(b"irreplaceable output")
        result = self.run_cli("--config-file", "config.yaml")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Refusing non-empty output", result.stderr)
        self.assertEqual(keep.read_bytes(), b"irreplaceable output")
        self.assertEqual(set(output.iterdir()), {keep})

    def test_explicit_zero_save_frequency_is_rejected_read_only(self):
        result = self.run_cli("--config-file", "config.yaml", "--check-config", "TRAIN.SAVE_FREQ", "0")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("TRAIN.SAVE_FREQ", result.stderr)
        self.assertFalse((self.project / "runtime-output").exists())

    def test_resume_requires_real_checkpoint_artifacts(self):
        result = self.run_cli("--config-file", "config.yaml", "--resume")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("checkpoint pointers", result.stderr)
        self.assertFalse((self.project / "runtime-output").exists())

    def test_test_checkpoint_selection_must_match_config_mode(self):
        result = self.run_cli("--config-file", "config.yaml", "--mode", "test", "--model-dir", "saved", "--load-iter", "1", "--check-config")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--load-iter requires", result.stderr)
        self.assertFalse((self.project / "runtime-output").exists())

    def test_debug_requires_explicit_bound(self):
        result = self.run_cli("--config-file", "config.yaml", "--mode", "debug", "--check-config")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("explicit TRAIN.MAX_EPOCHS", result.stderr)

    def test_missing_registration_module_fails_without_creating_output(self):
        result = self.run_cli("--config-file", "config.yaml", "--module", "no_such_consumer_module", "--check-config")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("no_such_consumer_module", result.stderr)
        self.assertFalse((self.project / "runtime-output").exists())


if __name__ == "__main__":
    unittest.main()
