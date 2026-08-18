"""Flow Matching Transformer (FMT) Module
"""
import torch
import torch.nn as nn
from models.lib.common import enc_dec_mask, get_sinusoid_encoding_table
from models.lib.network.mlp import MLP
from models.lib.network.dit import DiTBlock
from models.lib.network.attention import Attention
from models.lib.head.embeddings import TimestepEmbedder, LinearEmbedding
from models.lib.head.pose_encoding import PositionalEncoding, PositionEmbedding


class FlowVelocityPredictor(nn.Module):
    """
    Transformer network to predict velocity fields for flow matching at timestep t.
    """
    
    def __init__(self, in_dim, out_dim, hidden_dim, seq_len, n_layers=4, n_heads=4, mlp_ratio=4.0, align_mask_width=0, use_learnable_pe=True):
        """
        Args:
            in_dim (int): Input feature dimension.
            out_dim (int): Output velocity dimension.
            hidden_dim (int): Hidden dimension for transformer blocks.
            seq_len (int): Maximum sequence length.
            n_layers (int): Number of transformer layers. Defaults to 4.
            n_heads (int): Number of attention heads. Defaults to 4.
            neg_slope (float): Negative slope for LeakyReLU. Defaults to 0.2.
            use_learnable_pe (bool): Use learnable positional encoding. Defaults to False.
        """
        super().__init__()

        self.use_learnable_pe, self.seq_len, self.hidden_dim = use_learnable_pe, seq_len, hidden_dim
        # Project input features to hidden dimension
        self.feat_proj = LinearEmbedding(in_dim, hidden_dim)
        
        if use_learnable_pe:
            # Learnable positional encoding
            self.PE = PositionEmbedding(seq_len, hidden_dim)
        else:
            self.PE = PositionalEncoding(hidden_dim)
        
        # FMT Blocks
        self.fmt_blocks = nn.ModuleList([FMTBlock(hidden_dim, n_heads, mlp_ratio=mlp_ratio) for _ in range(n_layers)])

        # Flow/velocity decoder
        self.fmt_decoder = FMTDecoder(hidden_dim, out_dim)

        # define alignment mask
        if align_mask_width > 0:
            alignment_mask = enc_dec_mask(seq_len, seq_len, 1, align_mask_width)
            # alignment_mask = F.pad(alignment_mask, (0, 0, 1, 0), value=False)
            self.register_buffer('alignment_mask', alignment_mask)
        else:
            self.alignment_mask = None

        self.initialize_weights()

    def initialize_weights(self) -> None:
        """Initialize decoder weights to zero for stable training start."""
        if self.use_learnable_pe:
            pos_embed = get_sinusoid_encoding_table(self.seq_len, self.hidden_dim)
            self.PE.pos_embedding.data.copy_(pos_embed.unsqueeze(0))
        
        w = self.feat_proj.proj.weight.data
        nn.init.xavier_uniform_(w.view([w.shape[0], -1]))
        nn.init.constant_(self.feat_proj.proj.bias, 0)
        
        # Zero-out adaLN modulation layers in FMT blocks:
        for block in self.fmt_blocks:
            nn.init.constant_(block.adaLN_modulation[-1].weight, 0)
            nn.init.constant_(block.adaLN_modulation[-1].bias, 0)

        # Zero-out output layers:
        nn.init.constant_(self.fmt_decoder.adaLN_modulation[-1].weight, 0)
        nn.init.constant_(self.fmt_decoder.adaLN_modulation[-1].bias, 0)
        nn.init.constant_(self.fmt_decoder.linear.weight, 0)
        nn.init.constant_(self.fmt_decoder.linear.bias, 0)

    def forward(self, x_in, conditions):
        """
        Predict velocity field at timestep t.
        
        Args:
            x_in (torch.Tensor): Input features (N, L, in_dim).
            conditions (torch.Tensor): Conditioning features (N, L, hidden_dim).
            
        Returns:
            torch.Tensor: Predicted velocity (N, L, out_dim).
        """
        # Project input features
        x_in = self.feat_proj(x_in)  # (N, L, hidden_dim)

        # Add positional encoding
        x_in = self.PE(x_in)
        for block in self.fmt_blocks:
            x_in = block(x_in, conditions, self.alignment_mask)

        # Decode flow/velocity
        flow = self.fmt_decoder(x_in, conditions)  # (N, L_p + L, d_motion)  
        return flow
    

