# SPDX-License-Identifier: EUPL-1.2
# Copyright (c) 2026 Astatine OS Contributors

"""Training entrypoint for the graph regressor."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from astatine_os.models.gnn import create_gnn_model
from astatine_os.models.losses import multitask_l1_loss
from astatine_os.training.datamodules import ToyDatasetConfig, build_toy_dataloaders


@dataclass(frozen=True)
class TrainConfig:
    """Training configuration."""

    input_dim: int = 12
    hidden_dim: int = 64
    variant: str = "graphsage"
    epochs: int = 3
    learning_rate: float = 1e-3
    output_dir: Path = Path("./out/checkpoints")
    seed: int = 42


def run_training(config: TrainConfig) -> Path:
    """Run a small training routine and return checkpoint path."""
    try:
        import pytorch_lightning as pl  # type: ignore[import-not-found]
        import torch
    except Exception as exc:  # pragma: no cover
        raise RuntimeError(
            "pytorch-lightning and torch are required for train command. Install with extra [all]."
        ) from exc

    class RegressionModule(pl.LightningModule):
        def __init__(self) -> None:
            super().__init__()
            self.save_hyperparameters()
            self.model = create_gnn_model(
                input_dim=config.input_dim,
                hidden_dim=config.hidden_dim,
                variant=config.variant,
            )

        def forward(self, x):
            if (
                hasattr(self.model, "forward")
                and "edge_index" in self.model.forward.__code__.co_varnames
            ):
                num_nodes = x.shape[0]
                edge_index = torch.stack(
                    [torch.arange(0, num_nodes - 1), torch.arange(1, num_nodes)],
                    dim=0,
                ).to(x.device)
                return self.model(x, edge_index)
            return self.model(x)

        def training_step(self, batch, batch_idx):
            x, y = batch
            pred = self(x)
            loss = multitask_l1_loss(pred, y)
            self.log("train_loss", loss, prog_bar=True)
            return loss

        def validation_step(self, batch, batch_idx):
            x, y = batch
            pred = self(x)
            loss = multitask_l1_loss(pred, y)
            self.log("val_loss", loss, prog_bar=True)

        def configure_optimizers(self):
            return torch.optim.Adam(self.parameters(), lr=config.learning_rate)

    pl.seed_everything(config.seed, workers=True)
    train_loader, val_loader = build_toy_dataloaders(
        ToyDatasetConfig(input_dim=config.input_dim, seed=config.seed)
    )
    config.output_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_cb = pl.callbacks.ModelCheckpoint(
        dirpath=str(config.output_dir),
        filename="astatine-os-{epoch:02d}-{val_loss:.3f}",
        monitor="val_loss",
        mode="min",
        save_top_k=1,
    )
    trainer = pl.Trainer(
        max_epochs=config.epochs,
        deterministic=True,
        logger=False,
        enable_checkpointing=True,
        callbacks=[checkpoint_cb],
        accelerator="auto",
    )
    module = RegressionModule()
    trainer.fit(module, train_loader, val_loader)
    best = checkpoint_cb.best_model_path
    return Path(best) if best else config.output_dir
