# SPDX-License-Identifier: EUPL-1.2
# Copyright (c) 2026 Astatine OS Contributors

"""Graph neural network variants for microclimate prediction."""

from __future__ import annotations

from typing import Any


def create_gnn_model(
    input_dim: int,
    hidden_dim: int = 64,
    variant: str = "graphsage",
    dropout: float = 0.1,
) -> Any:
    """Build GraphSAGE or GAT model, fallback to MLP when torch-geometric is unavailable."""
    try:
        import torch
        import torch.nn as nn
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("torch is required for GNN model creation.") from exc

    try:
        from torch_geometric.nn import GATConv, SAGEConv  # type: ignore[import-not-found]
    except Exception:
        return nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 2),
        )

    class GNNModel(nn.Module):
        """Small configurable GNN model."""

        def __init__(self) -> None:
            super().__init__()
            if variant.lower() == "gat":
                self.conv1 = GATConv(input_dim, hidden_dim, heads=2, dropout=dropout)
                conv_out_dim = hidden_dim * 2
                self.conv2 = GATConv(conv_out_dim, hidden_dim, heads=1, dropout=dropout)
            else:
                self.conv1 = SAGEConv(input_dim, hidden_dim)
                self.conv2 = SAGEConv(hidden_dim, hidden_dim)
            self.dropout = nn.Dropout(dropout)
            self.head = nn.Linear(hidden_dim, 2)

        def forward(self, x: torch.Tensor, edge_index: torch.Tensor) -> torch.Tensor:
            x = self.conv1(x, edge_index)
            x = torch.relu(x)
            x = self.dropout(x)
            x = self.conv2(x, edge_index)
            x = torch.relu(x)
            return self.head(x)

    return GNNModel()
