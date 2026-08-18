import torch.nn as nn

from models.lib.head.embeddings import LinearEmbedding
from models.lib.head.pose_encoding import PositionalEncoding


class ConvTransformerEncoder(nn.Module):
    """ 
    Convolutional Transformer Encoder for sequence encoding.

    Combines CNN layers for temporal downsampling with Transformer layers for 
    sequence modeling. Commonly used in VQ-VAE architectures for motion/speech processing.

    Args:
        in_dim (int): Input feature dimension
        hidden_dim (int): Hidden dimension for Transformer and convolutions
        n_layers (int, optional): Number of Transformer encoder layers (default: 4)
        n_heads (int, optional): Number of attention heads in Transformer (default: 4)
        mlp_ratio (int, optional): Ratio for feedforward dimension in Transformer (default: 4)
        downsample_factor (int, optional): Number of temporal downsampling stages. If 0, no downsampling
            is applied. If > 0, reduces sequence length by 2^downsample_factor (default: 0)
        neg_slope (float, optional): Negative slope for LeakyReLU activation (default: 0.2)
        affine (bool, optional): Whether to use learnable affine parameters in normalization layers
            (default: True)
    """

    def __init__(self, in_dim, hidden_dim, n_layers=4, n_heads=4, mlp_ratio=4,
                downsample_factor=0, neg_slope=0.2, affine=True):
        super().__init__()
        
        # Project input features to hidden dimension
        self.feat_proj = nn.Sequential(nn.Linear(in_dim, hidden_dim), nn.LeakyReLU(neg_slope, True))
        
        # Build convolutional downsampling layers
        if downsample_factor == 0:
            # No downsampling: use single conv layer with stride 1
            layers = [nn.Sequential(
                        nn.Conv1d(hidden_dim, hidden_dim, kernel_size=5, stride=1, padding=2, padding_mode='replicate'),
                        nn.LeakyReLU(neg_slope, True),
                        nn.InstanceNorm1d(hidden_dim, affine=affine))]
        else:
            # First layer: conv with stride 2 for initial downsampling
            layers = [nn.Sequential(
                        nn.Conv1d(hidden_dim, hidden_dim, kernel_size=5, stride=2, padding=2, padding_mode='replicate'),
                        nn.LeakyReLU(neg_slope, True),
                        nn.InstanceNorm1d(hidden_dim, affine=affine))]
            # Additional layers: conv + MaxPool for further downsampling
            for _ in range(1, downsample_factor):
                layers += [nn.Sequential(
                            nn.Conv1d(hidden_dim, hidden_dim, kernel_size=5, stride=1, padding=2, padding_mode='replicate'),
                            nn.LeakyReLU(neg_slope, True),
                            nn.InstanceNorm1d(hidden_dim, affine=affine),
                            nn.MaxPool1d(2))]  # Halves the sequence length
        self.squasher = nn.Sequential(*layers)
        
        # Build Transformer encoder
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=hidden_dim,           # Model dimension
            nhead=n_heads,                # Number of attention heads
            dim_feedforward=hidden_dim * mlp_ratio,  # FFN hidden dimension
            activation='gelu',            # Activation function
            batch_first=True,             # Input shape: (batch, seq, feature)
            norm_first=True               # Pre-LN (layer norm before attention)
        )
        self.encoder_transformer = nn.TransformerEncoder(encoder_layer, num_layers=n_layers)

        # Positional and linear embeddings for Transformer input
        self.encoder_pos_embedding = PositionalEncoding(hidden_dim)
        self.encoder_linear_embedding = LinearEmbedding(hidden_dim, hidden_dim)

    def forward(self, inputs):
        """
        Forward pass of the encoder.
        
        Args:
            inputs (torch.Tensor): Input tensor of shape (batch_size, seq_len, in_dim)
        
        Returns:
            encoder_features (torch.Tensor): Encoded features of shape
                (batch_size, seq_len // 2^downsample_factor, hidden_dim)
        """
        # Project input to hidden dimension: (N, L, in_dim) -> (N, L, hidden_dim)
        inputs = self.feat_proj(inputs)
        
        # Apply convolutional downsampling: (N, L, C) -> (N, C, L) -> conv -> (N, C, L') -> (N, L', C)
        inputs = self.squasher(inputs.permute(0, 2, 1)).permute(0, 2, 1)

        # Apply embeddings for Transformer
        encoder_features = self.encoder_linear_embedding(inputs)
        encoder_features = self.encoder_pos_embedding(encoder_features)
        
        # Pass through Transformer encoder layers
        encoder_features = self.encoder_transformer(encoder_features)

        return encoder_features