class FMTBlock(nn.Module):
    """
    Flow Matching Transformer block with adaptive layer normalization (adaLN-Zero).
    Injects conditioning via learned scale, shift, and gate parameters.
    Modified from https://github.com/deepbrainai-research/float/blob/main/models/float/FMT.py
    """
    def __init__(self, hidden_size, num_heads, mlp_ratio=4.0, **block_kwargs) -> None:
        """
        Args:
            hidden_size (int): Hidden dimension of the transformer.
            num_heads (int): Number of attention heads.
            mlp_ratio (float): Ratio of MLP hidden dimension to input dimension. Defaults to 4.0.
            **block_kwargs: Additional arguments passed to the Attention layer.
        """
        super().__init__()
        self.norm1 = nn.LayerNorm(hidden_size, elementwise_affine=False, eps=1e-6)
        self.attn = Attention(hidden_size, num_heads=num_heads, qkv_bias=True, **block_kwargs)
        self.norm2 = nn.LayerNorm(hidden_size, elementwise_affine=False, eps=1e-6)
        self.mlp = MLP(in_features=hidden_size, hidden_features=int(hidden_size * mlp_ratio),
                    act_layer=lambda: nn.GELU(approximate="tanh"), drop=0)
        self.adaLN_modulation = nn.Sequential(
            nn.SiLU(),
            nn.Linear(hidden_size, 6 * hidden_size, bias=True)
        )

    def framewise_modulate(self, x, shift, scale) -> torch.Tensor:
        """Apply affine transformation: x * (1 + scale) + shift."""
        return x * (1 + scale) + shift

    def forward(self, x, c, mask=None) -> torch.Tensor:
        """
        Args:
            x (torch.Tensor): Input features (N, L, hidden_size).
            c (torch.Tensor): Conditioning vector (N, L, hidden_size).
            mask (torch.Tensor): Attention mask (required).
            
        Returns:
            torch.Tensor: Output features (N, L, hidden_size).
        """
        assert mask is not None
        shift_msa, scale_msa, gate_msa, shift_mlp, scale_mlp, gate_mlp = self.adaLN_modulation(c).chunk(6, dim=-1)        
        x = x + gate_msa * self.attn(self.framewise_modulate(self.norm1(x), shift_msa, scale_msa), mask = mask)
        x = x + gate_mlp * self.mlp(self.framewise_modulate(self.norm2(x), shift_mlp, scale_mlp))
        return x


class FMTDecoder(nn.Module):
    """
    Final decoder layer for Flow Matching Transformer with adaptive normalization.
    """
    def __init__(self, hidden_size, out_dim):
        """
        Args:
            hidden_size (int): Hidden dimension.
            out_dim (int): Output dimension.
        """
        super().__init__()
        self.norm_final = nn.LayerNorm(hidden_size, elementwise_affine=False, eps=1e-6)
        self.adaLN_modulation = nn.Sequential(
            nn.SiLU(),
            nn.Linear(hidden_size, 2 * hidden_size, bias=True)
        )
        self.linear = nn.Linear(hidden_size, out_dim, bias=True)

    def framewise_modulate(self, x, shift, scale) -> torch.Tensor:
        """Apply affine transformation: x * (1 + scale) + shift."""
        return x * (1 + scale) + shift

    def forward(self, x: torch.Tensor, c: torch.Tensor) -> torch.Tensor:
        """
        Decode features to output with adaptive normalization.
        
        Args:
            x (torch.Tensor): Input features (N, L, hidden_size).
            c (torch.Tensor): Conditioning vector (N, L, hidden_size).
            
        Returns:
            torch.Tensor: Decoded output (N, L, out_dim).
        """
        shift, scale = self.adaLN_modulation(c).chunk(2, dim=-1)
        x = self.framewise_modulate(self.norm_final(x), shift, scale)
        return self.linear(x)