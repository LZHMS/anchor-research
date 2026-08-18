#!/bin/bash

set -euo pipefail

# Environment setup — modify paths to match your environment
# export HF_ENDPOINT=https://hf-mirror.com
# export HF_HUB_DISABLE_XET=1
# export PYOPENGL_PLATFORM=osmesa
# export HF_HOME=~/hf_cache
# export TORCH_HOME=~/torch_cache

# source /path/to/conda.sh
# conda activate your_env

# ------------------------- Example Training Commands
#
# Single GPU training:
#   bash scripts/example/train.sh False train True 20000
#
# Distributed training (multi-GPU):
#   bash scripts/example/train.sh True train True 20000
#
# Test mode:
#   bash scripts/example/train.sh False test False 0
#
# Debug mode:
#   bash scripts/example/train.sh False debug False 100
#
# Multi-stage training (stage 2, with pretrained from stage 1):
#   bash scripts/example/train_stage2.sh False train True Stage2Trainer 90000
#
# -------------------------
