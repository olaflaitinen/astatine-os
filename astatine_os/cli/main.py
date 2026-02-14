# SPDX-License-Identifier: EUPL-1.2
# Copyright (c) 2026 Astatine OS Contributors

"""CLI for astatine-os."""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

from astatine_os.api import analyze_microclimate
from astatine_os.config import get_runtime_config
from astatine_os.data.aoi import NominatimGeocoder, resolve_place
from astatine_os.data.providers import (
    ERA5LandProvider,
    KartaViewProvider,
    OpenBuildingsProvider,
    Sentinel2Provider,
    TimeRange,
)
from astatine_os.logging import configure_logging
from astatine_os.reporting.report_md import write_markdown_report
from astatine_os.training.eval import evaluate_checkpoint
from astatine_os.training.train import TrainConfig, run_training


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="astatine-os")
    sub = parser.add_subparsers(dest="command", required=True)

    analyze = sub.add_parser("analyze", help="Run end-to-end microclimate analysis.")
    analyze.add_argument("--place", required=True)
    analyze.add_argument("--start", required=True)
    analyze.add_argument("--end", required=True)
    analyze.add_argument("--out", required=True)
    analyze.add_argument("--workers", type=int, default=2)

    data = sub.add_parser("data", help="Data operations.")
    data_sub = data.add_subparsers(dest="data_command", required=True)
    data_sub.add_parser("list-providers", help="List built-in data providers.")

    fetch = data_sub.add_parser("fetch", help="Fetch provider snapshots.")
    fetch.add_argument("--place", required=True)
    fetch.add_argument("--start", required=True)
    fetch.add_argument("--end", required=True)
    fetch.add_argument("--out", required=True)

    train = sub.add_parser("train", help="Train a baseline model.")
    train.add_argument("--out", required=True)
    train.add_argument("--epochs", type=int, default=3)

    eval_cmd = sub.add_parser("eval", help="Evaluate a checkpoint.")
    eval_cmd.add_argument("--checkpoint", required=True)

    report = sub.add_parser("report", help="Regenerate markdown report from JSON outputs.")
    report.add_argument("--place", required=True)
    report.add_argument("--start", required=True)
    report.add_argument("--end", required=True)
    report.add_argument("--out", required=True)

    return parser


def _handle_data_fetch(args: argparse.Namespace) -> int:
    cfg = get_runtime_config(out_dir=Path(args.out))
    geocoder = NominatimGeocoder(cfg.geocoder_user_agent)
    aoi = resolve_place(args.place, geocoder)
    time_range = TimeRange(start=date.fromisoformat(args.start), end=date.fromisoformat(args.end))

    providers = [
        Sentinel2Provider(use_live_stac=False),
        ERA5LandProvider(cfg.era5_cds_url, cfg.era5_cds_key),
        OpenBuildingsProvider(),
        KartaViewProvider(),
    ]
    snapshot = {"place": args.place, "providers": []}
    for provider in providers:
        payload = provider.fetch(aoi, time_range, resolution=10, bands=None)
        snapshot["providers"].append(
            {
                "name": provider.__class__.__name__,
                "source": payload.source,
                "metadata": payload.metadata,
                "attribution": provider.attribution(),
                "license": provider.license(),
            }
        )
    out_path = Path(args.out).expanduser().resolve()
    out_path.mkdir(parents=True, exist_ok=True)
    (out_path / "data_fetch_summary.json").write_text(
        json.dumps(snapshot, indent=2), encoding="utf-8"
    )
    print(f"Wrote provider snapshot to {out_path / 'data_fetch_summary.json'}")
    return 0


def _handle_report(args: argparse.Namespace) -> int:
    out_dir = Path(args.out).expanduser().resolve()
    preds_file = out_dir / "predictions_summary.json"
    if not preds_file.exists():
        raise FileNotFoundError(f"Expected predictions summary at {preds_file}")
    payload = json.loads(preds_file.read_text(encoding="utf-8"))
    features = []
    predictions = []
    from astatine_os.graph.schemas import GraphPrediction, TileFeature

    for item in payload["tile_features"]:
        features.append(TileFeature(**item))
    for item in payload["predictions"]:
        predictions.append(GraphPrediction(**item))
    write_markdown_report(
        path=out_dir / "report.md",
        place=args.place,
        start_date=args.start,
        end_date=args.end,
        tile_features=features,
        predictions=predictions,
        assumptions=payload.get("assumptions", []),
    )
    print(f"Wrote report to {out_dir / 'report.md'}")
    return 0


def main(argv: list[str] | None = None) -> int:
    """Run CLI."""
    configure_logging()
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "analyze":
        result = analyze_microclimate(
            place=args.place,
            start=args.start,
            end=args.end,
            out_dir=Path(args.out),
            config_overrides={"dask_workers": args.workers},
        )
        print(f"Analysis complete. Outputs in {result.output_dir}")
        return 0
    if args.command == "data":
        if args.data_command == "list-providers":
            providers = [
                "Sentinel2Provider",
                "LandsatThermalProvider",
                "ERA5LandProvider",
                "OpenBuildingsProvider",
                "OSMBuildingsProvider",
                "KartaViewProvider",
                "MapillaryProvider",
            ]
            print("\n".join(providers))
            return 0
        if args.data_command == "fetch":
            return _handle_data_fetch(args)
    if args.command == "train":
        ckpt = run_training(
            TrainConfig(
                output_dir=Path(args.out).expanduser().resolve(),
                epochs=args.epochs,
            )
        )
        print(f"Best checkpoint: {ckpt}")
        return 0
    if args.command == "eval":
        metrics = evaluate_checkpoint(Path(args.checkpoint).expanduser().resolve())
        print(json.dumps(metrics, indent=2))
        return 0
    if args.command == "report":
        return _handle_report(args)
    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
