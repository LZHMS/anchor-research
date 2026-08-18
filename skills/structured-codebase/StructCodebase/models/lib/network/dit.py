"""Network layer implementations for multimodal transformer models."""

import math
from typing import Optional, Tuple

import torch
import torch.nn as nn
from ..head.pose_encoding import PositionEmbedding
from .attention import SelfAttention, attention
from .mlp import MLP
from .conv import ConvMLP, ChannelLastConv1d
from ..tail.residual import modulate


class CrossModalLayer(nn.Module):
    """Cross-modal layer for multimodal sequence processing.

    This layer implements cross-modal attention between two different modalities,
    inspired by the FACT model [Li 2021]. It processes concatenated sequences
    from two modalities through a transformer and produces output predictions.

    Args:
        config (dict): Configuration dictionary containing:
            - 'transformer': Transformer configuration with keys:
                - 'hidden_size': Hidden dimension size
                - 'num_hidden_layers': Number of transformer layers
                - 'num_attention_heads': Number of attention heads
                - 'intermediate_size': MLP intermediate size
            - 'output_layer': Output layer configuration with 'out_dim'
            - 'in_dim': Input dimension for normalization
            - 'sequence_length': Sequence length for position embedding
    """

    def __init__(self, config: dict):
        super().__init__()
        self.config = config
        model_config = self.config['transformer']

        # Transformer layer for cross-modal processing
        self.transformer_layer = Transformer(
            in_size=model_config['hidden_size'],
            hidden_size=model_config['hidden_size'],
            num_hidden_layers=model_config['num_hidden_layers'],
            num_attention_heads=model_config['num_attention_heads'],
            intermediate_size=model_config['intermediate_size'])

        # Output projection layers
        output_layer_config = self.config['output_layer']
        self.cross_norm_layer = nn.LayerNorm(self.config['in_dim'])
        self.cross_output_layer = nn.Linear(
            self.config['in_dim'],
            output_layer_config['out_dim'],
            bias=False)

        # Position embedding for sequence processing
        self.cross_pos_embedding = PositionEmbedding(
            self.config["sequence_length"], self.config['in_dim'])


    def forward(self, modal_a_sequences: torch.Tensor,
                modal_b_sequences: Optional[torch.Tensor],
                mask_info: dict) -> torch.Tensor:
        """Forward pass of the cross-modal layer.

        Args:
            modal_a_sequences: First modality sequences (e.g., listener motion embedding)
                Shape: (batch_size, seq_len_a, hidden_size)
            modal_b_sequences: Second modality sequences (e.g., speaker motion+audio embedding)
                Shape: (batch_size, seq_len_b, hidden_size). Can be None.
            mask_info: Dictionary containing masking information for transformer attention

        Returns:
            Logits tensor after cross-modal processing
                Shape: (batch_size, seq_len, out_dim)

        Raises:
            ValueError: If modal_a and modal_b have different hidden sizes
        """
        _, _, modal_a_width = get_shape_list(modal_a_sequences)
        merged_sequences = modal_a_sequences

        # Concatenate sequences from both modalities if modal_b is provided
        if modal_b_sequences is not None:
            _, _, modal_b_width = get_shape_list(modal_b_sequences)
            if modal_a_width != modal_b_width:
                raise ValueError(
                    "The modal_a hidden size (%d) should be the same with the modal_b "
                    "hidden size (%d)" % (modal_a_width, modal_b_width))
            merged_sequences = torch.cat([merged_sequences, modal_b_sequences], axis=1)

        # Apply position embedding and transformer processing
        merged_sequences = self.cross_pos_embedding(merged_sequences)
        merged_sequences = self.transformer_layer((merged_sequences, mask_info))
        merged_sequences = self.cross_norm_layer(merged_sequences)
        logits = self.cross_output_layer(merged_sequences)
        return logits


