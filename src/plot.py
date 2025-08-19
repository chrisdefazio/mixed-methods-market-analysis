from __future__ import annotations

from pathlib import Path
from typing import Optional

import matplotlib.pyplot as plt


def savefig(path: str | Path, fig: Optional[plt.Figure] = None, dpi: int = 150) -> None:
    """Save a matplotlib figure to reports/figures.

    Args:
        path: Destination path; if relative, saved under project root.
        fig: Figure to save. If None, uses `plt.gcf()`.
        dpi: Resolution in dots per inch.
    """

    target = Path(path)
    # Ensure path is within reports/figures if user passes a bare filename
    if not target.is_absolute() and target.parent == Path("."):
        target = Path("reports/figures") / target

    target.parent.mkdir(parents=True, exist_ok=True)
    figure = fig if fig is not None else plt.gcf()
    figure.savefig(target, dpi=dpi, bbox_inches="tight")



