"""Plan or explicitly copy the bundled framework without replacing user files."""

import argparse
import json
import os
from pathlib import Path
import shutil
import stat
import sys

sys.dont_write_bytecode = True
SKILL_ROOT = Path(__file__).resolve().parents[1]
SOURCE = SKILL_ROOT / "StructCodebase"
IGNORED_DIRS = {"__pycache__", ".git"}
DOC_DIRS = {"docs", "doc", "notes", "papers", "reports", "figures"}
DOC_SUFFIXES = {".md", ".markdown", ".rst", ".txt", ".pdf", ".tex", ".bib"}
FIGURE_SUFFIXES = {".png", ".jpg", ".jpeg", ".svg", ".eps"}
VCS_FILES = {".git", ".gitignore", ".gitattributes", ".gitmodules", ".gitkeep"}
REQUIRED = ("main.py", "requirements.txt", "base/base_config.py", "base/base_trainer.py",
            "utils/registry.py", "utils/optim/optimizer.py", "scripts/run.sh", "scripts/setup.sh")


def reject_link(path):
    if path.is_symlink() or getattr(path, "is_junction", lambda: False)():
        raise ValueError("Symlink/junction paths are not supported: " + str(path))


def validate_ancestors(path):
    for item in (path, *path.parents):
        reject_link(item)
        if item.exists() and not item.is_dir():
            raise ValueError("Destination ancestor is not a directory: " + str(item))


def inventory(source):
    files, directories = [], []
    reject_link(source)
    if not source.is_dir():
        raise ValueError("Framework source is missing: " + str(source))
    for root, dirs, names in os.walk(source, followlinks=False):
        root = Path(root)
        dirs[:] = sorted(name for name in dirs if name not in IGNORED_DIRS)
        for name in dirs:
            item = root / name
            reject_link(item)
            directories.append(item.relative_to(source).as_posix())
        for name in sorted(names):
            if name in IGNORED_DIRS or Path(name).suffix in {".pyc", ".pyo"}:
                continue
            item = root / name
            reject_link(item)
            if not stat.S_ISREG(item.stat().st_mode):
                raise ValueError("Source contains a non-regular file: " + str(item))
            # Opening every source file validates readability before any mutation.
            with item.open("rb") as stream:
                stream.read(1)
            files.append(item.relative_to(source).as_posix())
    missing = sorted(set(REQUIRED) - set(files))
    if missing:
        raise ValueError("Incomplete framework source; missing: " + ", ".join(missing))
    return sorted(files), sorted(directories, key=lambda name: (name.count("/"), name))


def destination_entries(destination):
    files, directories = [], []
    if not destination.exists():
        return files, directories
    for root, dirs, names in os.walk(destination, followlinks=False):
        root = Path(root)
        for name in dirs + names:
            reject_link(root / name)
        # VCS contents are preserved, not inspected or copied into.
        dirs[:] = sorted(name for name in dirs if name not in IGNORED_DIRS)
        directories.extend((root / name).relative_to(destination) for name in dirs)
        for name in names:
            item = root / name
            if not stat.S_ISREG(item.stat().st_mode):
                raise ValueError("Destination contains a non-regular file: " + str(item))
            if item.suffix not in {".pyc", ".pyo"}:
                files.append(item.relative_to(destination))
    return files, directories


def docs_only(files, directories):
    for entry in directories:
        if entry.parts[0].lower() not in DOC_DIRS:
            return False
    for entry in files:
        if len(entry.parts) == 1 and entry.name in VCS_FILES:
            continue
        suffix = entry.suffix.lower()
        if suffix in DOC_SUFFIXES and (len(entry.parts) == 1 or entry.parts[0].lower() in DOC_DIRS):
            continue
        if suffix in FIGURE_SUFFIXES and entry.parts[0].lower() in DOC_DIRS:
            continue
        return False
    return True


