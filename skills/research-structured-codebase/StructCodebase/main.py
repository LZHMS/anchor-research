"""Generic entrypoint for explicitly registered, fully implemented consumer trainers."""

import argparse
import importlib
import json
import os
from pathlib import Path
import sys

# Inspection commands must not leave import caches in a copied project.
sys.dont_write_bytecode = True
PROJECT_ROOT = Path(__file__).resolve().parent


def parser():
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--config-file", help="YAML config, relative to the project root")
    result.add_argument("--module", action="append", default=[], metavar="DOTTED_MODULE",
                        help="Explicit registration module; repeat for multiple modules")
    result.add_argument("--trainer", help="Override TRAINER.NAME")
    result.add_argument("--mode", choices=("train", "test", "debug"), default="train")
    result.add_argument("--model-dir", help="Checkpoint root for testing or explicit resume")
    selection = result.add_mutually_exclusive_group()
    selection.add_argument("--load-iter", type=int, metavar="N")
    selection.add_argument("--load-epoch", type=int, metavar="N")
    result.add_argument("--resume", action="store_true", help="Explicitly authorize training resume")
    result.add_argument("--check-config", action="store_true", help="Print resolved config without constructing a trainer")
    result.add_argument("--list-trainers", action="store_true", help="List trainers registered by the explicit modules")
    result.add_argument("opts", nargs=argparse.REMAINDER, metavar="KEY VALUE",
                        help="Trailing YACS overrides (highest precedence)")
    return result


