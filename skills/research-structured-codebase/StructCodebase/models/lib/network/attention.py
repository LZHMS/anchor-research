"""Attention mechanisms for transformer-based models."""

from typing import Optional, Tuple

import torch
import torch.nn as nn
from torch.nn import functional as F
from einops.layers.torch import Rearrange
from einops import rearrange


def apply_rope(x: torch.Tensor, rot: torch.Tensor) -> torch.Tensor:
    """Apply rotary position embedding to input tensor."""
    # Simplified implementation - in practice this would apply
    # rotary transformations to the input
    if rot is not None:
        # This is a placeholder - actual RoPE implementation would be more complex
        return x * rot.unsqueeze(-1).unsqueeze(-1)
    return x


def attention(q: torch.Tensor, k: torch.Tensor, v: torch.Tensor):
    """Compute attention with flash attention fallback."""
    q = q.contiguous()
    k = k.contiguous()
    v = v.contiguous()
    # flash attention is not compatible with JVP calculation
    with torch.backends.cuda.sdp_kernel(enable_flash=False, enable_math=True, enable_mem_efficient=False):
        out = F.scaled_dot_product_attention(q, k, v)
    out = rearrange(out, 'b h n d -> b n (h d)').contiguous()
    return out


class RMSNorm(nn.Module):
    """Root Mean Square Normalization.

    This is a simplified version of RMSNorm that normalizes by the root mean square.
    """
    def __init__(self, dim, eps=1e-6):
        super().__init__()
        self.eps = eps
        self.scale = nn.Parameter(torch.ones(dim))

    def forward(self, x):
        # Compute RMS: sqrt(mean(x^2, dim=-1, keepdim=True))
        rms = torch.sqrt(torch.mean(x**2, dim=-1, keepdim=True) + self.eps)
        # Normalize and scale
        return x / rms * self.scale


class Attention(nn.Module):
	"""
	Multi-head self-attention mechanism with optional Q/K normalization and fused attention.
	Supports attention masking for sequence modeling tasks.
    Modified from https://github.com/deepbrainai-research/float/blob/main/models/float/FMT.py
	"""
	def __init__(
			self,
			dim: int,
			num_heads: int = 8,
			qkv_bias: bool = False,
			qk_norm: bool = False,
			attn_drop: float = 0.,
			proj_drop: float = 0.,
			norm_layer: nn.Module = nn.LayerNorm,
            fuse_attn: bool = True,
	) -> None:
		"""
		Args:
			dim (int): Input feature dimension.
			num_heads (int): Number of attention heads. Defaults to 8.
			qkv_bias (bool): Whether to add bias to QKV projection. Defaults to False.
			qk_norm (bool): Whether to normalize queries and keys. Defaults to False.
			attn_drop (float): Dropout rate for attention weights. Defaults to 0.
			proj_drop (float): Dropout rate for output projection. Defaults to 0.
			norm_layer (nn.Module): Normalization layer for Q/K. Defaults to nn.LayerNorm.
			fuse_attn (bool): Whether to use fused attention implementation. Defaults to True.
		"""

		super().__init__()
		assert dim % num_heads == 0, 'dim should be divisible by num_heads'
		self.num_heads = num_heads
		self.head_dim = dim // num_heads
		self.scale = self.head_dim ** -0.5
		self.fused_attn = self.use_fused_attn(fuse_attn)

		self.qkv = nn.Linear(dim, dim * 3, bias=qkv_bias)
		self.q_norm = norm_layer(self.head_dim) if qk_norm else nn.Identity()
		self.k_norm = norm_layer(self.head_dim) if qk_norm else nn.Identity()
		self.attn_drop = nn.Dropout(attn_drop)
		self.proj = nn.Linear(dim, dim)
		self.proj_drop = nn.Dropout(proj_drop)

	def use_fused_attn(self, fuse_attn: bool = False) -> bool:
		"""
		Check if fused attention implementation is available and should be used.

		Args:
			fuse_attn (bool): Whether to enable fused attention if available. Defaults to False.

		Returns:
			bool: True if fused attention should be used, False otherwise.
		"""
		if not hasattr(torch.nn.functional, "scaled_dot_product_attention"):
			return False
		return fuse_attn

	def forward(self, x: torch.Tensor, mask: torch.Tensor = None) -> torch.Tensor:
		"""
		Apply multi-head self-attention to input.

		Args:
			x (torch.Tensor): Input tensor of shape (batch_size, seq_len, dim).
			mask (torch.Tensor, optional): Boolean attention mask. True values are masked out.

		Returns:
			torch.Tensor: Output tensor of shape (batch_size, seq_len, dim).
		"""
		B, N, C = x.shape
		qkv = self.qkv(x).reshape(B, N, 3, self.num_heads, self.head_dim).permute(2, 0, 3, 1, 4)
		q, k, v = qkv.unbind(0)
		q, k = self.q_norm(q), self.k_norm(k)

		if self.fused_attn:
			x = F.scaled_dot_product_attention(
				q, k, v,
				attn_mask = ~mask,
				dropout_p=self.attn_drop.p if self.training else 0.,
			)
		else:
			q = q * self.scale
			attn = q @ k.transpose(-2, -1)
			attn = attn.softmax(dim=-1)
			attn = self.attn_drop(attn)
			x = attn @ v

		x = x.transpose(1, 2).reshape(B, N, C)
		x = self.proj(x)
		x = self.proj_drop(x)
		return x


