# SPDX-License-Identifier: EUPL-1.2
# Copyright (c) 2026 Astatine OS Contributors

"""Neighborhood airflow graph construction."""

from __future__ import annotations

import math
from collections.abc import Iterable

import networkx as nx

from astatine_os.graph.schemas import TileFeature


def _distance(a: TileFeature, b: TileFeature) -> float:
    dx = a.lon - b.lon
    dy = a.lat - b.lat
    return math.sqrt(dx * dx + dy * dy)


def build_airflow_graph(features: Iterable[TileFeature], k_neighbors: int = 4) -> nx.Graph:
    """Create an undirected graph using k-nearest neighbors by tile centroid."""
    nodes = list(features)
    graph = nx.Graph()
    for node in nodes:
        graph.add_node(node.tile_id, feature=node)

    for node in nodes:
        distances = sorted(
            ((_distance(node, other), other) for other in nodes if other.tile_id != node.tile_id),
            key=lambda item: item[0],
        )
        for dist, neighbor in distances[:k_neighbors]:
            weight = max(1e-6, 1.0 / (1.0 + dist))
            graph.add_edge(node.tile_id, neighbor.tile_id, weight=weight)
    return graph
