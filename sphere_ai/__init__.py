"""Sphere AI Python SDK for LLM interception and agentic security."""

from typing import Dict

from .engine import PolicyEngine, PolicyConfig
from .exceptions import (
    SphereSecurityViolation,
    SpherePolicyError,
    SphereConfigurationError,
)
from .logging import AuditLogger

_missing_dependencies: Dict[str, ModuleNotFoundError] = {}

try:  # Optional dependency: OpenAI SDK
    from .client import SphereClient
except ModuleNotFoundError as exc:  # pragma: no cover - triggered when optional deps missing
    SphereClient = None  # type: ignore[assignment]
    _missing_dependencies["SphereClient"] = exc
else:  # pragma: no cover - not triggered in CI
    _missing_dependencies.pop("SphereClient", None)

try:  # Optional dependency: PyYAML
    from .config import load_config_from_yaml
except ModuleNotFoundError as exc:  # pragma: no cover - triggered when optional deps missing
    load_config_from_yaml = None  # type: ignore[assignment]
    _missing_dependencies["load_config_from_yaml"] = exc
else:  # pragma: no cover - not triggered in CI
    _missing_dependencies.pop("load_config_from_yaml", None)

__version__ = "0.1.0"

__all__ = [
    "PolicyEngine",
    "PolicyConfig",
    "SphereSecurityViolation",
    "SpherePolicyError",
    "SphereConfigurationError",
    "AuditLogger",
    "__version__",
]

if load_config_from_yaml is not None:
    __all__.append("load_config_from_yaml")
if SphereClient is not None:
    __all__.append("SphereClient")


def __getattr__(name: str):  # pragma: no cover - simple attribute helper
    if name in _missing_dependencies:
        if name == "SphereClient":
            raise ModuleNotFoundError(
                "SphereClient requires the optional 'openai' dependency. Install the OpenAI "
                "Python package to use SphereClient."
            ) from _missing_dependencies[name]
        if name == "load_config_from_yaml":
            raise ModuleNotFoundError(
                "load_config_from_yaml requires the optional 'pyyaml' dependency. Install PyYAML "
                "to load policy configurations from YAML files."
            ) from _missing_dependencies[name]
    raise AttributeError(f"module 'sphere_ai' has no attribute {name!r}")
