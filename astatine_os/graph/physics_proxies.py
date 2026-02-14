# SPDX-License-Identifier: EUPL-1.2
# Copyright (c) 2026 Astatine OS Contributors

"""Physics-inspired proxy computation for urban microclimate."""

from __future__ import annotations


def compute_physics_proxies(
    building_density: float,
    mean_building_height_m: float,
    street_width_m: float,
    street_orientation_deg: float,
    vegetation_fraction: float,
    green_view_ratio: float,
) -> dict[str, float]:
    """Estimate interpretable physical proxies."""
    canyon_aspect_ratio = mean_building_height_m / max(2.0, street_width_m)
    sky_view_factor_proxy = max(0.05, 1.0 - min(0.95, canyon_aspect_ratio * 0.6))
    roughness_proxy = building_density * (mean_building_height_m / 25.0)
    ventilation_barrier_proxy = (1.0 - sky_view_factor_proxy) * (1.0 + roughness_proxy)
    orientation_factor = abs((street_orientation_deg % 180.0) - 90.0) / 90.0
    vegetation_cooling_proxy = 0.5 * vegetation_fraction + 0.5 * green_view_ratio
    return {
        "canyon_aspect_ratio": float(canyon_aspect_ratio),
        "sky_view_factor_proxy": float(sky_view_factor_proxy),
        "roughness_proxy": float(roughness_proxy),
        "ventilation_barrier_proxy": float(ventilation_barrier_proxy),
        "orientation_factor": float(orientation_factor),
        "vegetation_cooling_proxy": float(vegetation_cooling_proxy),
    }