def resolve_config(args):
    from base.base_config import BaseConfig
    import yaml

    cfg = BaseConfig().cfg
    cfg.ENV.USE_WANDB = False
    cfg.ENV.WANDB.KEY = None
    for name in ("ENTITY", "PROJECT", "NAME", "NOTES", "TAGS"):
        setattr(cfg.ENV.WANDB, name, "")
    # The core takes a modulo of SAVE_FREQ even at the last step.
    cfg.TRAIN.SAVE_FREQ = 1
    with open(args.config_file, encoding="utf-8") as stream:
        supplied = yaml.safe_load(stream) or {}
    if not isinstance(supplied, dict):
        raise ValueError("Config YAML must contain a mapping")
    cfg.merge_from_file(args.config_file)
    if args.trainer is not None:
        cfg.TRAINER.NAME = args.trainer
    if args.resume and args.model_dir:
        cfg.ENV.RESUME = args.model_dir

    world_size = int(os.environ.get("WORLD_SIZE", "1"))
    if "LOCAL_RANK" in os.environ:
        cfg.ENV.DISTRIBUTED = True
        cfg.ENV.GPU = list(range(world_size))
    overrides = args.opts[1:] if args.opts[:1] == ["--"] else args.opts
    if len(overrides) % 2:
        raise ValueError("Trailing YACS overrides must be KEY VALUE pairs")
    cfg.merge_from_list(overrides)

    if not cfg.TRAINER.NAME:
        raise ValueError("Set TRAINER.NAME in YAML, --trainer, or trailing overrides")
    if not isinstance(cfg.ENV.OUTPUT_DIR, str) or not cfg.ENV.OUTPUT_DIR.strip():
        raise ValueError("ENV.OUTPUT_DIR must be a non-empty path")
    if args.mode == "test":
        if args.resume:
            raise ValueError("--resume applies only to training/debug")
        if not args.model_dir:
            raise ValueError("Test mode requires --model-dir (no implicit checkpoint fallback)")
        if args.load_iter is not None and not cfg.TRAIN.USE_ITERS:
            raise ValueError("--load-iter requires TRAIN.USE_ITERS=True")
        if args.load_epoch is not None and cfg.TRAIN.USE_ITERS:
            raise ValueError("--load-epoch requires TRAIN.USE_ITERS=False")
        for value in (args.load_iter, args.load_epoch):
            if value is not None and value < 1:
                raise ValueError("Checkpoint iteration/epoch numbers must be positive (one-based)")
    else:
        if args.load_iter is not None or args.load_epoch is not None:
            raise ValueError("--load-iter/--load-epoch are test-only; resume uses core checkpoint pointers")
        if args.model_dir and not args.resume:
            raise ValueError("Training --model-dir requires explicit --resume")
        if cfg.ENV.RESUME and not args.resume:
            raise ValueError("ENV.RESUME requires explicit --resume")
        bound = "MAX_ITERS" if cfg.TRAIN.USE_ITERS else "MAX_EPOCHS"
        start = cfg.TRAIN.START_ITER if cfg.TRAIN.USE_ITERS else cfg.TRAIN.START_EPOCH
        maximum = getattr(cfg.TRAIN, bound)
        if not isinstance(start, int) or isinstance(start, bool) or start < 0:
            raise ValueError("The configured training start must be a non-negative integer")
        if not isinstance(maximum, int) or isinstance(maximum, bool) or maximum <= start:
            raise ValueError("TRAIN." + bound + " must be an integer greater than the configured start")
        if args.mode == "debug":
            train_yaml = supplied.get("TRAIN", {})
            explicit = isinstance(train_yaml, dict) and bound in train_yaml
            if not explicit and "TRAIN." + bound not in overrides[::2]:
                raise ValueError("Debug mode requires an explicit TRAIN." + bound + " bound in YAML or overrides")
        for key in ("SAVE_FREQ", "PRINT_FREQ"):
            value = getattr(cfg.TRAIN, key)
            if not isinstance(value, int) or isinstance(value, bool) or value < 1:
                raise ValueError("TRAIN." + key + " must be a positive integer")
        if cfg.TRAIN.EVALUATE and cfg.TRAIN.EVAL_FREQ < 1:
            raise ValueError("TRAIN.EVAL_FREQ must be positive when evaluation is enabled")
        if cfg.OPTIM.LR_UPDATE_FREQ < 1:
            raise ValueError("OPTIM.LR_UPDATE_FREQ must be positive")
    if cfg.ENV.DISTRIBUTED:
        if world_size < 1 or "LOCAL_RANK" not in os.environ:
            raise ValueError("Distributed execution requires torchrun with CUDA workers")
        visible = os.environ.get("CUDA_VISIBLE_DEVICES", "").split(",")
        if len(visible) != world_size or any(not item.strip().isdigit() for item in visible) or len(set(visible)) != world_size:
            raise ValueError("Distributed execution requires exactly WORLD_SIZE distinct numeric CUDA_VISIBLE_DEVICES")
        if not cfg.ENV.USE_CUDA or cfg.ENV.GPU != list(range(world_size)):
            raise ValueError("Distributed execution requires USE_CUDA=True and logical ENV.GPU=[0,...,WORLD_SIZE-1]")
    elif "LOCAL_RANK" in os.environ:
        raise ValueError("ENV.DISTRIBUTED=False conflicts with torchrun")
    cfg.freeze()
    return cfg


def require_fresh_output(directory):
    path = Path(directory)
    if path.exists() and (not path.is_dir() or any(path.iterdir())):
        raise ValueError("Refusing non-empty output directory: " + str(path) + "; choose a new ENV.OUTPUT_DIR or explicit --resume")


def checkpoint_paths(directory, names, use_iters, args):
    root = Path(directory)
    if not names:
        raise ValueError("The consumer trainer must register at least one model")
    paths = []
    for name in names:
        model_dir = root / name
        if args.resume:
            pointer = model_dir / "checkpoint"
            if not pointer.is_file():
                raise ValueError("Resume requires checkpoint pointer: " + str(pointer))
            lines = pointer.read_text(encoding="utf-8").splitlines()
            filename = lines[0] if lines else ""
            if not filename or Path(filename).name != filename or "/" in filename or "\\" in filename:
                raise ValueError("Invalid checkpoint pointer: " + str(pointer))
        else:
            step = args.load_iter if use_iters else args.load_epoch
            kind = "iter" if use_iters else "epoch"
            filename = "model-best.pth.tar" if step is None else "model.pth.tar-" + kind + "-" + str(step)
        path = model_dir / filename
        if not path.is_file():
            raise ValueError("Requested checkpoint is unavailable: " + str(path))
        paths.append(path)
    return paths


