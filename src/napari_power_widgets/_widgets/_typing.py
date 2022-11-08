from __future__ import annotations

import numpy as np


class MouseEvent:
    """Mimics a napari MouseEvent."""

    blocked: bool
    button: int
    buttons: list[int]
    delta: np.ndarray
    modifiers: list[str]
    type: str
    pos: np.ndarray
    position: np.ndarray
