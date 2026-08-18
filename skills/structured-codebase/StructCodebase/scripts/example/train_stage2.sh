#!/bin/bash

# ============================================================
# Multi-stage training script (e.g., stage 2 that loads
# pretrained weights from stage 1's output)
# ============================================================
# Usage:
#   bash scripts/example/train_stage2.sh [DISTRIBUTED] [MODE] [USE_WANDB] [TRAINER] [MAX_ITER] [RUN_TAG]
#
# Arguments:
#   $1 DISTRIBUTED : Enable distributed training (True/False)
#   $2 MODE        : Execution mode (train/test/debug)
#   $3 USE_WANDB   : Use wandb logging (True/False)
#   $4 TRAINER     : Trainer name for this stage
#   $5 MAX_ITER    : Maximum training iterations
#   $6 RUN_TAG     : Optional experiment tag
# ============================================================

DISTRIBUTED=${1:-False}
MODE=${2:-train}
USE_WANDB=${3:-False}
TRAINER=${4:-Stage2Trainer}
MAX_ITER=${5:-90000}
RUN_TAG=${6:-}

# DDP config
NUM_GPUS=3
GPU_IDS=[0,1,2]
MASTER_PORT=29501

# Experiment config
DATASET=MyDataset
CFG=example/${TRAINER}

# --- Pretrained model from stage 1 ---
STAGE1_TRAINER=example/Stage1Trainer
STAGE1_DIR=output/${DATASET}/${STAGE1_TRAINER}/model/model-best.pth.tar

BASE_DIR=output/${DATASET}/${CFG}${RUN_TAG:+_}${RUN_TAG}
MODEL_DIR=${BASE_DIR}
RUN_DIR=${BASE_DIR}

case ${MODE} in
  test)  RUN_DIR=${BASE_DIR}/test ;;
  debug) RUN_DIR=${BASE_DIR}/debug ;;
esac

mkdir -p ${RUN_DIR}

COMMON_ARGS=(
  main.py
  --mode ${MODE}
  --config-file config/${CFG}.yaml
  --model-dir ${MODEL_DIR}
  ENV.GPU ${GPU_IDS}
  ENV.RESUME ${RUN_DIR}
  ENV.DISTRIBUTED ${DISTRIBUTED}
  ENV.OUTPUT_DIR ${RUN_DIR}
  ENV.USE_WANDB ${USE_WANDB}
  ENV.WANDB.NAME ${CFG}_${DATASET}${RUN_TAG:+_}${RUN_TAG}
  DATASET.NAME ${DATASET}
  TRAINER.NAME ${TRAINER}
  TRAIN.MAX_ITERS ${MAX_ITER}
  # Pass the pretrained weights from stage 1
  MODEL.PRETRAINED.STAGE1_PATH ${STAGE1_DIR}
)

# Debug mode
if [ ${MODE} = debug ]; then
  export CUDA_LAUNCH_BLOCKING=1
fi

if [ ${DISTRIBUTED} = True ]; then
  echo "Starting distributed ${MODE} with ${NUM_GPUS} GPUs..."
  python -m torch.distributed.run \
    --nproc_per_node=${NUM_GPUS} \
    --master_port=${MASTER_PORT} \
    "${COMMON_ARGS[@]}"
else
  echo "Starting single GPU ${MODE} on GPU 0..."
  python "${COMMON_ARGS[@]}"
fi
