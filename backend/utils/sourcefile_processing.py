from typing import Optional

# Lightweight shim module to provide a stable import path for tests
# and helpers used in sourcefile processing utilities.

try:
    # Prefer the shared utility implementation
    from gjdutils.dt import dt_str as _dt_str  # type: ignore
except Exception:  # pragma: no cover - fallback for environments without gjdutils
    from datetime import datetime

    def _dt_str(dt: Optional[datetime] = None, seconds: bool = True, tz: Optional[str] = None) -> str:
        now = dt or datetime.now()
        return now.strftime("%y%m%d_%H%M%S" if seconds else "%y%m%d_%H%M")


def dt_str(dt: Optional["datetime"] = None, seconds: bool = True, tz: Optional[str] = None) -> str:  # type: ignore[name-defined]
    """Return a compact timestamp string, delegating to gjdutils when available.

    Format example: 250915_134501
    """
    return _dt_str(dt=dt, seconds=seconds, tz=tz)


