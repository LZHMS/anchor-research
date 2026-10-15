#!/usr/bin/env bash
set -euo pipefail

# Instructions only: running or sourcing this file does not install packages,
# change the active environment, create outputs, or start an experiment.
cat <<'USAGE'
Environment setup (run these commands yourself from the copied project root):
  python -m venv .venv
  source .venv/bin/activate
  # Git Bash on Windows: source .venv/Scripts/activate
  # Install a PyTorch build appropriate for your CPU or allocated CUDA devices:
  # https://pytorch.org/get-started/locally/
  python -m pip install -r requirements.txt

First implement your real dataset/model/trainer and write its YAML config.
The paths and registration module below refer to those consumer-owned files;
no example trainer or dataset is supplied. Repeated --module imports register
your components. Direct Python and the optional Bash wrapper use the same CLI.

Inspect the entrypoint without starting training:
  python main.py --help
  bash scripts/run.sh --help
  bash scripts/run.sh --config-file config/experiment.yaml --check-config
  bash scripts/run.sh --module trainers.experiment --list-trainers

Single-process training (CPU or one device selected by your config):
  bash scripts/run.sh --config-file config/experiment.yaml --module trainers.experiment ENV.OUTPUT_DIR output/experiment
  # Equivalent direct invocation from the project root:
  python main.py --config-file config/experiment.yaml --module trainers.experiment ENV.OUTPUT_DIR output/experiment

Use a specific interpreter, including a path containing spaces:
  PYTHON="/absolute/path/to/environment/bin/python" bash scripts/run.sh --help

Checkpoints and execution modes:
  bash scripts/run.sh --config-file config/experiment.yaml --module trainers.experiment --resume ENV.OUTPUT_DIR output/experiment
  bash scripts/run.sh --config-file config/experiment.yaml --module trainers.experiment --mode test --model-dir output/experiment --load-epoch 10
  bash scripts/run.sh --config-file config/experiment.yaml --module trainers.experiment --mode debug ENV.OUTPUT_DIR output/debug-experiment
  # Use --load-iter instead of --load-epoch for iteration-based checkpoints.
  # A later training stage uses its own YAML with real pretrained model fields
  # understood by your trainer; it uses this same entrypoint, not another script.

Optional single-node CUDA torchrun (only after allocating these devices):
  CUDA_VISIBLE_DEVICES=0,1 bash scripts/run.sh --distributed 2 --master-port 29501 --config-file config/experiment.yaml --module trainers.experiment ENV.OUTPUT_DIR output/distributed-experiment
  # Change the indices/count to your allocation; they must match exactly.
  # Put wrapper options first. CPU/MPS distributed training is not supported.

The wrapper may be invoked by absolute path from any working directory. Relative
paths then resolve from the copied project root; direct Python invocation should
also be run there. All main.py options and trailing YACS KEY VALUE overrides are
passed through unchanged. Quote paths/values containing spaces.

Training refuses non-empty output directories unless --resume is explicit and
valid checkpoints exist. Neither launch path deletes outputs or silently resumes.
USAGE
