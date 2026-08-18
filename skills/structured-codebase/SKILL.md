---
name: structured-codebase
description: Parses and operates within the Structured Codebase training framework (a modular, registry-driven architecture inspired by Dassl). Use this skill whenever the user wants to bootstrap a new training project from scratch, add a new trainer, create a new model, configure datasets, run training pipelines, or understand where components (base models, losses, evaluators, trainers) belong in this framework. Also use when the user asks about extending trainers, adding training scripts, modifying configs, or working with this project structure in any way.
version: 1.0.0
author: Zhihao Li
license: MIT
metadata:
  hermes:
    tags: [Coding, Structured, Trainer, Codebase]
---

# Structured Codebase Framework

A decoupled, trainer-based architecture built on a modular, registry-driven foundation (inspired by Dassl). Designed as the starting point for any AI model training project.

## 🚀 Bootstrapping a New Project

When bootstrapping a new project:
1. Create the project root directory
2. Copy the contents of `StructCodebase/` (from the skill directory) into the project root — it contains the `base/` framework, `utils/`, and a skeleton `train.py`
3. Implement `dataset/`, `models/`, `trainers/`, `config/`, and `scripts/` as described below
4. Create `main.py` as the entry point (see Entry Point section)

## 📁 Directory Structure

```
<project>/
├── main.py                  # Entry point — parses args, builds trainer, runs train/test/debug
├── base/                    # Core framework — DO NOT MODIFY without user confirmation
│   ├── __init__.py
│   ├── base_config.py       # YACS CfgNode config definition
│   ├── base_datamanager.py  # DATASET_REGISTRY
│   ├── base_dataset.py      # DatasetBase
│   ├── base_evaluator.py    # EVALUATOR_REGISTRY
│   ├── base_loss.py         # LOSS_REGISTRY, build_loss()
│   ├── base_model.py        # MODEL_REGISTRY
│   └── base_trainer.py      # TrainerBase, TRAINER_REGISTRY, build_trainer()
├── config/                  # YACS .yaml config files, organized by category
│   └── <category>/
│       └── <trainer>.yaml
├── dataset/                 # Dataset implementations, inherit DatasetBase
├── models/
│   ├── <model>.py           # Top-level model definitions
│   ├── avatar/              # Domain-specific head/body models
│   └── lib/                 # Reusable sub-components
│       ├── algorithm/       # Flow matching, diffusion schedule, etc.
│       ├── audio/           # Audio feature extractors (HuBERT, wav2vec2, ...)
│       ├── head/            # Model head modules (embeddings, pose encoding, ...)
│       ├── network/         # Network blocks (attention, transformer, MLP, conv, ...)
│       └── tail/            # Tail modules (norm, residual, layers, ...)
├── trainers/                # Training logic, inherit TrainerBase
│   └── ablation/            # Ablation study trainers (optional)
├── losses/                  # Custom loss functions
├── evaluator/               # Evaluation logic
├── utils/                   # Shared utilities
│   ├── registry.py          # Registry class
│   ├── meters.py            # AverageMeter
│   ├── tools.py             # Helpers (mkdir_if_missing, check_availability, ...)
│   ├── optim/               # optimizer.py, scheduler.py
│   └── ...                  # Domain-specific utilities
├── scripts/                 # Bash scripts for training execution
│   ├── setup.sh             # Environment setup + example commands
│   └── <category>/          # Category-specific train/test scripts
├── data/                    # Raw data
├── pretrained/              # Pretrained weights
└── output/                  # Training output
```

## 🔒 Golden Rules

### 1. `base/` is read-only
The `base/` directory defines the core framework scaffolding. **Do NOT modify files in `base/` unless the user explicitly confirms.** All new functionality should be built by extending the base classes, not by changing them. If a change to `base/` seems necessary, first explain to the user why and get their confirmation before proceeding.

### 2. New trainers MUST be imported in `main.py`
The registry system discovers trainers through Python imports. A class decorated with `@TRAINER_REGISTRY.register()` only registers itself when its module is imported. All trainer imports are at the top of `main.py`. The workflow:

1. Create the trainer file (e.g., `trainers/MyNewTrainer.py`)
2. Add import in `main.py`: `from trainers.MyNewTrainer import MyNewTrainer`

Without step 2, `build_trainer()` will NOT find the trainer — the decorator never ran. This applies to all registries (MODEL, DATASET, EVALUATOR, LOSS) — their modules must be imported before use.

### 3. Training runs through `scripts/` bash scripts
All training and testing is launched via bash scripts under `scripts/`, NOT by running `python main.py` directly. When creating a new trainer, also create a corresponding script following the standard pattern (see below). Look at existing scripts in the `scripts/<category>/` directories for reference.