def validate_resume_steps(trainer, paths, cfg):
    key = "iter" if cfg.TRAIN.USE_ITERS else "epoch"
    maximum = cfg.TRAIN.MAX_ITERS if cfg.TRAIN.USE_ITERS else cfg.TRAIN.MAX_EPOCHS
    steps = []
    for path in paths:
        # Validate mode and multi-model consistency before the core starts
        # restoring models. The core owns the actual optimizer/scheduler restore.
        checkpoint = trainer.load_checkpoint(str(path))
        step = checkpoint.get(key)
        if not isinstance(step, int) or isinstance(step, bool) or step < 0:
            raise ValueError("Resume checkpoint must contain a non-negative " + key + ": " + str(path))
        if step >= maximum:
            raise ValueError("Resume checkpoint " + key + " is already at or beyond the configured training bound: " + str(path))
        steps.append(step)
    if len(set(steps)) != 1:
        raise ValueError("Registered model resume checkpoints have inconsistent training steps")


def execute(args, cfg):
    output = Path(cfg.ENV.OUTPUT_DIR)
    resume_dir = cfg.ENV.RESUME or str(output)
    if args.mode != "test":
        if args.resume:
            root = Path(resume_dir)
            if not root.is_dir() or not any(root.glob("*/checkpoint")):
                raise ValueError("Resume source has no core checkpoint pointers: " + str(root))
        # Other ranks enter the core process-group initialization before logging;
        # rank zero alone checks output so its new output.log cannot race this guard.
        elif not cfg.ENV.DISTRIBUTED or int(os.environ.get("RANK", "0")) == 0:
            require_fresh_output(output)
    elif not Path(args.model_dir).is_dir():
        raise ValueError("Model directory does not exist: " + args.model_dir)

    from base.base_trainer import TRAINER_REGISTRY, build_trainer
    if cfg.TRAINER.NAME not in TRAINER_REGISTRY.registered_names():
        raise ValueError("Unknown trainer " + repr(cfg.TRAINER.NAME) + "; import its registration module with --module. Registered: " + repr(TRAINER_REGISTRY.registered_names()))
    if cfg.ENV.DISTRIBUTED:
        import torch
        if not torch.cuda.is_available() or torch.cuda.device_count() < int(os.environ["WORLD_SIZE"]):
            raise ValueError("Protected core distributed training requires one available CUDA device per worker (no CPU/MPS DDP)")
    trainer = build_trainer(cfg)
    if args.mode == "test":
        checkpoint_paths(args.model_dir, trainer.get_model_names(), cfg.TRAIN.USE_ITERS, args)
        trainer.load_model(args.model_dir, epoch=args.load_epoch, iter=args.load_iter)
        trainer.test()
    else:
        if args.resume:
            paths = checkpoint_paths(resume_dir, trainer.get_model_names(), cfg.TRAIN.USE_ITERS, args)
            validate_resume_steps(trainer, paths, cfg)
        trainer.train()


def main(argv=None):
    cli = parser()
    args = cli.parse_args(argv)
    if not args.config_file and (not args.list_trainers or args.check_config):
        cli.error("--config-file is required except for --help or --list-trainers")
    os.chdir(PROJECT_ROOT)
    try:
        cfg = resolve_config(args) if args.config_file else None
        for module in args.module:
            if not all(part.isidentifier() for part in module.split(".")):
                raise ValueError("--module must be a dotted Python module name: " + repr(module))
            importlib.import_module(module)
        if args.list_trainers:
            from base.base_trainer import TRAINER_REGISTRY
            print(json.dumps({"trainers": sorted(TRAINER_REGISTRY.registered_names())}))
        if args.check_config:
            print(cfg.dump())
        if args.list_trainers or args.check_config:
            return 0
        execute(args, cfg)
        return 0
    except (ValueError, OSError, ImportError, KeyError, AssertionError) as error:
        cli.error(str(error))


if __name__ == "__main__":
    sys.exit(main())