def build_plan(destination):
    raw = Path(destination).expanduser()
    if ".." in raw.parts:
        raise ValueError("Destination may not contain '..' traversal components")
    absolute = raw.absolute()
    validate_ancestors(absolute)
    destination = absolute.resolve()
    if destination == SKILL_ROOT or SKILL_ROOT in destination.parents or destination in SOURCE.parents:
        raise ValueError("Destination must not overlap the skill or framework source")
    files, directories = inventory(SOURCE)
    existing_files, existing_dirs = destination_entries(destination)
    present = {entry.as_posix() for entry in existing_files}
    # Complete known structure is required, but contents may be user-customized.
    # Reuse is never an upgrade or a claim that consumer experiments are ready.
    if set(files).issubset(present):
        action = "reuse"
    else:
        if not docs_only(existing_files, existing_dirs):
            raise ValueError("Refusing unrelated application or partial/conflicting framework target: " + str(destination))
        conflicts = [name for name in files + directories if (destination / name).exists()]
        if conflicts:
            raise ValueError("Refusing to overwrite existing paths: " + ", ".join(conflicts))
        action = "copy"
    return {"source": str(SOURCE), "destination": str(destination), "action": action,
            "files": files if action == "copy" else [],
            "directories": directories if action == "copy" else [],
            "message": "Existing framework reused unchanged; consumer readiness is not asserted." if action == "reuse"
                       else "Dry-run plan; --apply authorizes copying only, not training."}


def apply_plan(plan):
    if plan["action"] == "reuse":
        return dict(plan, applied=False, copied=0)
    destination = Path(plan["destination"])
    created_files, created_dirs = [], []

    def make_directory(path):
        if path.exists():
            reject_link(path)
            if not path.is_dir():
                raise ValueError("Conflicting destination path: " + str(path))
            return
        if not path.parent.exists():
            make_directory(path.parent)
        path.mkdir()
        created_dirs.append(path)

    try:
        make_directory(destination)
        for name in plan["directories"]:
            make_directory(destination / name)
        for name in plan["files"]:
            target = destination / name
            validate_ancestors(target.parent)
            source = SOURCE / name
            reject_link(source)
            # Exclusive creation is essential even after preflight: never replace
            # a file that appeared between planning and application.
            with target.open("xb") as output:
                created_files.append((target, os.fstat(output.fileno())))
                with source.open("rb") as input_stream:
                    shutil.copyfileobj(input_stream, output)
            shutil.copystat(source, target, follow_symlinks=False)
    except Exception as error:
        rollback_errors = []
        for path, original in reversed(created_files):
            try:
                current = path.lstat()
                if stat.S_ISREG(current.st_mode) and (current.st_dev, current.st_ino) == (original.st_dev, original.st_ino):
                    path.unlink()
            except FileNotFoundError:
                pass
            except OSError as rollback_error:
                rollback_errors.append(str(rollback_error))
        for path in reversed(created_dirs):
            try:
                path.rmdir()  # Never recursively remove user files or directories.
            except FileNotFoundError:
                pass
            except OSError as rollback_error:
                rollback_errors.append(str(rollback_error))
        detail = "; rollback could not remove: " + "; ".join(rollback_errors) if rollback_errors else ""
        raise ValueError("Copy failed; only invocation-created paths were rolled back: " + str(error) + detail) from error
    return dict(plan, applied=True, copied=len(created_files), message="Framework copied; no experiment was launched.")


def main(argv=None):
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--dest", required=True, help="Fresh target or documentation-only workspace")
    cli.add_argument("--apply", action="store_true", help="Authorize the planned non-overwriting copy")
    args = cli.parse_args(argv)
    try:
        plan = build_plan(args.dest)
        result = apply_plan(plan) if args.apply else dict(plan, applied=False, copied=0)
        print(json.dumps(result, indent=2))
        return 0
    except (OSError, ValueError) as error:
        print(json.dumps({"error": str(error), "applied": False}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