### 4. New components follow inheritance, not replacement
When adding new functionality:
- **New trainer** → New file under `trainers/`, inherit `TrainerBase`
- **New model** → New file under `models/`, register with `@MODEL_REGISTRY.register()` if needed
- **New dataset** → New file under `dataset/`, inherit `DatasetBase`
- **New loss** → Add to `losses/`, register with `@LOSS_REGISTRY.register()`
- **Reusable component** → Put in `models/lib/` (network, audio, head, algorithm, tail)

Never modify an existing trainer or model to add new functionality — create a new class that inherits instead.

## 🔧 Registry System (How Discovery Works)

The framework uses a decorator-based registry for dynamic module loading. Flow:

1. `main.py` imports trainer modules → `@TRAINER_REGISTRY.register()` populates the registry with the class name as the key
2. Config YAML sets `TRAINER.NAME: SomeTrainer`
3. `build_trainer(cfg)` looks up `cfg.TRAINER.NAME` in the registry and instantiates with the config

| Registry | Defined in | Decorator |
|----------|-----------|-----------|
| TRAINER | `base/base_trainer.py` | `@TRAINER_REGISTRY.register()` |
| MODEL | `base/base_model.py` | `@MODEL_REGISTRY.register()` |
| DATASET | `base/base_datamanager.py` | `@DATASET_REGISTRY.register()` |
| EVALUATOR | `base/base_evaluator.py` | `@EVALUATOR_REGISTRY.register()` |
| LOSS | `base/base_loss.py` | `@LOSS_REGISTRY.register()` |

The registry uses the class name as the registration key by default. The name in the config YAML (`TRAINER.NAME`, `MODEL.NAME`, etc.) must match exactly.

## 📝 Trainer Lifecycle

`TrainerBase` handles the full training loop. Subclasses override specific hooks:

```
train()
  before_train()      # Resume checkpoint, init writer
  └─ Iter mode (TRAIN.USE_ITERS: True):
       for iter in range(start_iter, max_iters):
         before_iter()      # Reset meters, set train mode
         run_iter()         # parse_batch → forward_backward → log
         after_iter()       # Update LR, eval, save checkpoint
  └─ Epoch mode (TRAIN.USE_ITERS: False):
       for epoch in range(start_epoch, max_epoch):
         before_epoch()     # Reset meters, set train mode
         run_epoch()        # parse_batch → forward_backward → log
         after_epoch()      # Update LR, eval, save checkpoint
  after_train()       # Final test, close writer, destroy DDP
```

**Methods you MUST implement:**

| Method | Purpose |
|--------|---------|
| `build_data_loader()` | Create `self.train_loader`, `self.val_loader`, `self.test_loader` via a DataManager |
| `build_model()` | Build model, optimizer, scheduler; call `self.register_model("model", model, optim, sched)` |
| `forward_backward(batch)` | Forward pass → loss → `self.model_backward_and_update(loss)` → return `{"loss_name": value}` dict |
| `parse_batch(batch)` | Extract tensors from batch dict and move to `self.device` |

**Methods you MAY override:**

| Method | Purpose |
|--------|---------|
| `before_train()` | Extra setup (call `super().before_train()` first) |
| `eval(n_rounds)` | Custom validation pipeline |
| `test()` | Custom inference/evaluation pipeline |

### Example: Minimal New Trainer

```python
from base.base_trainer import TrainerBase, TRAINER_REGISTRY
from base.base_loss import build_loss

@TRAINER_REGISTRY.register()
class MyNewTrainer(TrainerBase):
    def __init__(self, cfg):
        super().__init__(cfg)
        self.build_data_loader()
        self.build_model()
        self.criterion = build_loss(cfg)

    def build_data_loader(self):
        from dataset.my_dataset import MyDatasetDM
        dm = MyDatasetDM(self.cfg, infinite_train=True)
        self.train_loader = dm.train_loader
        self.val_loader = dm.val_loader
        self.test_loader = dm.test_loader
        self.dm = dm

    def build_model(self):
        from models.my_model import MyModel
        self.model = MyModel(self.cfg.MODEL)
        self.model.to(self.device)
        self.optim = self.build_optimizer(self.model)
        self.sched = self.build_lr_scheduler(self.optim)
        if self.is_distributed:
            self.model = self.wrap_model_with_ddp(self.model, find_unused_parameters=False)
        self.register_model("model", self.model, self.optim, self.sched)

    def forward_backward(self, batch):
        x = self.parse_batch(batch)
        pred = self.model(x)
        loss = self.criterion(pred, x)
        self.model_backward_and_update(loss)
        return {"loss": loss.item()}

    def parse_batch(self, batch):
        return batch["data"].to(self.device)
```

**Then in `main.py`, add:**
```python
from trainers.MyNewTrainer import MyNewTrainer
```

## ⚙️ Configuration (YACS)

Configs live under `config/<category>/<trainer>.yaml`. Key sections:

| Section | Purpose |
|---------|---------|
| `ENV` | GPU, distributed training, wandb, output dir, seed |
| `DATASET` | Dataset name, root, dataset-specific params |
| `DATALOADER` | Batch size, num workers |
| `MODEL` | Model name, architecture params, pretrained paths |
| `TRAINER` | Trainer name (must match the class name registered in the registry) |
| `TRAIN` | USE_ITERS, MAX_ITERS/MAX_EPOCHS, SAVE_FREQ, EVAL_FREQ, PRINT_FREQ |
| `TEST` | Split, NO_TEST, FINAL_MODEL |
| `OPTIM` | Optimizer, LR, scheduler, warmup |
| `LOSS` | Loss name and params |

Novel parameters not defined in `base_config.py` go under `ENV.EXTRA` and are accessed via `self.cfg.ENV.EXTRA.get('KEY')`.

Override config values at runtime through the bash script's `COMMON_ARGS`:
```bash
TRAIN.MAX_ITERS 90000
TRAINER.NAME MyNewTrainer
MODEL.PRETRAINED.PATH /path/to/checkpoint.pth.tar
```

## 🚀 Standard Script Pattern

All training scripts follow a standard pattern. When creating a new trainer, create a matching script:

```bash
#!/bin/bash

# Runtime args
DISTRIBUTED=${1:-False}
MODE=${2:-train}
USE_WANDB=${3:-False}
TRAINER=${4:-MyTrainerName}
MAX_ITER=${5:-20000}
RUN_TAG=${6:-}

# DDP config
NUM_GPUS=3
GPU_IDS=[0,1,2]
MASTER_PORT=29501

# Experiment config
DATASET=MyDataset
CFG=Category/${TRAINER}

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
)

# For multi-stage training, add pretrained model paths:
# PRE_STAGE=Category/PreviousTrainer
# PRETRAINED_DIR=output/${DATASET}/${PRE_STAGE}/model/model-best.pth.tar
# Then append: MODEL.PRETRAINED.SOME_PATH ${PRETRAINED_DIR}

# Debug mode
if [ ${MODE} = debug ]; then
  export CUDA_LAUNCH_BLOCKING=1
fi

if [ ${DISTRIBUTED} = True ]; then
  python -m torch.distributed.run \
    --nproc_per_node=${NUM_GPUS} \
    --master_port=${MASTER_PORT} \
    "${COMMON_ARGS[@]}"
else
  python "${COMMON_ARGS[@]}"
fi
```

Standard script argument positions (reference existing scripts in the project for the exact convention):
- `$1` DISTRIBUTED, `$2` MODE, `$3` USE_WANDB — always present
- `$4` TRAINER name — varies per script
- `$5` STAGE or MAX_ITER — depends on whether multi-stage
- `$6` MAX_ITER or RUN_TAG
- Look at existing `scripts/<category>/` scripts for the established convention and follow it

## 📦 Entry Point (`main.py`)

`main.py` is the single entry point for all training and testing. It:

1. Parses CLI args: `--config-file`, `--mode` (train/test/debug/analysis), `--model-dir`, `--load-iter`, `--load-epoch`, and extra `opts`
2. Loads config: `BaseConfig().cfg.merge_from_file()` then `merge_from_list()` for CLI overrides
3. Freezes config and calls `build_trainer(cfg)` — looks up `cfg.TRAINER.NAME` in `TRAINER_REGISTRY`
4. Runs `trainer.train()` or `trainer.test()` based on mode

**Critical:** Every trainer model file must be imported at the top of `main.py` so `@TRAINER_REGISTRY.register()` decorators execute. If a new trainer is not in the imports, it will NOT be found at runtime.

## 🧠 Best Practices

- **Don't reinvent the loop** — `TrainerBase` handles epochs, iterations, checkpointing, DDP, and logging. Only override lifecycle hooks.
- **Losses** — Use `build_loss(cfg)` from `base.base_loss` or custom losses in `losses/`.
- **Metrics** — Log via `self.write_scalar(tag, value, global_step)`. For batched logging, `self.write_meters(meters_dict, prefix="train/", global_step=self.iter)`.
- **Distributed training** — Check `self.is_distributed` before DDP-specific code, `self.is_main_process()` for rank-0 operations, `self.reduce_meters()` for cross-GPU aggregation.
- **Reusable components** — Shared blocks (MLP, attention, VQ, norm, residual) go in `models/lib/`.
- **Multiple trainers per file** — Related trainers (e.g., stage-1 encoder + stage-2 diffusion) can share a file. Each gets its own `@TRAINER_REGISTRY.register()` decorator and its own import line in `main.py`.
- **Config organization** — Group configs by category (`config/Category/Trainer.yaml`), matching the script organization under `scripts/Category/`.
