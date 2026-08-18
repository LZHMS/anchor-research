import numpy as np
import torch.nn as nn
import torch.nn.functional as F

from utils.registry import Registry
from utils.tools import check_availability
from utils.loss import calc_vq_loss, calc_logit_loss, nt_xent_loss

import logging
logger: logging.Logger

EVALUATOR_REGISTRY = Registry("EVALUATOR")


def build_evaluator(cfg, *args, **kwargs):
    avai_evaluators = EVALUATOR_REGISTRY.registered_names()
    check_availability(cfg.EVALUATE.EVALUATOR, avai_evaluators)
    if cfg.ENV.VERBOSE:
        logger.info("Loading evaluator: {}".format(cfg.EVALUATE.EVALUATOR))
    return EVALUATOR_REGISTRY.get(cfg.EVALUATE.EVALUATOR)(cfg.EVALUATE, *args, **kwargs)  

class EvaluatorBase(nn.Module):
    """Base evaluator."""

    def __init__(self, cfg):
        super().__init__()
        self.cfg = cfg

    def reset(self):
        """
        Reset evaluator state for new evaluation sequence.
        """
        pass

    def process(self, mo, gt):
        raise NotImplementedError

    def forward(self):
        raise NotImplementedError

    def compute_mod(self, vertices_gt, vertices_pred):
        """
        Calculate Mouth Opening Deviation (MOD).
        
        This metric specifically evaluates the accuracy of mouth opening magnitude.
        
        Args:
            vertices_gt (np.ndarray): Ground truth vertices (T, V, 3).
            vertices_pred (np.ndarray): Predicted vertices (T, V, 3).
            
        Returns:
            float: The mean MOD value over the sequence (in meters if input is meters).
        """
        # 1. Extract paired landmarks for mouth opening (T, N_pairs, 3)
        gt_top = vertices_gt[:, self.mod_top_indices, :]
        gt_bottom = vertices_gt[:, self.mod_bottom_indices, :]

        pred_top = vertices_pred[:, self.mod_top_indices, :]
        pred_bottom = vertices_pred[:, self.mod_bottom_indices, :]

        # 2. Calculate opening distance for each pair (T, N_pairs) - Euclidean distance
        dist_gt = np.linalg.norm(gt_top - gt_bottom, axis=2)
        dist_pred = np.linalg.norm(pred_top - pred_bottom, axis=2)

        # 3. Calculate "average opening" scalar for each frame (T,)
        # By averaging center (larger) and side (smaller) points, we get a regional average
        opening_scalar_gt = np.mean(dist_gt, axis=1)
        opening_scalar_pred = np.mean(dist_pred, axis=1)

        # 4. Calculate sequence mean absolute error
        mod_per_frame = np.abs(opening_scalar_gt - opening_scalar_pred)
        return np.mean(mod_per_frame)

    def compute_fdd(self, vertices_gt, vertices_pred, upper_map):
        """
        Calculate Facial Dynamics Deviation (FDD), specifically for upper face.
        
        This metric evaluates the variation/dynamics of the upper face motion.
        
        Args:
            vertices_gt (np.ndarray): Ground truth vertices (T, V, 3).
            vertices_pred (np.ndarray): Predicted vertices (T, V, 3).
            upper_map (list): Indices of vertices belonging to the upper face region.
            
        Returns:
            float: The absolute difference in motion standard deviation between GT and prediction.
        """
        motion_pred = vertices_pred - self.template.reshape(1, -1, 3)
        motion_gt = vertices_gt - self.template.reshape(1, -1, 3)

        upper_motion_gt_norm = np.linalg.norm(motion_gt[:, upper_map, :], axis=2)
        upper_motion_pred_norm = np.linalg.norm(motion_pred[:, upper_map, :], axis=2)

        # Calculate standard deviation of motion magnitude across time
        gt_motion_std = np.mean(np.std(upper_motion_gt_norm, axis=0))
        pred_motion_std = np.mean(np.std(upper_motion_pred_norm, axis=0))

        return np.abs(gt_motion_std - pred_motion_std)

    def compute_lve(self, vertices_gt, vertices_pred, mouth_map):
        """
        Calculate Lip Vertex Error (LVE).
        
        This metric measures the maximum error among all lip vertices for each frame.
        
        Args:
            vertices_gt (np.ndarray): Ground truth vertices (T, V, 3).
            vertices_pred (np.ndarray): Predicted vertices (T, V, 3).
            mouth_map (list): Indices of vertices belonging to the mouth region.
            
        Returns:
            list: List of maximum lip errors for each frame.
        """
        lip_gt = vertices_gt[:, mouth_map, :]
        lip_pred = vertices_pred[:, mouth_map, :]
        lip_dist = np.linalg.norm(lip_gt - lip_pred, axis=2)
        frame_max_err = np.max(lip_dist, axis=1)  # Max error per frame
        return frame_max_err.tolist()

    def compute_mve(self, vertices_gt, vertices_pred):
        """
        Calculate Mean Vertex Error (MVE).
        
        This computes the average Euclidean distance over all vertices for each frame.
        
        Args:
            vertices_gt (np.ndarray): Ground truth vertices (T, V, 3).
            vertices_pred (np.ndarray): Predicted vertices (T, V, 3).
            
        Returns:
            list: List of mean vertex errors for each frame.
        """
        frame_mve = np.mean(np.linalg.norm(vertices_gt - vertices_pred, axis=2), axis=1)
        return frame_mve.tolist()