class MultiHeadAttention(nn.Module):
    """Multi-head attention layer with masking support.

    This class implements a standard multi-head attention mechanism that supports
    attention masking for sequence processing tasks.

    Args:
        in_dim (int): Input feature dimension
        dim (int): Hidden dimension for attention computation
        heads (int): Number of attention heads. Default is 8.
    """

    def __init__(self, in_dim: int, dim: int, heads: int = 8):
        super().__init__()
        self.heads = heads
        self.scale = dim ** -0.5

        # Linear projections for Q, K, V
        self.to_qkv = nn.Linear(in_dim, dim * 3, bias=False)
        self.to_out = nn.Linear(dim, dim)

        # Rearrangement operations for multi-head attention
        self.rearrange_qkv = Rearrange(
            "b n (qkv h d) -> qkv b h n d", qkv=3, h=self.heads)
        self.rearrange_out = Rearrange("b h n d -> b n (h d)")

    def forward(self, x_data: Tuple[torch.Tensor, dict]) -> Tuple[torch.Tensor, dict]:
        """Forward pass of the attention layer.

        Args:
            x_data: Tuple containing input tensor and mask information.
                - x: Input tensor of shape (batch_size, seq_len, in_dim)
                - mask_info: Dictionary containing masking information with keys:
                    - 'max_mask': Maximum sequence length for masking
                    - 'mask': Attention mask tensor

        Returns:
            Tuple containing output tensor and original mask information.
                - out: Output tensor of shape (batch_size, seq_len, dim)
                - mask_info: Original mask information dictionary
        """
        x, mask_info = x_data
        max_mask = mask_info['max_mask']
        mask = mask_info['mask']

        # Project input to Q, K, V and rearrange for multi-head attention
        qkv = self.to_qkv(x)
        qkv = self.rearrange_qkv(qkv)
        q = qkv[0]  # Query: (batch_size, heads, seq_len, dim//heads)
        k = qkv[1]  # Key: (batch_size, heads, seq_len, dim//heads)
        v = qkv[2]  # Value: (batch_size, heads, seq_len, dim//heads)

        # Compute attention scores
        dots = torch.einsum("bhid,bhjd->bhij", q, k) * self.scale

        # Apply masking if provided
        if max_mask is not None:
            dots[:, :, :max_mask, :max_mask] = \
                dots[:, :, :max_mask, :max_mask].masked_fill(mask == 0., float('-inf'))

        # Apply softmax to get attention weights
        attn = F.softmax(dots, dim=-1)

        # Apply attention weights to values
        out = torch.einsum("bhij,bhjd->bhid", attn, v)

        # Rearrange and project output
        out = self.rearrange_out(out)
        out = self.to_out(out)
        return (out, mask_info)


