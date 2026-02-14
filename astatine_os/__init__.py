# SPDX-License-Identifier: EUPL-1.2
# Copyright (c) 2026 Astatine OS Contributors

"""Public package API for astatine_os."""

from astatine_os.api import AnalysisResult, analyze_microclimate
from astatine_os.version import __version__

__all__ = ["AnalysisResult", "__version__", "analyze_microclimate"]