class ConvTransformerDecoder(nn.Module):
    """ 
    Convolutional Transformer Decoder for sequence reconstruction.

    Combines Transformer layers for sequence modeling with upsampling layers to 
    restore the original sequence length. Typically paired with ConvTransformerEncoder
    in VQ-VAE architectures.

    Args:
        out_dim (int): Output feature dimension
        hidden_dim (int): Hidden dimension for Transformer and convolutions
        n_layers (int, optional): Number of Transformer decoder layers (default: 4)
        n_heads (int, optional): Number of attention heads in Transformer (default: 4)
        mlp_ratio (int, optional): Ratio for feedforward dimension in Transformer (default: 4)
        downsample_factor (int, optional): Number of upsampling stages. Must match the encoder's
            downsample_factor. If 0, no upsampling is applied. If > 0, restores sequence length by
            2^downsample_factor (default: 0)
        neg_slope (float, optional): Negative slope for LeakyReLU activation (default: 0.2)
        affine (bool, optional): Whether to use learnable affine parameters in normalization layers
            (default: True)
    """

    def __init__(self, out_dim, hidden_dim, n_layers=4, n_heads=4, mlp_ratio=4,
                downsample_factor=0, neg_slope=0.2, affine=True):
        super().__init__()
        
        # Build upsampling layers to restore original sequence length
        self.expander = nn.ModuleList()
        if downsample_factor == 0:
            # No upsampling: use single conv layer
            self.expander.append(nn.Sequential(
                        nn.Conv1d(hidden_dim, hidden_dim, kernel_size=5, stride=1, padding=2, padding_mode='replicate'),
                        nn.LeakyReLU(neg_slope, True),
                        nn.InstanceNorm1d(hidden_dim, affine=affine)))
        else:
            # First layer: transposed convolution for initial upsampling
            self.expander.append(nn.Sequential(
                        nn.ConvTranspose1d(hidden_dim, hidden_dim, kernel_size=5, stride=2, padding=2, output_padding=1, padding_mode='replicate'),
                        nn.LeakyReLU(neg_slope, True),
                        nn.InstanceNorm1d(hidden_dim, affine=affine)))
            # Additional layers: conv + repeat_interleave for further upsampling
            for _ in range(1, downsample_factor):
                self.expander.append(nn.Sequential(
                            nn.Conv1d(hidden_dim, hidden_dim, kernel_size=5, stride=1, padding=2, padding_mode='replicate'),
                            nn.LeakyReLU(neg_slope, True),
                            nn.InstanceNorm1d(hidden_dim, affine=affine)))
        
        # Build Transformer decoder (using TransformerEncoder architecture)
        decoder_layer = nn.TransformerEncoderLayer(
            d_model=hidden_dim,           # Model dimension
            nhead=n_heads,                # Number of attention heads
            dim_feedforward=hidden_dim * mlp_ratio,  # FFN hidden dimension
            activation='gelu',            # Activation function
            batch_first=True,             # Input shape: (batch, seq, feature)
            norm_first=True               # Pre-LN (layer norm before attention)
        )
        self.decoder_transformer = nn.TransformerEncoder(decoder_layer, num_layers=n_layers)
        
        # Positional and linear embeddings for Transformer input
        self.decoder_pos_embedding = PositionalEncoding(hidden_dim)
        self.decoder_linear_embedding = LinearEmbedding(hidden_dim, hidden_dim)
        
        # Final projection to output dimension
        self.feat_reverse_proj = nn.Linear(hidden_dim, out_dim)

    def forward(self, inputs):
        """
        Forward pass of the decoder.
        
        Args:
            inputs (torch.Tensor): Input tensor of shape (batch_size, seq_len // 2^downsample_factor, hidden_dim)
                Note: accepts sequence-first format (N, L, C) for consistency with encoder
        
        Returns:
            pred_recon (torch.Tensor): Reconstructed sequence of shape (batch_size, seq_len, out_dim)
        """
        # Convert from sequence-first to channel-first format: (N, L, C) -> (N, C, L)
        inputs = inputs.permute(0, 2, 1)
        
        # Apply upsampling to restore original sequence length
        # First layer: transposed conv, subsequent layers: conv + repeat_interleave
        for i, module in enumerate(self.expander):
            inputs = module(inputs).repeat_interleave(2, dim=2) if i > 0 else module(inputs)
        
        # Convert from channel-first to sequence format: (N, C, L) -> (N, L, C)
        inputs = inputs.permute(0, 2, 1)

        # Apply embeddings for Transformer
        decoder_features = self.decoder_linear_embedding(inputs)
        decoder_features = self.decoder_pos_embedding(decoder_features)
        
        # Pass through Transformer decoder layers
        decoder_features = self.decoder_transformer(decoder_features)
        
        # Project to output dimension: (N, L, hidden_dim) -> (N, L, out_dim)
        pred_recon = self.feat_reverse_proj(decoder_features)

        return pred_recon