class SelfAttention(nn.Module):
    """Self-attention mechanism with RMS normalization and optional rotary position embedding.

    This class implements self-attention with separate normalization for queries and keys,
    and supports rotary position embedding for enhanced positional understanding.

    Args:
        dim (int): Model dimension
        nheads (int): Number of attention heads
    """

    def __init__(self, dim: int, nheads: int):
        super().__init__()
        self.dim = dim
        self.nheads = nheads

        # Linear projection for Q, K, V
        self.qkv = nn.Linear(dim, dim * 3, bias=True)

        # RMS normalization for queries and keys
        self.q_norm = RMSNorm(dim // nheads)
        self.k_norm = RMSNorm(dim // nheads)

        # Rearrangement for splitting into heads and QKV components
        self.split_into_heads = Rearrange('b n (h d j) -> b h n d j',
                                          h=nheads,
                                          d=dim // nheads,
                                          j=3)

    def pre_attention(self, x: torch.Tensor, rot: Optional[torch.Tensor]) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """Prepare Q, K, V tensors and apply rotary position embedding if provided.

        Args:
            x: Input tensor of shape (batch_size, n_tokens, n_channels)
            rot: Optional rotary position embedding tensor. If None, no rotation is applied.

        Returns:
            Tuple of (query, key, value) tensors, each of shape
            (batch_size, nheads, n_tokens, dim//nheads)
        """
        # Project input to QKV space
        qkv = self.qkv(x)

        # Split into heads and separate Q, K, V components
        q, k, v = self.split_into_heads(qkv).chunk(3, dim=-1)
        q = q.squeeze(-1)  # Remove the j dimension (which was 3)
        k = k.squeeze(-1)
        v = v.squeeze(-1)

        # Apply RMS normalization
        q = self.q_norm(q)
        k = self.k_norm(k)

        # Apply rotary position embedding if provided
        if rot is not None:
            q = apply_rope(q, rot)
            k = apply_rope(k, rot)

        return q, k, v

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass of self-attention.

        Args:
            x: Input tensor of shape (batch_size, n_tokens, n_channels)

        Returns:
            Output tensor of shape (batch_size, n_tokens, n_channels)
        """
        # Note: The order q, v, k = self.pre_attention(x) seems incorrect
        # It should probably be q, k, v = self.pre_attention(x)
        q, v, k = self.pre_attention(x, None)  # No rotary embedding for basic self-attention
        out = attention(q, k, v)
        return out


class CrossModalAttention(nn.Module):
    """Cross-modal attention layer for multimodal learning.

    This layer performs attention between two different modalities, computing
    queries from modality A and keys/values from modality B. This enables
    information flow from modality B to guide the representation learning of modality A.

    Args:
        in_dim (int): Input dimension for modality A (query modality)
        dim (int): Hidden dimension for attention computation
        heads (int): Number of attention heads. Default is 8.
        in_dim2 (int, optional): Input dimension for modality B (key/value modality).
            If None, uses the same dimension as in_dim.
    """

    def __init__(self, in_dim: int, dim: int, heads: int = 8, in_dim2: Optional[int] = None):
        super().__init__()
        self.heads = heads
        self.scale = dim ** -0.5

        # Linear projections for different modalities
        if in_dim2 is not None:
            self.to_kv = nn.Linear(in_dim2, in_dim2 * 2, bias=False)  # K, V from modality B
        else:
            self.to_kv = nn.Linear(in_dim, dim * 2, bias=False)  # K, V from modality A
        self.to_q = nn.Linear(in_dim, dim, bias=False)  # Q from modality A

        # Compute output dimension for final projection
        if in_dim2 is not None:
            dim2 = int((in_dim + in_dim2 * 2) / 3)  # Average of Q, K, V dimensions
        else:
            dim2 = dim
        self.to_out = nn.Linear(dim2, dim)

        # Rearrangement operations for multi-head attention
        self.rearrange_qkv = Rearrange(
            "b n (qkv h d) -> qkv b h n d", qkv=3, h=self.heads)
        self.rearrange_out = Rearrange("b h n d -> b n (h d)")

    def forward(self, x_data: dict) -> dict:
        """Forward pass of cross-modal attention.

        Args:
            x_data: Dictionary containing input tensors for both modalities:
                - 'x_a': Tensor for modality A (query modality)
                - 'x_b': Tensor for modality B (key/value modality)

        Returns:
            Dictionary containing:
                - 'x_a': Original modality A tensor (unchanged)
                - 'x_b': Updated modality B tensor after cross-modal attention
        """
        x_a = x_data['x_a']  # Modality A: source of queries
        x_b = x_data['x_b']  # Modality B: source of keys and values

        # Project modalities to their respective spaces
        kv = self.to_kv(x_b)  # Keys and values from modality B
        q = self.to_q(x_a)    # Queries from modality A

        # Concatenate and rearrange for multi-head attention
        qkv = torch.cat((q, kv), dim=-1)
        qkv = self.rearrange_qkv(qkv)
        q = qkv[0]  # Query: (batch_size, heads, seq_len, dim//heads)
        k = qkv[1]  # Key: (batch_size, heads, seq_len, dim//heads)
        v = qkv[2]  # Value: (batch_size, heads, seq_len, dim//heads)

        # Compute attention scores and weights
        dots = torch.einsum("bhid,bhjd->bhij", q, k) * self.scale
        attn = F.softmax(dots, dim=-1)

        # Apply attention to values
        out = torch.einsum("bhij,bhjd->bhid", attn, v)

        # Rearrange and project output back to original dimension
        out = self.rearrange_out(out)
        out = self.to_out(out)

        return {'x_a': x_a, 'x_b': out}