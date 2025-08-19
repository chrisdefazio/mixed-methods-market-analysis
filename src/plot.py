from __future__ import annotations

from pathlib import Path
from typing import Optional

import matplotlib.pyplot as plt


def _project_root() -> Path:
    """Best-effort detection of project root from current working directory."""
    cwd = Path.cwd()
    for base in [cwd, *cwd.parents]:
        if (base / "pyproject.toml").exists() or (base / ".git").exists():
            return base
    return cwd


def savefig(path: str | Path, fig: Optional[plt.Figure] = None, dpi: int = 150) -> None:
    """Save a matplotlib figure to reports/figures.

    Args:
        path: Destination path; if relative, saved under project root.
        fig: Figure to save. If None, uses `plt.gcf()`.
        dpi: Resolution in dots per inch.
    """

    target = Path(path)
    # Resolve relative paths against the detected project root
    if not target.is_absolute():
        root = _project_root()
        if target.parent == Path("."):
            target = root / "reports" / "figures" / target.name
        else:
            target = root / target

    target.parent.mkdir(parents=True, exist_ok=True)
    figure = fig if fig is not None else plt.gcf()
    figure.savefig(target, dpi=dpi, bbox_inches="tight")
