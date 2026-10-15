---
name: research-structured-codebase
description: Use the bundled registry-driven PyTorch framework to safely initialize a selected code project, implement real trainers/data/models, and invoke its generic train/test entry point. Preserve existing repositories, output artifacts and protected core files; use as an optional implementation helper of research-run-experiment, not an autonomous experiment scheduler.
version: 2.0.0
author: Zhihao Li
license: MIT
user-invocable: true
argument-hint: "repo_path: <selected-code-root> | action: inspect/bootstrap/extend | trainer: <actual-class> | config: <actual-YAML>"
metadata:
  category: coding
  tags: [research, coding, structured, trainer, codebase, pytorch]
  related_skills: [research-run-experiment]
---

# Research Structured Codebase

Use the framework when explicitly selected or when extending an existing compatible project. Do not migrate an unrelated repository into it merely because this skill is available. Use the host's available file/process/question/subagent capabilities; no particular agent framework, CLI or model is required.

## Responsibility and project roots

- `SKILL_DIR` is this installed skill's actual directory; bundled assets are `SKILL_DIR/StructCodebase`.
- `CODE_ROOT` is the explicit `repo_path`, otherwise the accepted caller's selected code root. Resolve relative paths against the caller's project root. Never use the installed skill directory as the output project.
- When called by [research-run-experiment](../research-run-experiment/SKILL.md), keep its original project/docs binding and single `docs/research-experiment-plannning/EXPERIMENT_TRACKER.md`. An external code root does not move research documents.
- This helper owns framework preparation and scoped implementation. The caller owns run selection, resource budget, execution consent, progress and result reporting. Loading the helper is not authorization to launch training or overwrite user files.
- Direct requests authorize only the requested action. Unknown destination, conflicting application code or an unselected framework requires clarification before mutation. A completed bootstrap is not a completed experiment.

## Safe initialization and reuse

Inspect the selected destination and actual bundled assets before changes. For a new project, use the real deterministic initializer rather than a recursive copy over arbitrary files:

```text
python "<actual SKILL_DIR>/scripts/bootstrap.py" --dest "<selected CODE_ROOT>"
python "<actual SKILL_DIR>/scripts/bootstrap.py" --dest "<selected CODE_ROOT>" --apply
```

The default command is a read-only plan; `--apply` is explicit copy authorization. Use actual resolved paths at runtime, not example placeholders.

The initializer must preserve existing research docs, refuse unrelated applications/partial conflicting copies, ignore generated caches, and never overwrite files. An already recognized framework is reused without recopying or upgrading its user's implementation. A missing existing source is an error; a deliberately selected fresh destination may legitimately not exist. Do not confuse those cases.

Copying/initialization failures are failures, not partial success. Report exact conflicts and keep user material intact; no force-delete/force-overwrite path. Inspect the produced inventory and use its real entry point. Do not copy `__pycache__`, `.pyc`, `.pyo`, or repository metadata into new projects.

The bundle includes real `main.py`, `requirements.txt`, `base/`, `utils/`, reusable `models/lib/` code and optional shell launchers. It does not include an implemented application dataset/trainer or a scientifically validated model. Add only the components actually required by the user's plan; never invent dataset paths, pretrained weights, metrics or completed reports.

## Environment

Use the project's existing interpreter/environment when compatible. Inspect `requirements.txt` and the selected components' imports before requesting dependency installation; do not install globally or fetch datasets/models automatically. Core training uses PyTorch, YACS, NumPy, Pillow, Loguru and TensorBoard. The optional DataManager/DatasetBase path additionally needs its actual imports, including `tabulate` and `gdown`; optional audio/model libraries may require further project-specific packages.

WandB is opt-in. The entry point uses generic disabled tracking defaults before applying explicit user YAML/CLI settings, rather than inheriting a personal project identity. Keep authentication in an authorized environment/credential mechanism, not committed config files, printed commands or reports.

Single-process CPU and available CUDA follow the real core backend behavior. Do not claim MPS or CPU distributed support that the core does not implement. CUDA distributed work requires explicitly allocated devices and the matching launcher setup; an idle-device observation is not a reservation.

Linux is the primary execution assumption. Do not expand this helper into a Windows
compatibility layer; platform-specific third-party environment diagnostics are separate
prerequisites, not scientific results or permission to weaken execution checks.

