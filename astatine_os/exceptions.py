# SPDX-License-Identifier: EUPL-1.2
# Copyright (c) 2026 Astatine OS Contributors

"""Custom exceptions for astatine_os."""


class AstatineOSError(Exception):
    """Base exception for package-specific errors."""


class ConfigurationError(AstatineOSError):
    """Raised when configuration is invalid."""


class ProviderError(AstatineOSError):
    """Raised when a data provider fails."""


class GeocodingError(AstatineOSError):
    """Raised when place resolution fails."""


class ModelingError(AstatineOSError):
    """Raised when model training or inference fails."""
