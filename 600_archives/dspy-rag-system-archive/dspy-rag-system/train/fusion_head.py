"""
Learned fusion head for combining multiple retrieval signals.

This module provides a simple PyTorch neural network that learns to combine
BM25, vector similarity, title matching, and other signals into a single score.
"""

import torch
import torch.nn as nn


class FusionHead(nn.Module):
    """
    Simple neural network for learning fusion weights.

    Args:
        in_dim: Number of input features
        hidden: Hidden layer size (0 for linear model, >0 for MLP)
    """

    def __init__(self, in_dim: int, hidden: int = 0):
        super().__init__()
        self.in_dim = in_dim
        self.hidden = hidden

        if hidden > 0:
            # Two-layer MLP with GELU activation
            self.net = nn.Sequential(nn.Linear(in_dim, hidden), nn.GELU(), nn.Linear(hidden, 1))
        else:
            # Simple linear layer
            self.net = nn.Linear(in_dim, 1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass through the network.

        Args:
            x: Input tensor of shape [batch_size, in_dim]

        Returns:
            Output tensor of shape [batch_size]
        """
        return self.net(x).squeeze(-1)

    def get_num_parameters(self) -> int:
        """Get total number of trainable parameters."""
        return sum(p.numel() for p in self.parameters() if p.requires_grad)