## Real project layout

| Path | Role |
|------|------|
| `main.py` | Generic CLI: config, explicit registration imports, train/test dispatch and output protection |
| `base/` | Protected framework implementation; extend through public interfaces |
| `utils/` | Registry, meters, optimizer/scheduler utilities |
| `models/lib/` | Optional reusable model components; import only what is actually needed |
| `scripts/run.sh` | Optional generic Bash wrapper, not a requirement on Windows/native Python |
| `scripts/setup.sh` | Safe environment/usage guidance; no implicit experiment |
| `dataset/`, `models/`, `trainers/`, `losses/`, `evaluator/` | Actual application components created as needed |
| `config/` | Actual project YAML files; no fictional trainer/data identifiers |
| `output/` or configured path | Runtime artifacts, distinct per attempt and never silently deleted |

## Extension rules

1. **Protected core:** do not modify an existing project's `base/` without explicit user approval. Explain the exact reason before changing it; prefer a real subclass/hook when appropriate. Do not monkeypatch core functions to suppress errors.
2. **Reuse before adding:** inspect the actual implementation first. Fix a component in place when correcting its own behavior; create a distinct subclass/component for a genuinely different experimental variant. Do not duplicate classes merely to avoid editing a small bug, or replace unrelated user implementations.
3. **Imports perform registration:** use explicit `--module <dotted.module>` flags, repeatable for trainer/dataset/evaluator/loss modules. Import the actual dependencies before building registered components. Do not recursively import every project module, download models on discovery, or invent registration success.
4. **Models:** the bundled `base/base_model.py` defines `BaseModel`, not `MODEL_REGISTRY`. Instantiate the project's real model in `build_model`; use a model registry only if that project actually defines one.
5. **No training by implication:** framework selection, code generation, config inspection and registry listing do not approve a run. Keep the caller's exact task/mode/budget, dataset protocol, original evidence and protected artifacts.

## Registry contract

| Registry | Actual source | Selection field |
|----------|---------------|-----------------|
| `TRAINER_REGISTRY` | `base/base_trainer.py` | `TRAINER.NAME` |
| `DATASET_REGISTRY` | `base/base_dataset.py` | `DATASET.NAME` |
| `EVALUATOR_REGISTRY` | `base/base_evaluator.py` | `EVALUATE.EVALUATOR` |
| `LOSS_REGISTRY` | `base/base_loss.py` | `LOSS.NAME` |

`utils.registry.Registry` uses class/function names. A decorator runs only when its module is imported. Unknown names must fail with the actual available registration context, not fall back to another model/trainer. `base/base_datamanager.py` supplies `DataManager` and data-loader helpers; it is not the location of `DATASET_REGISTRY`.

## Trainer lifecycle and real interfaces

`TrainerBase(cfg)` initializes system/device/logging; it does **not** automatically construct application data or models. A consumer constructor calls `super().__init__(cfg)`, then builds actual data/model/loss/optimizer state in its own required order.

| Interface | Correct use |
|-----------|-------------|
| `build_data_loader()` | Consumer setup method; assign real train/val/test loaders or appropriate project data manager |
| `build_model()` | Consumer setup method; construct model and optimizer, optional scheduler |
| `register_model(name, model, optim, sched)` | Register the actual model and separate optimizer/scheduler; never pass the optimizer in the model position |
| `forward_backward(batch)` | Compute a real loss against the plan's targets, update parameters and return observed loss scalars |
| `parse_batch(batch)` | Consumer helper called where needed; the core does not invent or automatically parse arbitrary data formats |
| `test(split=..., n_rounds=...)` | Consumer evaluation implementation matching the actual loop calls; the base method is abstract |
| `model_backward_and_update(loss, names=None)` | Existing checked backward/update/gradient clipping path |
| `build_optimizer(model, param_groups=None)` | Uses `cfg.OPTIM`; returns an optimizer |
| `build_lr_scheduler(optimizer)` | Uses configured supported scheduler settings; pass the optimizer, not a model |
| `write_scalar(tag, value, step)` / `write_meters(meters, prefix, step)` | Record actual observed values, on the appropriate process |

