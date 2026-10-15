"""Non-destructive initializer boundaries, using only temporary destinations."""

import importlib.util
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
SKILL = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("framework_bootstrap", SKILL / "scripts" / "bootstrap.py")
bootstrap = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bootstrap)


class BootstrapTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.destination = self.root / "project"

    def test_dry_run_does_not_create_destination_or_include_caches(self):
        plan = bootstrap.build_plan(self.destination)
        self.assertEqual(plan["action"], "copy")
        self.assertFalse(self.destination.exists())
        self.assertTrue(plan["files"])
        self.assertTrue(all("__pycache__" not in item and not item.endswith((".pyc", ".pyo")) for item in plan["files"]))

    def test_docs_survive_apply_and_customized_framework_is_reused(self):
        self.destination.mkdir()
        document = self.destination / "PAPER_PLAN.md"
        document.write_bytes(b"user research plan\n")
        result = bootstrap.apply_plan(bootstrap.build_plan(self.destination))
        self.assertTrue(result["applied"])
        self.assertEqual(document.read_bytes(), b"user research plan\n")
        main = self.destination / "main.py"
        main.write_bytes(b"# user customized entrypoint\n")
        plan = bootstrap.build_plan(self.destination)
        self.assertEqual(plan["action"], "reuse")
        self.assertEqual(bootstrap.apply_plan(plan)["copied"], 0)
        self.assertEqual(main.read_bytes(), b"# user customized entrypoint\n")

    def test_unrelated_app_and_partial_framework_are_refused_unchanged(self):
        self.destination.mkdir()
        application = self.destination / "app.py"
        application.write_bytes(b"user application\n")
        with self.assertRaisesRegex(ValueError, "unrelated application|partial"):
            bootstrap.build_plan(self.destination)
        self.assertEqual(application.read_bytes(), b"user application\n")
        application.unlink()
        (self.destination / "base").mkdir()
        (self.destination / "base" / "base_config.py").write_bytes(b"user config\n")
        with self.assertRaisesRegex(ValueError, "partial"):
            bootstrap.build_plan(self.destination)
        self.assertEqual((self.destination / "base" / "base_config.py").read_bytes(), b"user config\n")

    def test_failed_copy_rolls_back_created_paths_but_keeps_docs(self):
        self.destination.mkdir()
        document = self.destination / "notes.md"
        document.write_bytes(b"keep me")
        original_copy = shutil.copyfileobj
        calls = 0

        def failing_copy(source, target, *args, **kwargs):
            nonlocal calls
            calls += 1
            if calls == 2:
                target.write(b"partial")
                raise OSError("injected copy failure")
            return original_copy(source, target, *args, **kwargs)

        with patch.object(bootstrap.shutil, "copyfileobj", side_effect=failing_copy):
            with self.assertRaisesRegex(ValueError, "rolled back"):
                bootstrap.apply_plan(bootstrap.build_plan(self.destination))
        self.assertEqual(document.read_bytes(), b"keep me")
        self.assertEqual(set(self.destination.iterdir()), {document})

    def test_self_and_traversal_destinations_are_refused(self):
        with self.assertRaisesRegex(ValueError, "overlap"):
            bootstrap.build_plan(bootstrap.SKILL_ROOT / "nested-project")
        with self.assertRaisesRegex(ValueError, "traversal"):
            bootstrap.build_plan(self.root / "nested" / ".." / "project")

    def test_symlink_destination_is_refused(self):
        target = self.root / "real"
        target.mkdir()
        try:
            self.destination.symlink_to(target, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("Creating symlinks is not permitted on this platform")
        with self.assertRaisesRegex(ValueError, "Symlink"):
            bootstrap.build_plan(self.destination)
        self.assertEqual(list(target.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
