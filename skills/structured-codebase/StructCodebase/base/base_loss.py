import torch
import torch.nn as nn
import torch.nn.functional as F
from utils.registry import Registry
from utils.tools import check_availability
import logging
logger: logging.Logger

LOSS_REGISTRY = Registry("LOSS")
def build_loss(cfg, *args, **kwargs):
    """
    Build loss module from config.
    """
    avai_losses = LOSS_REGISTRY.registered_names()
    check_availability(cfg.LOSS.NAME, avai_losses)
    if cfg.ENV.VERBOSE:
        logger.info("Using loss: {}".format(cfg.LOSS.NAME))
    return LOSS_REGISTRY.get(cfg.LOSS.NAME)(cfg.LOSS, *args, **kwargs)

@LOSS_REGISTRY.register()
class L1Loss(nn.Module):
    def __init__(self, cfg):
        super().__init__()

    def forward(self, pred, target):
        return F.l1_loss(pred, target)
    
@LOSS_REGISTRY.register()
class L2Loss(nn.Module):
    def __init__(self, cfg):
        super().__init__()

    def forward(self, pred, target):
        return F.mse_loss(pred, target)