`train()` calls `before_train`, the iteration or epoch hooks and `after_train`. Iteration mode uses `next(train_loader)`, so provide an actual iterator/infinite loader; epoch mode uses a finite iterable with a valid length. Call superclass hooks when extending them so resume, logging and cleanup remain active.

Set positive save/evaluation/print intervals for the paths actually enabled. The entry point supplies a safe positive save default before YAML merging; explicit invalid settings must fail clearly, not be silently changed. Training completion is not evidence that a scientific criterion was met; use real evaluation artifacts and leave result interpretation to the execution/research workflow.

## Configuration and command precedence

Use the actual `BaseConfig().cfg` schema. Precedence is:

1. Core defaults with entry-point safety defaults.
2. The supplied YAML.
3. Explicit named CLI options such as `--trainer`.
4. Trailing YACS `KEY VALUE` overrides.

Declare genuinely new application settings in the supported schema or `ENV.EXTRA`; do not assume every arbitrary new nested CLI key exists. Read the actual model's pretrained configuration fields instead of copying a fictional `STAGE1_PATH` into another project.

Config paths, working directories and relative runtime paths belong to `CODE_ROOT`; use absolute paths when binding external data/artifacts. Keep command/config/source hashes with the caller's attempt. Configuration checking must not create output directories or start a trainer.

## Native entry point

Direct Python is supported; Bash is optional. Representative requests below assume the consumer really implements the named module/class and supplies the real YAML:

```text
python main.py --help
python main.py --config-file config/experiment.yaml --check-config
python main.py --module trainers.actual_trainer --list-trainers
python main.py --config-file config/experiment.yaml --module trainers.actual_trainer --mode train ENV.USE_CUDA False ENV.USE_WANDB False
python main.py --config-file config/experiment.yaml --module trainers.actual_trainer --mode train --resume ENV.USE_WANDB False
python main.py --config-file config/experiment.yaml --module trainers.actual_trainer --mode test --model-dir "<actual checkpoint source>" --load-iter 2 ENV.USE_CUDA False
```

Replace example module/config paths with discovered real files; never invoke an invented trainer. `--module` is repeatable. `--load-iter` and `--load-epoch` are mutually exclusive and must match the experiment's iteration/epoch convention. `debug` invokes the real training path under explicitly configured limits; it is not an unlimited extra experiment. There is no invented `analysis` dispatch.

Existing nonempty training output requires explicit `--resume` and valid compatible checkpoint artifacts. Never silently resume, erase an output directory, change the selected checkpoint or report a successful test without actually loading/evaluating it. A missing checkpoint or unsupported serialization/metadata format is a real error. Preserve original checkpoint bytes and the full failure; do not disable safe deserialization globally.

Checkpoints save model configuration as recursively plain dictionaries/lists/tuples and
load explicitly with `weights_only=True`; unknown serialized objects are rejected, not
retried with unsafe pickle. Validation metadata may be a real number or `None`, and is
logged honestly. The exact model directories and iteration/epoch names still apply.
Legacy checkpoints containing custom configuration objects are not silently converted;
report the incompatibility and obtain a separately authorized trusted migration if needed.

## Optional shell launcher

```text
bash scripts/run.sh --config-file config/experiment.yaml --module trainers.actual_trainer --mode train ENV.USE_CUDA False
bash scripts/run.sh --distributed 2 --config-file config/experiment.yaml --module trainers.actual_trainer --mode train
```

`PYTHON` can explicitly select an interpreter. Optional distributed count/master-port options configure the real torchrun path; default is one process, never a hard-coded three-GPU job. Use only allocated visible devices and explicit matching settings. Multi-stage experiments use the same entrypoint with their real config/checkpoint inputs, not a hard-coded fake predecessor. The launcher preserves argument boundaries, propagates failures and never cleans outputs. Use native Python when Bash is unavailable.

## Completion and handoff

After preparation/extension, report the actual code root, files changed, selected module/config/entrypoint, dependency/device requirements, concrete verification and remaining blockers. State separately whether initialization, implementation, an actual smoke run or a real authorized experiment completed. Never label copied assets as a completed trained model.

When acting under `research-run-experiment`, return these implementation facts to its main agent. It alone updates the shared tracker and decides whether the already authorized run can proceed or a fresh user decision is needed. Do not open a parallel progress database or automatically enter paper writing, submit artifacts, clone more repositories or expand data-source permissions.
