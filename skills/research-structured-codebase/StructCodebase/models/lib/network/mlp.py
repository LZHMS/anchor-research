""" MLP module w/ dropout and configurable activation layer
    Modified from https://github.com/huggingface/pytorch-image-models/blob/main/timm/layers/mlp.py
"""
import torch.nn as nn
from functools import partial
from typing import Optional, Type, Union, Tuple
from models.lib.helpers import to_2tuple

class MLP(nn.Module):
    """
    Multi-Layer Perceptron with configurable activation, normalization, and dropout.

    Supports three modes:
        - Standard: Linear layers for N*C tensors (use_conv2d=False, use_conv1d=False)
        - Image Conv: 1x1 Conv2d for NCHW image tensors (use_conv2d=True)
        - Sequence Conv: 1x1 Conv1d for NCL sequence tensors (use_conv1d=True)
    """
    def __init__(
            self,
            in_features: int,
            hidden_features: Optional[int] = None,
            out_features: Optional[int] = None,
            act_layer: Type[nn.Module] = nn.GELU,
            norm_layer: Optional[Type[nn.Module]] = None,
            bias: Union[bool, Tuple[bool, bool]] = True,
            drop: Union[float, Tuple[float, float]] = 0.,
            use_conv1d: bool = False,
            use_conv2d: bool = False,
            device=None,
            dtype=None,
    ):
        """
        Args:
            in_features (int): Input feature dimension.
            hidden_features (int, optional): Hidden layer dimension. Defaults to in_features.
            out_features (int, optional): Output feature dimension. Defaults to in_features.
            act_layer (Type[nn.Module]): Activation layer. Defaults to nn.GELU.
            norm_layer (Type[nn.Module], optional): Normalization layer. Defaults to None.
            bias (bool or Tuple[bool, bool]): Bias for fc1 and fc2 layers. Defaults to True.
            drop (float or Tuple[float, float]): Dropout probability for two dropout layers. Defaults to 0.
            use_conv1d (bool): Use Conv1d (1x1) for sequence data (NCL). Defaults to False.
            use_conv2d (bool): Use Conv2d (1x1) for image data (NCHW). Defaults to False.
            device: Device for parameters.
            dtype: Data type for parameters.
        """
        dd = {'device': device, 'dtype': dtype}
        super().__init__()
        out_features = out_features or in_features
        hidden_features = hidden_features or in_features
        bias = to_2tuple(bias)
        drop_probs = to_2tuple(drop)
        
        # Choose layer type based on input format
        if use_conv1d:
            linear_layer = partial(nn.Conv1d, kernel_size=1)
        elif use_conv2d:
            linear_layer = partial(nn.Conv2d, kernel_size=1)
        else:
            linear_layer = nn.Linear
        
        self.use_conv1d = use_conv1d
        self.fc1 = linear_layer(in_features, hidden_features, bias=bias[0], **dd)
        self.act = act_layer()
        self.drop1 = nn.Dropout(drop_probs[0])
        self.norm = norm_layer(hidden_features, **dd) if norm_layer is not None else nn.Identity()
        self.fc2 = linear_layer(hidden_features, out_features, bias=bias[1], **dd)
        self.drop2 = nn.Dropout(drop_probs[1])

    def forward(self, x):
        """
        Forward pass through the MLP.

        Args:
            x (torch.Tensor): Input tensor.
                - If use_conv2d=False and use_conv1d=False: shape (N, *, C)
                - If use_conv2d=True: shape (N, C, H, W)
                - If use_conv1d=True: shape (N, L, C) will be transposed to (N, C, L)

        Returns:
            torch.Tensor: Output tensor with same format as input.
        """
        # For sequence data (NLC), transpose to NCL for Conv1d
        if self.use_conv1d and x.dim() == 3:
            x = x.transpose(1, 2)  # NLC -> NCL
        
        x = self.fc1(x)
        x = self.act(x)
        x = self.drop1(x)
        x = self.norm(x)
        x = self.fc2(x)
        x = self.drop2(x)
        
        # Transpose back to NLC for sequence data
        if self.use_conv1d and x.dim() == 3:
            x = x.transpose(1, 2)  # NCL -> NLC
        
        return x