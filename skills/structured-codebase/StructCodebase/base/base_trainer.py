import time
import datetime
import shutil
import pickle
import random
import gc
import builtins
import sys
import numpy as np
import os
import os.path as osp
from loguru import logger
from functools import partial
from collections import OrderedDict, defaultdict

import torch
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.utils.tensorboard import SummaryWriter

from utils.registry import Registry
from utils.meters import AverageMeter
from utils.tools import tolist_if_not, mkdir_if_missing, check_availability

from utils.optim.optimizer import RAdam
from utils.optim.scheduler import ConstantWarmupScheduler, LinearWarmupScheduler, GradualWarmupScheduler


TRAINER_REGISTRY = Registry("TRAINER")

def build_trainer(cfg):
    avai_trainers = TRAINER_REGISTRY.registered_names()
    check_availability(cfg.TRAINER.NAME, avai_trainers)
    return TRAINER_REGISTRY.get(cfg.TRAINER.NAME)(cfg)

class TrainerBase:
    """Base class for iterative trainer."""

    def __init__(self, cfg):
        self._models = OrderedDict()
        self._optims = OrderedDict()
        self._scheds = OrderedDict()
        self._writer = None

        self.best_result = np.inf    # mini

        # Save as attributes some frequently used variables
        self.use_iters = cfg.TRAIN.USE_ITERS
        if self.use_iters:
            self.iter, self.start_iter = 0, cfg.TRAIN.START_ITER
            self.max_iters = cfg.TRAIN.MAX_ITERS
        else:
            self.epoch, self.start_epoch = 0, cfg.TRAIN.START_EPOCH
            self.max_epoch = cfg.TRAIN.MAX_EPOCHS

        self.output_dir = cfg.ENV.OUTPUT_DIR
        self.eval_step = 0
        self.cfg = cfg
        
        # Distributed training attributes
        self.is_distributed = False
        self.rank = 0
        self.world_size = 1
        self.local_rank = 0

        self.system_init()
        self.check_cfg()

    def check_cfg(self):
        """Print system info and env info.
        """
        logger.info('Collecting system info ...')
        logger.info(f"Project configuration:\n{self.cfg}")
        logger.info('Collecting env info ...')
        from torch.utils.collect_env import get_pretty_env_info
        # Code source: github.com/facebookresearch/maskrcnn-benchmark
        logger.info(f"Env information:\n{get_pretty_env_info()}")

    def system_init(self):
        # System Initialization
        # Initialize distributed training first
        if self.cfg.ENV.DISTRIBUTED:
            self._init_distributed()
        
        # Reconfigure logger for distributed training
        self._setup_distributed_logger()
        
        ## random seed setting
        if self.cfg.ENV.SEED >= 0:
            seed = self.cfg.ENV.SEED + self.rank  # Different seed for each process
            logger.info('Setting fixed seed: {} (base={}, rank={})'.format(seed, self.cfg.ENV.SEED, self.rank))
            random.seed(seed)
            np.random.seed(seed)
            torch.manual_seed(seed)
            torch.cuda.manual_seed_all(seed)

        ## cuda setting
        if torch.cuda.is_available() and self.cfg.ENV.USE_CUDA:
            torch.backends.cudnn.benchmark = True
            if self.is_distributed:
                # In distributed mode, use local_rank to determine GPU
                target_gpu = self.cfg.ENV.GPU[self.local_rank % len(self.cfg.ENV.GPU)]
            else:
                target_gpu = self.cfg.ENV.GPU[0]
                if len(self.cfg.ENV.GPU) > 1 and torch.distributed.is_available():
                    # assume torchrun/launch supplies LOCAL_RANK; fallback to rank % len(gpu_ids)
                    local_rank = int(os.environ.get("LOCAL_RANK", 0))
                    if torch.distributed.is_initialized():
                        local_rank = torch.distributed.get_rank() % len(self.cfg.ENV.GPU)
                    target_gpu = self.cfg.ENV.GPU[local_rank % len(self.cfg.ENV.GPU)]

            self.device = torch.device(f"cuda:{target_gpu}")
            torch.cuda.set_device(self.device)
            logger.info('Setting device to {}'.format(self.device))
        else:
            self.device = torch.device("cpu")
            logger.info('Setting device to {}'.format(self.device))
    
    def _init_distributed(self):
        """Initialize distributed training environment."""
        # Initialize process group first
        dist.init_process_group(
            backend=self.cfg.ENV.DIST_BACKEND,
            init_method=self.cfg.ENV.DIST_URL
        )
        self.rank = dist.get_rank()
        self.world_size = dist.get_world_size()
        self.is_distributed = True
        
        # Get local rank from environment variable (set by torchrun)
        # If not set, derive from rank (for compatibility with python -m torch.distributed.launch)
        self.local_rank = int(os.environ.get('LOCAL_RANK', self.rank % torch.cuda.device_count()))
        
        print(f"Initialized distributed training: rank={self.rank}, world_size={self.world_size}, local_rank={self.local_rank}")
    
    def _setup_distributed_logger(self):
        """Reconfigure logger for distributed training using loguru.
        
        This sets up the logger to automatically filter messages based on process rank.
        After this, you don't need to check is_main_process() before logging.
        """
        from loguru import logger as loguru_logger
        
        # Remove default handler
        loguru_logger.remove()
        loguru_logger.level("INFO", color="<white>")
        loguru_logger.level("DEBUG", color="<dim>")
        loguru_logger.level("WARNING", color="<bold><yellow>")
        loguru_logger.level("ERROR", color="<bold><red>")
        
        # Only add handler for main process (rank 0)
        if self.rank == 0:
            # Add colored output to stderr (for terminal display)
            loguru_logger.add(
                sys.stderr,
                format="[<green>{time:YYYY-MM-DD HH:mm:ss}</green> <cyan>{name}:{line}</cyan> <level>{level}</level>]=> <level>{message}</level>",
                level="INFO",
                colorize=True  # Always colorize stderr output
            )
            
            # Add plain text output to file (if output.log exists in output_dir)
            log_file = osp.join(self.output_dir, "output.log")
            loguru_logger.add(
                log_file,
                format="[{time:YYYY-MM-DD HH:mm:ss} {name}:{line} {level}]=> {message}",
                level="INFO",
                colorize=False,  # No color codes in file
                mode="a"  # Append mode
            )
        
        # Set as global logger (for compatibility with existing code)
        builtins.logger = loguru_logger
    
    def is_main_process(self):
        """Check if current process is the main process (rank 0)."""
        return self.rank == 0
        
    def register_model(self, name="model", model=None, optim=None, sched=None):
        if self.__dict__.get("_models") is None:
            raise AttributeError(
                "Cannot assign model before super().__init__() call"
            )

        if self.__dict__.get("_optims") is None:
            raise AttributeError(
                "Cannot assign optim before super().__init__() call"
            )

        if self.__dict__.get("_scheds") is None:
            raise AttributeError(
                "Cannot assign sched before super().__init__() call"
            )

        assert name not in self._models, "Found duplicate model names"

        self._models[name] = model
        self._optims[name] = optim
        self._scheds[name] = sched
    
    def wrap_model_with_ddp(self, model, find_unused_parameters=False, static_graph=False):
        """Wrap model with DistributedDataParallel.
        
        Args:
            model: The model to wrap
            find_unused_parameters: Whether to find unused parameters (useful for complex models)
            static_graph: If True, DDP knows the graph is static and will not check for unused parameters
                        after the first iteration. This can suppress warnings and improve performance.
        
        Returns:
            Wrapped model or original model if not distributed
        """
        if self.is_distributed:
            # Wrap with DDP
            model = DDP(
                model,
                device_ids=[self.local_rank],
                output_device=self.local_rank,
                find_unused_parameters=find_unused_parameters,
                static_graph=static_graph
            )
            logger.info(f"Model wrapped with DistributedDataParallel (local_rank={self.local_rank})")
        return model
    
    @property
    def model_module(self):
        """Get the actual model (unwrapped from DDP if necessary)."""
        return self.model.module if hasattr(self.model, 'module') else self.model
    
    def get_model_names(self, names=None):
        names_real = list(self._models.keys())
        if names is not None:
            names = tolist_if_not(names)
            for name in names:
                assert name in names_real
            return names
        else:
            return names_real

    def set_model_mode(self, mode="train", names=None):
        names = self.get_model_names(names)

        for name in names:
            if mode == "train":
                self._models[name].train()
            elif mode in ["test", "eval"]:
                self._models[name].eval()
            else:
                raise KeyError

    """Writer for TensorBoard.
        Functions:
            > init_writer
            > close_writer
            > write_scalar
    """
    def init_writer(self, extra_config=None):
        # Only initialize writer on main process
        if not self.is_main_process():
            return
            
        if self.__dict__.get("_writer") is None or self._writer is None:
            writer_dir = osp.join(self.output_dir, "tensorboard")
            mkdir_if_missing(writer_dir)
            logger.info(f"Initialize tensorboard (log_dir={writer_dir})")
            self._writer = SummaryWriter(log_dir=writer_dir)

        # Start a new wandb run to track this script.
        if self.cfg.ENV.USE_WANDB:
            import wandb
            wandb.login(key=self.cfg.ENV.WANDB.KEY)
            config = {"batch_size": self.cfg.DATALOADER.TRAIN.BATCH_SIZE,
                    "learning_rate": self.cfg.OPTIM.LR}
            config["steps"] = self.cfg.TRAIN.MAX_ITERS if self.cfg.TRAIN.USE_ITERS else self.cfg.TRAIN.MAX_EPOCHS
            if extra_config:
                config.update(extra_config)

            wandb_dir = osp.join(self.output_dir, "wandb")
            mkdir_if_missing(wandb_dir)
            logger.info(f"Initialize wandb (log_dir={wandb_dir})")
            self.wandb_run = wandb.init(
                name=self.cfg.ENV.WANDB.NAME,
                # Set the wandb entity where your project will be logged (generally your team name).
                entity=self.cfg.ENV.WANDB.ENTITY,
                # Set the wandb project where this run will be logged.
                project=self.cfg.ENV.WANDB.PROJECT,
                # Track hyperparameters and run metadata.
                config=config,
                notes=self.cfg.ENV.WANDB.NOTES,
                tags=self.cfg.ENV.WANDB.TAGS,
                dir=wandb_dir,
                mode=self.cfg.ENV.WANDB.MODE
            )

    def close_writer(self):
        if not self.is_main_process():
            return
            
        if self._writer is not None:
            self._writer.close()
        if self.cfg.ENV.USE_WANDB:
            # Finish the run and upload any remaining data.
            self.wandb_run.finish()

    # ==================== Distributed Training Utilities ====================
    
    def reduce_meter(self, meter, reduce_op='mean'):
        """Reduce an AverageMeter across all processes.
        
        Args:
            meter: An AverageMeter object with sum and count attributes.
            reduce_op: Reduction operation ('mean' or 'sum').
            
        Returns:
            The reduced average value.
        """
        if not self.is_distributed:
            return meter.avg if hasattr(meter, 'avg') else meter
        
        import torch.distributed as dist
        sum_tensor = torch.tensor([meter.sum], device=self.device, dtype=torch.float64)
        count_tensor = torch.tensor([meter.count], device=self.device, dtype=torch.float64)
        dist.all_reduce(sum_tensor, op=dist.ReduceOp.SUM)
        dist.all_reduce(count_tensor, op=dist.ReduceOp.SUM)
        
        if reduce_op == 'mean' and count_tensor.item() > 0:
            return sum_tensor.item() / count_tensor.item()
        elif reduce_op == 'sum':
            return sum_tensor.item()
        return 0.0
    
    def reduce_meters(self, meters_dict, reduce_op='mean'):
        """Reduce a dictionary of AverageMeter objects across all processes.
        
        Args:
            meters_dict: A dict of {name: AverageMeter}.
            reduce_op: Reduction operation ('mean' or 'sum').
            
        Returns:
            A dict of {name: reduced_value}.
        """
        if not self.is_distributed:
            return {k: v.avg for k, v in meters_dict.items()}
        
        import torch.distributed as dist
        # Batch all reductions for efficiency
        keys = list(meters_dict.keys())
        sums = torch.tensor([meters_dict[k].sum for k in keys], device=self.device, dtype=torch.float64)
        counts = torch.tensor([meters_dict[k].count for k in keys], device=self.device, dtype=torch.float64)
        
        dist.all_reduce(sums, op=dist.ReduceOp.SUM)
        dist.all_reduce(counts, op=dist.ReduceOp.SUM)
        
        results = {}
        for i, k in enumerate(keys):
            if reduce_op == 'mean' and counts[i].item() > 0:
                results[k] = sums[i].item() / counts[i].item()
            elif reduce_op == 'sum':
                results[k] = sums[i].item()
            else:
                results[k] = 0.0
        return results
    
    def reduce_value(self, value, reduce_op='mean', count=1):
        """Reduce a scalar value across all processes.
        
        Args:
            value: A scalar value.
            reduce_op: Reduction operation ('mean' or 'sum').
            count: The count for averaging (default 1).
            
        Returns:
            The reduced value.
        """
        if not self.is_distributed:
            return value
        
        import torch.distributed as dist
        tensor = torch.tensor([value, count], device=self.device, dtype=torch.float64)
        dist.all_reduce(tensor, op=dist.ReduceOp.SUM)
        
        if reduce_op == 'mean' and tensor[1].item() > 0:
            return tensor[0].item() / tensor[1].item()
        elif reduce_op == 'sum':
            return tensor[0].item()
        return value
    
    def barrier(self):
        """Synchronize all processes. Call this when all processes need to wait for each other."""
        if self.is_distributed:
            import torch.distributed as dist
            dist.barrier()
    
    def broadcast_value(self, value, src=0):
        """Broadcast a scalar value from source process to all other processes.
        
        Args:
            value: The scalar value to broadcast (only meaningful on src process).
            src: The source rank to broadcast from (default: 0, main process).
            
        Returns:
            The broadcasted value on all processes.
        """
        if not self.is_distributed:
            return value
        
        import torch.distributed as dist
        tensor = torch.tensor([value], device=self.device, dtype=torch.float64)
        dist.broadcast(tensor, src=src)
        return tensor.item()
            
    def write_scalar(self, tag, scalar_value, global_step=None):
        if not self.is_main_process():
            return
            
        if self._writer is not None:
            self._writer.add_scalar(tag, scalar_value, global_step)

        if self.cfg.ENV.USE_WANDB:
            self.wandb_run.log({tag: scalar_value})
    
    def write_meters(self, meters, prefix="", global_step=None, reduce_op='mean'):
        """
        Convenience method to reduce meters across processes and write to tensorboard/wandb.
        
        Args:
            meters (dict): Dictionary of AverageMeter objects
            prefix (str): Prefix for scalar tags (e.g., "train/", "val/")
            global_step (int, optional): Global step for logging
            reduce_op (str): Reduction operation ('mean' or 'sum')
            
        Example:
            self.write_meters(loss_meter, prefix="val/loss_", global_step=self.iter)
        """
        # Reduce meters across all processes (all processes participate)
        reduced_meters = self.reduce_meters(meters, reduce_op=reduce_op)
        
        # Only write to tensorboard/wandb on main process
        if self.is_main_process():
            for name, value in reduced_meters.items():
                tag = f"{prefix}{name}"
                self.write_scalar(tag, value, global_step=global_step)
        
        return reduced_meters
            
    """Train model with a generic training loop.
        Functions:
            > train
            > before_train
            > after_train
            > before_epoch
            > after_epoch
            > run_epoch
            > parse_batch_train
    """
    def train(self):
        """Generic training loops.
        """
        self.before_train()
        if self.use_iters:
            assert self.max_iters is not None, "max_iters must be specified when use_iters=True"
            for self.iter in range(self.start_iter, self.max_iters):
                self.before_iter()
                self.run_iter()
                self.after_iter()
        else:
            assert self.max_epoch is not None, "max_epoch must be specified"
            for self.epoch in range(self.start_epoch, self.max_epoch):
                self.before_epoch()
                self.run_epoch()
                self.after_epoch()

        self.after_train()

    def before_train(self):
        directory = self.output_dir
        if self.cfg.ENV.RESUME:
            directory = self.cfg.ENV.RESUME
        if self.use_iters:
            self.start_iter = self.resume_model_if_exist(directory)
        else:
            self.start_epoch = self.resume_model_if_exist(directory)

        # Free transient CUDA allocations created during checkpoint restore.
        self.cleanup_cuda_memory(reason="post-resume")

        # Initialize summary writer
        self.init_writer()

        # Remember the starting time (for computing the elapsed time)
        self.time_start = time.time()

    def after_train(self):
        logger.info("Finish training!")

        do_test = not self.cfg.TEST.NO_TEST
        if do_test:
            if self.cfg.TEST.FINAL_MODEL == "best_val":
                logger.info("Deploy the model with the best val performance")
                self.load_model(self.output_dir)
            else:
                step_info = "iter" if self.use_iters else "epoch"
                logger.info(f"Deploy the last-{step_info} model")
            self.test()

        # Show elapsed time
        elapsed = round(time.time() - self.time_start)
        elapsed = str(datetime.timedelta(seconds=elapsed))
        logger.info(f"Elapsed: {elapsed}")

        # Close writer
        self.close_writer()
        
        # Clean up distributed training
        if self.is_distributed:
            dist.destroy_process_group()

    def before_epoch(self):
        self.set_model_mode("train")
        self.batch_time = AverageMeter()
        self.data_time = AverageMeter()
        self.loss_meter = defaultdict(AverageMeter)
        self.acc_meter = defaultdict(AverageMeter)
    
    def before_iter(self):
        self.set_model_mode("train")
        self.batch_time = AverageMeter()
        self.data_time = AverageMeter()
        self.loss_meter = defaultdict(AverageMeter)
        self.acc_meter = defaultdict(AverageMeter)

    def after_epoch(self):
        """Actions after each epoch"""
        
        # update learning rate
        if ((self.epoch + 1) % self.cfg.OPTIM.LR_UPDATE_FREQ == 0):
            self.update_lr()

        last_epoch = (self.epoch + 1) == self.max_epoch
        if self.cfg.TRAIN.EVALUATE and self.is_main_process():
            if ((self.epoch + 1) % self.cfg.TRAIN.EVAL_FREQ == 0) or last_epoch:
                self.test(split="val")
        
        # Save checkpoint (only on main process)
        if self.is_main_process():
            if ((self.epoch + 1) % self.cfg.TRAIN.SAVE_FREQ == 0) or last_epoch:
                self.save_model(epoch=self.epoch, directory=self.output_dir)

    def after_iter(self):
        last_iter = (self.iter + 1) == self.max_iters
        is_best, val_result = False, self.best_result
        
        # update learning rate
        if ((self.iter + 1) % self.cfg.OPTIM.LR_UPDATE_FREQ == 0):
            self.update_lr()

        # Validation
        # NOTE: validation (test) must run on all ranks to avoid deadlock if distributed
        if self.cfg.TRAIN.EVALUATE:
            if ((self.iter + 1) % self.cfg.TRAIN.EVAL_FREQ == 0) or last_iter:
                val_result = self.test(split="val", n_rounds=self.cfg.TRAIN.EVAL_ROUND)
    
                # Save the best result (only on main process)
                if self.is_main_process():
                    is_best = val_result < self.best_result
                    if is_best:
                        self.best_result = val_result
                        logger.info(f"*** Found better model with total loss: {val_result:.4f} ***")
        
        # Save checkpoint (only on main process)
        if self.is_main_process():
            if ((self.iter + 1) % self.cfg.TRAIN.SAVE_FREQ == 0) or last_iter or is_best:
                # Save model checkpoint
                self.save_model(iter=self.iter, directory=self.output_dir, is_best=is_best, val_result=val_result)

    def run_epoch(self):
        """Run one training epoch."""
        self.num_batches = len(self.train_loader)
        end_time = time.time()
        for self.batch_id, batch in enumerate(self.train_loader):
            self.data_time.update(time.time() - end_time)
            loss_dict = self.forward_backward(batch)
            self.batch_time.update(time.time() - end_time)
        
            for k, v in loss_dict.items():
                self.loss_meter[k].update(v)

            # Logging
            nb_remain = self.num_batches - self.batch_id - 1
            nb_remain += (self.max_epoch - self.epoch - 1) * self.num_batches
            eta_seconds = self.batch_time.avg * nb_remain
            eta = str(datetime.timedelta(seconds=int(eta_seconds)))
            if (self.batch_id + 1) % self.cfg.TRAIN.PRINT_FREQ == 0:
                info = []
                info += [f"epoch [{self.epoch + 1}/{self.max_epoch}]"]
                info += [f"batch [{self.batch_id + 1}/{self.num_batches}]"]
                info += [f"time {self.batch_time.val:.3f} ({self.batch_time.avg:.3f})"]
                info += [f"data {self.data_time.val:.3f} ({self.data_time.avg:.3f})"]
                info += [f"{item} {loss.val:.4f}" for item, loss in self.loss_meter.items()]
                info += [f"lr {self.get_current_lr():.4e}"]
                info += [f"eta {eta}"]
                logger.info(" ".join(info))
            
            n_iter = self.epoch * self.num_batches + self.batch_id
            for item, loss in self.loss_meter.items():
                self.write_scalar(f"train/loss_{item}", loss.avg, n_iter)
            self.write_scalar("train/lr", self.get_current_lr(), n_iter)
            end_time = time.time()
    
    def run_iter(self):
        # Load data
        end_time = time.time()
        batch = next(self.train_loader)
        self.data_time.update(time.time() - end_time)
        loss_dict = self.forward_backward(batch)
        self.batch_time.update(time.time() - end_time)

        for k, v in loss_dict.items():
            self.loss_meter[k].update(v)

        eta_seconds = self.batch_time.avg * (self.max_iters - self.iter)
        eta = str(datetime.timedelta(seconds=int(eta_seconds)))
        
        # Aggregate loss values across all processes
        reduced_losses = self.reduce_meters(self.loss_meter)
        # Reduce loss meters across all processes for logging and tensorboard
        if (self.iter + 1) % self.cfg.TRAIN.PRINT_FREQ == 0:
            info = []
            info += [f"iter [{self.iter + 1}/{self.max_iters}]"]
            info += [f"time {self.batch_time.val:.3f} ({self.batch_time.avg:.3f})"]
            info += [f"data {self.data_time.val:.3f} ({self.data_time.avg:.3f})"]
            info += [f"{item} {loss:.4f}" for item, loss in reduced_losses.items()]
            info += [f"lr {self.get_current_lr():.4e}"]
            info += [f"eta {eta}"]
            logger.info(" ".join(info))
            
        # Write reduced losses to tensorboard (write_scalar already checks is_main_process)
        for item, loss in reduced_losses.items():
            self.write_scalar(f"train/loss_{item}", loss, self.iter)
        self.write_scalar("train/lr", self.get_current_lr(), self.iter)

    def parse_batch_train(self, batch):
        raise NotImplementedError

    """Test model with a generic testing loop.
        Functions:
            > test
            > parse_batch_test
    """
    def test(self):
        raise NotImplementedError

    def parse_batch_test(self, batch):
        raise NotImplementedError

    """Model update with a generic forward-backward loop.
        Functions:
            > build_loss_metrics
            > forward_backward
            > model_inference
            > model_zero_grad
            > model_backward
            > model_update
            > update_lr
            > model_backward_and_update
            > detect_anomaly
    """

    def forward_backward(self, batch):
        raise NotImplementedError

    def model_zero_grad(self, names=None):
        names = self.get_model_names(names)
        for name in names:
            if self._optims[name] is not None:
                self._optims[name].zero_grad()

    def model_backward(self, loss):
        self.detect_anomaly(loss)
        loss.backward()

    def model_update(self, names=None):
        names = self.get_model_names(names)
        for name in names:
            if self._optims[name] is not None:
                self._optims[name].step()

    def update_lr(self, names=None):
        names = self.get_model_names(names)

        for name in names:
            if self._scheds[name] is not None:
                self._scheds[name].step()

    def model_backward_and_update(self, loss, names=None):
        self.model_zero_grad(names)
        self.model_backward(loss)
        # Apply gradient clipping to prevent exploding gradients
        self.clip_gradients(names)

        self.model_update(names)

    def clip_gradients(self, names=None):
        """Apply gradient clipping to prevent exploding gradients."""
        names = self.get_model_names(names)
        max_norm = getattr(self.cfg.TRAIN, 'GRAD_CLIP', 1.0)  # Default gradient clip value

        for name in names:
            if self._models[name] is not None:
                torch.nn.utils.clip_grad_norm_(self._models[name].parameters(), max_norm)

    def detect_anomaly(self, loss):
        if not torch.isfinite(loss).all():
            # Log additional information for debugging
            logger.error(f"Loss contains NaN or inf values: {loss}")
            if hasattr(loss, 'item'):
                logger.error(f"Loss value: {loss.item()}")
            raise FloatingPointError("Loss is infinite or NaN!")

    def build_optimizer(self, model, param_groups=None):
        """A function wrapper for building an optimizer.

        Args:
            model (nn.Module or iterable): model.
            optim_cfg (CfgNode): optimization config.
            param_groups: If provided, directly optimize param_groups and abandon model
        """
        AVAI_OPTIMS = ["adam", "amsgrad", "sgd", "rmsprop", "radam", "adamw"]
        optim_cfg = self.cfg.OPTIM
        optim, lr, weight_decay = optim_cfg.NAME, optim_cfg.LR, optim_cfg.WEIGHT_DECAY
        adam_beta1, adam_beta2 = optim_cfg.ADAM_BETA1, optim_cfg.ADAM_BETA2
        momentum, rmsprop_alpha = optim_cfg.MOMENTUM, optim_cfg.RMSPROP_ALPHA
        sgd_dampening, sgd_nesterov = optim_cfg.SGD_DAMPNING, optim_cfg.SGD_NESTEROV

        assert optim in AVAI_OPTIMS, ValueError(f"optim must be one of {AVAI_OPTIMS}, but got {optim}")
        if param_groups == None:
            param_groups = filter(lambda p: p.requires_grad, model.parameters())

        if optim == "adam":
            optimizer = torch.optim.Adam(param_groups, lr=lr)
        elif optim == "amsgrad":
            optimizer = torch.optim.Adam(param_groups, lr=lr, weight_decay=weight_decay,
                                        betas=(adam_beta1, adam_beta2), amsgrad=True)
        elif optim == "sgd":
            optimizer = torch.optim.SGD(param_groups, lr=lr, momentum=momentum, weight_decay=weight_decay,
                                        dampening=sgd_dampening, nesterov=sgd_nesterov)
        elif optim == "rmsprop":
            optimizer = torch.optim.RMSprop(param_groups, lr=lr, momentum=momentum,
                                        weight_decay=weight_decay, alpha=rmsprop_alpha)
        elif optim == "radam":
            optimizer = RAdam(param_groups, lr=lr, weight_decay=weight_decay, betas=(adam_beta1, adam_beta2))
        elif optim == "adamw":
            optimizer = torch.optim.AdamW(param_groups, lr=lr, weight_decay=weight_decay,
                                        betas=(adam_beta1, adam_beta2))
        else:
            raise NotImplementedError(f"Optimizer {optim} not implemented yet!")

        return optimizer
    
    def build_lr_scheduler(self, optimizer):
        """A function wrapper for building a learning rate scheduler.

        Args:
            optimizer (Optimizer): an Optimizer.
            optim_cfg (CfgNode): optimization config.
        """
        AVAI_SCHEDS = ["single_step", "multi_step", "cosine", "gradual", "gradualThenDecay"]
        optim_cfg = self.cfg.OPTIM
        step_size, gamma, lr_scheduler = optim_cfg.STEP_SIZE, optim_cfg.GAMMA, optim_cfg.LR_SCHEDULER
        min_lr, warmup_step = optim_cfg.MIN_LR_RATIO * optim_cfg.LR, optim_cfg.WARMUP_STEP
        if self.cfg.OPTIM.MAX_STEP > 0:
            training_step = self.cfg.OPTIM.MAX_STEP
        else:
            training_step = self.max_iters if self.use_iters else self.max_epoch

        assert lr_scheduler in AVAI_SCHEDS, ValueError(f"scheduler must be one of {AVAI_SCHEDS}, but got {lr_scheduler}")
        if lr_scheduler == "single_step":
            assert isinstance(step_size, int), TypeError(f"For single_step lr_scheduler, step_size must be an integer, but got {type(step_size)}")
            step_size = training_step if step_size <= 0 else step_size
            scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=step_size, gamma=gamma)
        elif lr_scheduler == "multi_step":
            assert isinstance(step_size, (list, tuple)), TypeError(f"For multi_step lr_scheduler, step_size must be a list, but got {type(step_size)}")
            scheduler = torch.optim.lr_scheduler.MultiStepLR(optimizer, milestones=step_size, gamma=gamma)
        elif lr_scheduler == "cosine":
            scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, training_step, min_lr)
        elif lr_scheduler == "warmup":
            scheduler = GradualWarmupScheduler(optimizer, optim_cfg.MULTIPLIER, warmup_step)
        
        if warmup_step > 0:   # assume first warmup then training scheduler
            if optim_cfg.WARMUP_TYPE == "constant":
                scheduler = ConstantWarmupScheduler(optimizer, scheduler, warmup_step, optim_cfg.LR)
            elif optim_cfg.WARMUP_TYPE == "linear":
                scheduler = LinearWarmupScheduler(optimizer, scheduler, warmup_step, min_lr)
            elif optim_cfg.WARMUP_TYPE == "gradual":
                scheduler = GradualWarmupScheduler(optimizer, optim_cfg.MULTIPLIER, warmup_step, scheduler)
        return scheduler
    
    def get_current_lr(self, names=None):
        """Get current learning rate."""
        names = self.get_model_names(names)
        name = names[0]
        return self._optims[name].param_groups[0]["lr"]
    
    """Save the model at a given directory.
        Functions:
            > save_model
            > save_checkpoint
    """
    def save_model(
        self, iter=None, epoch=None, directory=None, is_best=False, val_result=None, model_name=""
    ):
        # Only save on main process
        if not self.is_main_process():
            return
            
        names = self.get_model_names()
        # Determine which model to load
        step_info = "iter" if self.use_iters else "epoch"
        step = iter if self.use_iters else epoch
        for name in names:
            # Get model state dict, unwrap DDP if necessary
            model = self._models[name]
            if isinstance(model, DDP):
                model_dict = model.module.state_dict()
            else:
                model_dict = model.state_dict()

            optim_dict = None
            if self._optims[name] is not None:
                optim_dict = self._optims[name].state_dict()

            sched_dict = None
            if self._scheds[name] is not None:
                sched_dict = self._scheds[name].state_dict()
            
            self.save_checkpoint(
                {
                    "state_dict": model_dict,
                    "model_config": self.cfg.MODEL,
                    f"{step_info}": step + 1,
                    "optimizer": optim_dict,
                    "scheduler": sched_dict,
                    "val_result": val_result
                },
                osp.join(directory, name),
                is_best=is_best,
                model_name=model_name,
            )

    def save_checkpoint(
        self,
        state,
        save_dir,
        is_best=False,
        remove_module_from_keys=True,
        model_name=""
    ):
        r"""Save checkpoint.

        Args:
            state (dict): dictionary.
            save_dir (str): directory to save checkpoint.
            is_best (bool, optional): if True, this checkpoint will be copied and named
                ``model-best.pth.tar``. Default is False.
            remove_module_from_keys (bool, optional): whether to remove "module."
                from layer names. Default is True.
            model_name (str, optional): model name to save.
        """
        mkdir_if_missing(save_dir)

        if remove_module_from_keys:
            # remove 'module.' in state_dict's keys
            state_dict = state["state_dict"]
            new_state_dict = OrderedDict()
            for k, v in state_dict.items():
                if k.startswith("module."):
                    k = k[7:]
                new_state_dict[k] = v
            state["state_dict"] = new_state_dict

        # save model
        step = state["epoch"] if "epoch" in state else state["iter"]
        step_info = "epoch" if "epoch" in state else "iter"
        if not model_name:
            model_name = f"model.pth.tar-{step_info}-" + str(step)
        fpath = osp.join(save_dir, model_name)
        torch.save(state, fpath)
        logger.info(f"Checkpoint saved to {fpath}")

        # save current model name
        checkpoint_file = osp.join(save_dir, "checkpoint")
        checkpoint = open(checkpoint_file, "w+")
        checkpoint.write("{}\n".format(osp.basename(fpath)))
        checkpoint.close()

        if is_best:
            best_fpath = osp.join(osp.dirname(fpath), "model-best.pth.tar")
            shutil.copy(fpath, best_fpath)
            logger.info('Best checkpoint saved to "{}"'.format(best_fpath))

    """Load a checkpoint from a given directory.
        Functions:
            > load_model
            > load_checkpoint
            > load_pretrained_weights
    """
    def load_model(self, directory, epoch=None, iter=None, load_model=True):
        if not directory:
            logger.warning(
                "Note that load_model() is skipped as no pretrained "
                "model is given (ignore this if it's done on purpose)"
            )

        names = self.get_model_names()

        # By default, the best model is loaded
        model_file = "model-best.pth.tar"

        # Determine which model to load
        step_info = "iter" if self.use_iters else "epoch"
        step = iter if self.use_iters else epoch
        if step is not None:
            model_file = f"model.pth.tar-{step_info}-" + str(step)

        models_config, models_state_dict = {}, {}
        for name in names:
            model_path = osp.join(directory, name, model_file)

            if not osp.exists(model_path):
                raise FileNotFoundError(f"No model at {model_path}")

            checkpoint = self.load_checkpoint(model_path)
            state_dict = checkpoint["state_dict"]
            step = checkpoint[step_info]
            val_result = checkpoint["val_result"]
            model_config = checkpoint["model_config"]
            logger.info(f"Load {model_path} to {name} ({step_info}={step}, val_result={val_result:.1f})")
            # Load state dict to model, handle DDP wrapper
            model = self._models[name]
            if isinstance(model, DDP):
                model.module.load_state_dict(state_dict)
            else:
                model.load_state_dict(state_dict)

            models_config[name] = model_config
            models_state_dict[name] = state_dict
        
        if not load_model:
            return models_config, models_state_dict

    def load_checkpoint(self, fpath):
        r"""Load checkpoint.

        ``UnicodeDecodeError`` can be well handled, which means
        python2-saved files can be read from python3.

        Args:
            fpath (str): path to checkpoint.

        Returns:
            dict

        Examples::
            >>> fpath = 'log/my_model/model.pth.tar-10'
            >>> checkpoint = load_checkpoint(fpath)
        """
        if fpath is None:
            raise ValueError("File path is None")

        if not osp.exists(fpath):
            raise FileNotFoundError('File is not found at "{}"'.format(fpath))

        # Always load checkpoints on CPU first to avoid transient GPU peaks.
        map_location = "cpu"

        try:
            checkpoint = torch.load(fpath, map_location=map_location)

        except UnicodeDecodeError:
            pickle.load = partial(pickle.load, encoding="latin1")
            pickle.Unpickler = partial(pickle.Unpickler, encoding="latin1")
            checkpoint = torch.load(
                fpath, pickle_module=pickle, map_location=map_location
            )

        except Exception:
            logger.error('Unable to load checkpoint from "{}"'.format(fpath))
            raise

        return checkpoint

    def cleanup_cuda_memory(self, reason=""):
        if not torch.cuda.is_available():
            return

        # Ensure pending kernels finish before trying to release cached blocks.
        torch.cuda.synchronize(self.device)
        gc.collect()
        torch.cuda.empty_cache()
        try:
            torch.cuda.ipc_collect()
        except RuntimeError:
            # ipc_collect may fail in some runtime states; empty_cache has already run.
            pass

        if reason:
            logger.info(f"CUDA memory cleanup done ({reason})")

    def load_pretrained_weights(self, model, weight_path):
        r"""Load pretrianed weights to model.

        Features::
            - Incompatible layers (unmatched in name or size) will be ignored.
            - Can automatically deal with keys containing "module.".

        Args:
            model (nn.Module): network model.
            weight_path (str): path to pretrained weights.

        Examples::
            >>> weight_path = 'log/my_model/model-best.pth.tar'
            >>> load_pretrained_weights(model, weight_path)
        """
        checkpoint = self.load_checkpoint(weight_path)
        if "state_dict" in checkpoint:
            state_dict = checkpoint["state_dict"]
        else:
            state_dict = checkpoint

        model_dict = model.state_dict()
        new_state_dict = OrderedDict()
        matched_layers, discarded_layers = [], []

        for k, v in state_dict.items():
            if k.startswith("module."):
                k = k[7:]  # discard module.

            if k in model_dict and model_dict[k].size() == v.size():
                new_state_dict[k] = v
                matched_layers.append(k)
            else:
                discarded_layers.append(k)

        model_dict.update(new_state_dict)
        model.load_state_dict(model_dict)

        if len(matched_layers) == 0:
            logger.warning(
                f"Cannot load {weight_path} (check the key names manually)"
            )
        else:
            logger.info(f"Successfully loaded pretrained weights from {weight_path}")
            if len(discarded_layers) > 0:
                logger.info(
                    f"Layers discarded due to unmatched keys or size: {discarded_layers}"
                )

    """Resume model training from a checkpoint if it exists.
        Functions:
            > resume_model_if_exist
            > resume_from_checkpoint
    """
    def resume_model_if_exist(self, directory):
        names = self.get_model_names()
        file_missing = False

        for name in names:
            path = osp.join(directory, name)
            if not osp.exists(path):
                file_missing = True
                break

        if file_missing:
            logger.warning("No checkpoint found, train from scratch")
            return 0

        logger.info(f"Found checkpoint at {directory} (will resume training)")

        for name in names:
            path = osp.join(directory, name)
            start_step = self.resume_from_checkpoint(
                path, self._models[name], self._optims[name],
                self._scheds[name]
            )

        return start_step

    def resume_from_checkpoint(self, fdir, model, optimizer=None, scheduler=None):
        r"""Resume training from a checkpoint.

        This will load (1) model weights and (2) ``state_dict``
        of optimizer if ``optimizer`` is not None.

        Args:
            fdir (str): directory where the model was saved.
            model (nn.Module): model.
            optimizer (Optimizer, optional): an Optimizer.
            scheduler (Scheduler, optional): an Scheduler.

        Returns:
            int: start_step.

        Examples::
            >>> fdir = 'log/my_model'
            >>> start_step = resume_from_checkpoint(fdir, model, optimizer, scheduler)
        """
        with open(osp.join(fdir, "checkpoint"), "r") as checkpoint:
            model_name = checkpoint.readlines()[0].strip("\n")
            fpath = osp.join(fdir, model_name)

        logger.info('Loading checkpoint from "{}"'.format(fpath))
        checkpoint = self.load_checkpoint(fpath)
        
        # Handle DDP module prefix mismatch
        state_dict = checkpoint["state_dict"]
        model_state_dict = model.state_dict()
        
        # Check if there's a module prefix mismatch
        checkpoint_has_module = any(k.startswith('module.') for k in state_dict.keys())
        model_has_module = any(k.startswith('module.') for k in model_state_dict.keys())
        
        if checkpoint_has_module != model_has_module:
            logger.info(f"Detected module prefix mismatch (checkpoint: {checkpoint_has_module}, model: {model_has_module})")
            new_state_dict = {}
            
            if checkpoint_has_module and not model_has_module:
                # Remove 'module.' prefix from checkpoint
                logger.info("Removing 'module.' prefix from checkpoint keys")
                for k, v in state_dict.items():
                    new_key = k[7:] if k.startswith('module.') else k
                    new_state_dict[new_key] = v
            elif not checkpoint_has_module and model_has_module:
                # Add 'module.' prefix to checkpoint
                logger.info("Adding 'module.' prefix to checkpoint keys")
                for k, v in state_dict.items():
                    new_key = f'module.{k}' if not k.startswith('module.') else k
                    new_state_dict[new_key] = v
            
            state_dict = new_state_dict
        
        model.load_state_dict(state_dict)
        logger.info("Loaded model weights")

        if optimizer is not None and "optimizer" in checkpoint.keys():
            optimizer.load_state_dict(checkpoint["optimizer"])
            logger.info("Loaded optimizer")

        if scheduler is not None and "scheduler" in checkpoint.keys():
            scheduler.load_state_dict(checkpoint["scheduler"])
            logger.info("Loaded scheduler")

        start_step = checkpoint["epoch"] if "epoch" in checkpoint else checkpoint["iter"]
        start_info = "epoch" if "epoch" in checkpoint else "iter"
        logger.info(f"Previous {start_info}: {start_step}")

        # Drop temporary checkpoint object ASAP to reduce peak memory after restore.
        del checkpoint

        return start_step
    
    """Some tools for parameters calculation.
        Functions:
            > count_num_param
    """
    def count_num_param(self, model=None, params=None):
        r"""Count number of parameters in a model.

        Args:
            model (nn.Module): network model.
            params: network model`s params.
        Examples::
            >>> model_size = count_num_param(model)
        """
        if model is not None:
            total_params = sum(p.numel() for p in model.parameters())
            trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
            return (total_params, trainable_params)

        if params is not None:
            s = 0
            for p in params:
                if isinstance(p, dict):
                    s += p["params"].numel()
                else:
                    s += p.numel()
            return s

        raise ValueError("model and params must provide at least one.")