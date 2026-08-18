import math
import torch
import torch.nn as nn


class TimestepEmbedder(nn.Module):
    """
    Embeds scalar timesteps into vector representations using sinusoidal encoding and MLP.
    Commonly used in diffusion models and flow matching transformers.
    """

    def __init__(self, hidden_size, frequency_embedding_size=256):
        """
        Args:
            hidden_size (int): Output embedding dimension.
            frequency_embedding_size (int): Sinusoidal encoding dimension. Defaults to 256.
        """
        super().__init__()
        self.mlp = nn.Sequential(
            nn.Linear(frequency_embedding_size, hidden_size, bias=True),
            nn.SiLU(),
            nn.Linear(hidden_size, hidden_size, bias=True),
        )
        self.frequency_embedding_size = frequency_embedding_size

    @staticmethod
    def timestep_embedding(t: torch.Tensor, dim: int, max_period: int = 10000) -> torch.Tensor:
        """
        Create sinusoidal timestep embeddings with exponentially spaced frequencies.
        Borrowed from https://github.com/deepbrainai-research/float/blob/main/models/float/FMT.py

        Args:
            t (torch.Tensor): 1-D tensor of shape (N,) with timestep values, typically in [0, 1].
            dim (int): Output embedding dimension. Padded with zeros if odd.
            max_period (int): Controls minimum frequency. Defaults to 10000.

        Returns:
            torch.Tensor: Shape (N, dim) positional embeddings.
        """
        half = dim // 2
        freqs = torch.exp(
			-math.log(max_period) * torch.arange(start=0, end=half, dtype=torch.float32) / half
		).to(device=t.device)
        args = t[:, None].float() * freqs[None]
        embedding = torch.cat([torch.cos(args), torch.sin(args)], dim=-1)
        if dim % 2:
            embedding = torch.cat([embedding, torch.zeros_like(embedding[:, :1])], dim=-1)
        return embedding
    
    def forward(self, t: torch.Tensor) -> torch.Tensor:
        """
        Convert timesteps to embeddings via sinusoidal encoding and MLP projection.

        Args:
            t (torch.Tensor): Timestep tensor of shape (N,), typically normalized to [0, 1].

        Returns:
            torch.Tensor: Embedded timestep tensor of shape (N, hidden_size).
        """
        t_freq = self.timestep_embedding(t, self.frequency_embedding_size)
        t_emb = self.mlp(t_freq)
        return t_emb


class LinearEmbedding(nn.Module):
    """
    Linear projection layer with optional normalization for embedding transformations.
    """

    def __init__(self, in_dim, out_dim, norm_layer=None, bias=True):
        """
        Args:
            in_dim (int): Input feature dimension.
            out_dim (int): Output feature dimension.
            norm_layer (nn.Module, optional): Normalization layer. Defaults to None.
            bias (bool): Whether to include bias in linear projection. Defaults to True.
        """
        super().__init__()
        self.proj = nn.Linear(in_dim, out_dim, bias=bias)
        self.norm = norm_layer(out_dim) if norm_layer else nn.Identity()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Apply linear projection and optional normalization.

        Args:
            x (torch.Tensor): Input tensor.

        Returns:
            torch.Tensor: Projected and normalized tensor.
        """
        return self.norm(self.proj(x))

class LinearEmbeddingSE(nn.Module):
    """ Linear Layer """

    def __init__(self, size, dim):
        super().__init__()
        self.net = nn.Linear(size, dim)

    def forward(self, x):
        return self.net(x)