"""Full deterministic semantic critical-path reference for ASET."""

from .engine import (
    EFFECT_CLASSES,
    GATE_WRITES,
    DeterministicConnector,
    ReferenceError,
    ReferenceMachine,
    run_critical_path,
)
from .model import (
    Artifact,
    Context,
    CoreResolution,
    CriticalPathResult,
    EffectRecord,
    GateCrossing,
    GovernedPatch,
    Permit,
    PermitUseReceipt,
)

__version__ = "0.2.0"

__all__ = [
    "EFFECT_CLASSES",
    "GATE_WRITES",
    "Artifact",
    "Context",
    "CoreResolution",
    "CriticalPathResult",
    "DeterministicConnector",
    "EffectRecord",
    "GateCrossing",
    "GovernedPatch",
    "Permit",
    "PermitUseReceipt",
    "ReferenceError",
    "ReferenceMachine",
    "run_critical_path",
]