class DiTBlock(nn.Module):
    """
    带有自适应层归一化 (AdaLN) 的 Transformer Block。
    这是 Flow Matching 和 Diffusion Transformer 的标准模块。
    """
    def __init__(self, hidden_size, num_heads):
        super().__init__()
        self.norm1 = nn.LayerNorm(hidden_size, elementwise_affine=False, eps=1e-6)
        self.attn = nn.MultiheadAttention(hidden_size, num_heads=num_heads, batch_first=True)
        self.norm2 = nn.LayerNorm(hidden_size, elementwise_affine=False, eps=1e-6)
        self.mlp = nn.Sequential(
            nn.Linear(hidden_size, hidden_size * 4),
            nn.GELU(),
            nn.Linear(hidden_size * 4, hidden_size)
        )
        
        # AdaLN 调制层: 预测 shift (gamma) 和 scale (beta)
        # 输入是 time_embedding，输出是 6 个参数 (norm1_shift, norm1_scale, norm1_gate, norm2_shift, norm2_scale, norm2_gate)
        self.adaLN_modulation = nn.Sequential(
            nn.SiLU(),
            nn.Linear(hidden_size, 6 * hidden_size, bias=True)
        )

    def forward(self, x, c, key_padding_mask=None):
        """
        Args:
            x: (Batch, Seq_Len, Hidden_Size) - Input sequence
            c: (Batch, Hidden_Size) or (Batch, 1, Hidden_Size) - Conditioning signal for AdaLN
            key_padding_mask: (Batch, Seq_Len) - True 表示是 padding
        """
        # Handle conditioning signal: ensure it's (Batch, Hidden_Size)
        if c.ndim == 3:
            # If c is (Batch, Seq_Len, Hidden_Size), take mean or first token
            c = c.mean(dim=1)  # (Batch, Hidden_Size)
        
        # AdaLN modulation
        shift_msa, scale_msa, gate_msa, shift_mlp, scale_mlp, gate_mlp = self.adaLN_modulation(c).chunk(6, dim=1)

        def modulate(x, shift, scale):
            return x * (1 + scale.unsqueeze(1)) + shift.unsqueeze(1)

        # Attention with mask
        x_norm1 = modulate(self.norm1(x), shift_msa, scale_msa)
        
        attn_out, _ = self.attn(
            query=x_norm1, 
            key=x_norm1, 
            value=x_norm1, 
            key_padding_mask=key_padding_mask,
            need_weights=False
        )
        
        x = x + gate_msa.unsqueeze(1) * attn_out
        
        # MLP
        x_norm2 = modulate(self.norm2(x), shift_mlp, scale_mlp)
        mlp_out = self.mlp(x_norm2)
        x = x + gate_mlp.unsqueeze(1) * mlp_out
        
        return x

class MMDitSingleBlock(nn.Module):
    """Single block of MMDiT (Multimodal Diffusion Transformer).

    This class implements a single transformer block with adaptive layer normalization
    (AdaLN) modulation, supporting both convolutional and linear projections.
    Used in diffusion models for conditional generation.

    Args:
        dim: Model dimension
        nhead: Number of attention heads
        mlp_ratio: Ratio for MLP hidden dimension expansion. Default is 4.0.
        pre_only: If True, only perform pre-attention operations (for conditional generation).
            Default is False.
        kernel_size: Kernel size for convolutional layers. Default is 7.
        padding: Padding for convolutional layers. Default is 3.
    """

    def __init__(self,
                dim: int,
                nhead: int,
                mlp_ratio: float = 4.0,
                pre_only: bool = False,
                kernel_size: int = 7,
                padding: int = 3):
        super().__init__()
        self.norm1 = nn.LayerNorm(dim, elementwise_affine=False)
        self.attn = SelfAttention(dim, nhead)

        self.pre_only = pre_only

        # Adaptive Layer Normalization (AdaLN) modulation
        if pre_only:
            # For pre-only mode: modulate attention with shift and scale
            self.adaLN_modulation = nn.Sequential(nn.SiLU(), nn.Linear(dim, 2 * dim, bias=True))
        else:
            # For full mode: modulate both attention and MLP with shift, scale, and gate
            if kernel_size == 1:
                self.linear1 = nn.Linear(dim, dim)
            else:
                self.linear1 = ChannelLastConv1d(dim, dim, kernel_size=kernel_size, padding=padding)
            self.norm2 = nn.LayerNorm(dim, elementwise_affine=False)

            # Feed-forward network
            if kernel_size == 1:
                self.ffn = MLP(dim, int(dim * mlp_ratio), out_features=dim)
            else:
                self.ffn = ConvMLP(dim,
                                    int(dim * mlp_ratio),
                                    kernel_size=kernel_size,
                                    padding=padding)

            # Modulation for 6 parameters: shift_msa, scale_msa, gate_msa, shift_mlp, scale_mlp, gate_mlp
            self.adaLN_modulation = nn.Sequential(nn.SiLU(), nn.Linear(dim, 6 * dim, bias=True))

    def pre_attention(self, x: torch.Tensor, c: torch.Tensor, rot: Optional[torch.Tensor]) -> Tuple[Tuple[torch.Tensor, torch.Tensor, torch.Tensor], Tuple[Optional[torch.Tensor], ...]]:
        """Prepare attention inputs and modulation coefficients.

        Args:
            x: Input tensor of shape (batch_size, seq_len, dim)
            c: Conditioning tensor of shape (batch_size, dim)
            rot: Optional rotary position embedding tensor

        Returns:
            Tuple containing:
                - (q, k, v): Query, key, value tensors from attention preparation
                - Modulation coefficients: (gate_msa, shift_mlp, scale_mlp, gate_mlp)
                  Some may be None in pre_only mode
        """
        # Get modulation coefficients from conditioning
        modulation = self.adaLN_modulation(c)

        if self.pre_only:
            # Only modulate attention: shift and scale for MSA (Multi-Head Self Attention)
            (shift_msa, scale_msa) = modulation.chunk(2, dim=-1)
            gate_msa = shift_mlp = scale_mlp = gate_mlp = None
        else:
            # Modulate both attention and MLP: 6 parameters total
            (shift_msa, scale_msa, gate_msa, shift_mlp, scale_mlp,
             gate_mlp) = modulation.chunk(6, dim=-1)

        # Apply first AdaLN modulation to input
        x = modulate(self.norm1(x), shift_msa, scale_msa)
        # Get Q, K, V from attention layer
        q, k, v = self.attn.pre_attention(x, rot)
        return (q, k, v), (gate_msa, shift_mlp, scale_mlp, gate_mlp)

    def post_attention(self, x: torch.Tensor, attn_out: torch.Tensor, c: Tuple[Optional[torch.Tensor], ...]) -> torch.Tensor:
        """Apply post-attention processing with MLP and residual connections.

        Args:
            x: Original input tensor of shape (batch_size, seq_len, dim)
            attn_out: Attention output tensor of shape (batch_size, seq_len, dim)
            c: Modulation coefficients tuple (gate_msa, shift_mlp, scale_mlp, gate_mlp)

        Returns:
            Processed tensor after MLP and residual connections
        """
        if self.pre_only:
            return x

        (gate_msa, shift_mlp, scale_mlp, gate_mlp) = c

        # Ensure all modulation parameters have compatible shapes
        target_dim = x.shape[-1]
        batch_size = x.shape[0]

        # First residual connection with gating
        x = x + self.linear1(attn_out) * gate_msa.unsqueeze(1)

        # Second AdaLN modulation
        r = modulate(self.norm2(x), shift_mlp, scale_mlp)

        # Second residual connection with gating
        x = x + self.ffn(r) * gate_mlp.unsqueeze(1)

        return x

    def forward(self, x: torch.Tensor, cond: torch.Tensor,
                rot: Optional[torch.Tensor]) -> torch.Tensor:
        """Forward pass of the MMDiT single block.

        Args:
            x: Input tensor of shape (batch_size, seq_len, dim)
            cond: Conditioning tensor of shape (batch_size, dim)
            rot: Optional rotary position embedding tensor

        Returns:
            Output tensor of shape (batch_size, seq_len, dim)
        """
        # Prepare attention inputs and modulation coefficients
        x_qkv, x_conditions = self.pre_attention(x, cond, rot)

        # Apply attention mechanism
        attn_out = attention(*x_qkv)

        # Apply post-attention processing (MLP, residuals, gating)
        x = self.post_attention(x, attn_out, x_conditions)

        return x


