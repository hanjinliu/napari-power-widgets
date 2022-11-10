from __future__ import annotations

from typing import Tuple
from enum import Enum
from napari.utils._magicgui import find_viewer_ancestor
from magicgui.widgets import TupleEdit, SpinBox
from magicgui.widgets._bases.value_widget import UNSET
from ._buttoned import ButtonedValueWidget


class ZStepSpinBox(ButtonedValueWidget):
    """
    A SpinBox widget capable of reading the current z-step from the viewer.

    If viewer has more than 3 dimensions, the last used dimension is used.
    """

    def __init__(self, value=UNSET, nullable=False, **kwargs):
        self._spinbox = SpinBox(value=value, max=1e6, step=1)
        super().__init__(self._spinbox, text="Read slider", **kwargs)

    def _on_button_clicked(self):
        if viewer := find_viewer_ancestor(self):
            _dims = viewer.dims
            if _dims.ndim < 3:
                raise ValueError("Viewer must have at least 3 dimensions")
            step = _dims.current_step
            idx = _dims.last_used
            self.value = step[idx]


class TrackMode(Enum):
    idle = "idle"
    tracking = "tracking"

    def switched(self):
        if self == TrackMode.idle:
            return TrackMode.tracking
        else:
            return TrackMode.idle


class ZRangeEdit(ButtonedValueWidget):
    """
    Two SpinBoxes capable of tracking the change in z-step from the viewer.

    This widget enters tracking mode when the button is clicked. In tracking
    mode, change in dimension slider will be recorded to the widget. If
    ordered=True, the first value will always be smaller than the second value.

    Note that, unlike range and slice, the second value is **inclusive**.
    """

    def __init__(
        self,
        value: tuple[int, int] = UNSET,
        ordered: bool = True,
        nullable=False,
        **kwargs,
    ):
        self._ordered = ordered
        self._mode = TrackMode.idle
        _options = dict(max=1e6, step=1)
        self._zrange = TupleEdit(
            value=value, annotation=Tuple[int, int], options=_options
        )
        super().__init__(self._zrange, text="Track slider", **kwargs)

    @property
    def ordered(self) -> bool:
        """True if the range is ordered."""
        return self._ordered

    @property
    def mode(self) -> TrackMode:
        return self._mode

    @mode.setter
    def mode(self, val: TrackMode | str):
        self._mode = TrackMode(val)
        viewer = find_viewer_ancestor(self)
        if viewer is None:
            raise ValueError("No viewer found")

        if self.mode == TrackMode.tracking:
            self.button.text = "Finish tracking"
            self._start = None
            self._current_step = viewer.dims.current_step
            viewer.dims.events.current_step.connect(
                self._on_current_step_changed
            )
            viewer.dims.events.ndim.connect(self._abort_tracking)
        else:
            self.button.text = "Track slider"
            viewer.dims.events.current_step.disconnect(
                self._on_current_step_changed
            )
            viewer.dims.events.ndim.disconnect(self._abort_tracking)
        return None

    @property
    def value(self) -> tuple[int, int]:
        return self._zrange.value

    @value.setter
    def value(self, val: tuple[int, int]):
        if self.ordered:
            val = sorted(val)
        self._zrange.value = val

    def _on_button_clicked(self):
        """Switch the tracking mode."""
        self.mode = self.mode.switched()

    def _abort_tracking(self):
        self.mode = TrackMode.idle

    def _on_current_step_changed(self, event):
        if self.mode == TrackMode.idle:
            raise RuntimeError("Should not be idle.")
        viewer = find_viewer_ancestor(self)
        if viewer is None:
            raise ValueError("No viewer found")

        idx = viewer.dims.last_used
        if self._start is None:
            self._start = self._current_step[idx]

        _stop = viewer.dims.current_step[idx]
        self._zrange.value = self._start, _stop
