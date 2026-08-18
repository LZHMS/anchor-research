#!/bin/bash

# ============================================================
# Standard single-stage training script
# ============================================================
# Usage:
#   bash scripts/example/train.sh [DISTRIBUTED] [MODE] [USE_WANDB] [MAX_ITER] [RUN_TAG]
#
# Arguments:
#   $1 DISTRIBUTED : Enable distributed training (True/False)
#   $2 MODE        : Execution mode (train/test/debug)
#   $3 USE_WANDB   : Use wandb logging (True/False)
#   $4 MAX_ITER    : Maximum training iterations
#   $5 RUN_TAG     : Optional experiment tag
# ============================================================

DISTRIBUTED=${1:-False}
MODE=${2:-train}
USE_WANDB=${3:-False}
MAX_ITER=${4:-20000}
RUN_TAG=${5:-}

# DDP config
NUM_GPUS=3
GPU_IDS=[0,1,2]
MASTER_PORT=29501

# Experiment config
RESUME=True
DATASET=MyDataset
TRAINER=MyTrainer
CFG=example/${TRAINER}

BASE_DIR=output/${DATASET}/${CFG}${RUN_TAG:+_}${RUN_TAG}
MODEL_DIR=${BASE_DIR}
RUN_DIR=${BASE_DIR}

case ${MODE} in
  test)  RUN_DIR=${BASE_DIR}/test ;;
  debug) RUN_DIR=${BASE_DIR}/debug ;;
esac

if [ -d ${RUN_DIR} ] && [ ${RESUME} = False ]; then
  echo "Results exist in ${RUN_DIR}. Skip this job."
  rm -rf ${RUN_DIR}
else
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
  )

  # Debug mode: enable synchronous CUDA for easier debugging
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
fi