class JointBlock(nn.Module):
    """Joint attention block that processes latent and text features together.

    This block implements joint attention between latent features (e.g., audio/motion)
    and text features, allowing cross-modal information flow. It uses separate
    MMDiT blocks for each modality but combines their attention computations.

    Args:
        dim: Model dimension for both latent and text features
        nhead: Number of attention heads
        mlp_ratio: Ratio for MLP hidden dimension expansion. Default is 4.0.
        pre_only: If True, only perform pre-attention operations for text features.
            Default is False.
    """

    def __init__(self, dim: int, nhead: int, mlp_ratio: float = 4.0, pre_only: bool = False):
        super().__init__()
        self.pre_only = pre_only

        # Block for latent features (e.g., audio/motion) - always full processing
        self.latent_block = MMDitSingleBlock(dim,
                                             nhead,
                                             mlp_ratio,
                                             pre_only=False,
                                             kernel_size=3,
                                             padding=1)

        # Block for audio features - may be pre_only depending on configuration
        self.audio_block = MMDitSingleBlock(dim, nhead, mlp_ratio, pre_only=pre_only, kernel_size=1)

    def forward(self, latent: torch.Tensor, audio_f: torch.Tensor,
                global_c: torch.Tensor, extended_c: torch.Tensor,
                latent_rot: torch.Tensor, audio_rot: torch.Tensor,
                ) -> Tuple[torch.Tensor, torch.Tensor]:
        """Forward pass with joint attention between latent and text features.

        Args:
            latent: Latent features (e.g., motion) of shape (batch_size, latent_len, dim)
            audio_f: Audio features of shape (batch_size, audio_len, dim)
            global_c: Global conditioning tensor of shape (batch_size, dim)
            extended_c: Extended conditioning tensor of shape (batch_size, dim)
            latent_rot: Rotary position embedding for latent features
            audio_rot: Rotary position embedding for audio features

        Returns:
            Tuple of (processed_latent, processed_audio_f) with same shapes as inputs
        """
        # Prepare attention inputs for both modalities
        x_qkv, x_mod = self.latent_block.pre_attention(latent, extended_c, rot=latent_rot)
        t_qkv, t_mod = self.audio_block.pre_attention(audio_f, global_c, rot=audio_rot)

        latent_len = latent.shape[1]

        # Concatenate Q, K, V across sequence dimension for joint attention
        joint_qkv = [torch.cat([x_qkv[i], t_qkv[i]], dim=2) for i in range(3)]

        # Perform joint attention across both modalities
        attn_out = attention(*joint_qkv)

        # Split attention output back to respective modalities
        x_attn_out = attn_out[:, :latent_len]
        t_attn_out = attn_out[:, latent_len:]

        # Apply post-attention processing for latent features (always full processing)
        latent = self.latent_block.post_attention(latent, x_attn_out, x_mod)

        # Apply post-attention processing for text features (skip if pre_only)
        if not self.pre_only:
            audio_f = self.audio_block.post_attention(audio_f, t_attn_out, t_mod)

        return latent, audio_f