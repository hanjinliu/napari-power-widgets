from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Union

import napari
import numpy as np
from magicgui.widgets import Container, PushButton, TupleEdit
from magicgui.widgets._bases.value_widget import UNSET

from ._typing import MouseEvent

if TYPE_CHECKING:
    _RangeLike = Union[tuple[float, float], slice]
    _IntRangeLike = Union[tuple[int, int], slice]
    from napari.layers import Layer


class Mode(Enum):
    idle = "idle"
    selecting = "selecting"

    def switched(self) -> Mode:
        """Return the switched mode."""
        if self is Mode.idle:
            return Mode.selecting
        else:
            return Mode.idle


class BoxSelector(Container):
    def __init__(
        self,
        value: tuple[_RangeLike, _RangeLike] = UNSET,
        xlim: tuple[float, float] | None = None,
        ylim: tuple[float, float] | None = None,
        nullable: bool = False,
        **kwargs,
    ):
        self._setup_container(xlim, ylim)
        self._btn = PushButton(
            text="Select", tooltip="Get selection from viewer"
        )

        self._current_viewer: napari.Viewer | None = None
        self._layer_states: list[tuple[Layer, bool]] = []
        self._mode = Mode.idle

        super().__init__(
            layout="horizontal",
            widgets=[self._range_container, self._btn],
            **kwargs,
        )

        self.value = value

        self._init_signals()

    @property
    def value(self) -> tuple[tuple[float, float], tuple[float, float]]:
        """(Y, X) ranges."""
        return (self._yrange.value, self._xrange.value)

    @value.setter
    def value(self, value: tuple[_RangeLike, _RangeLike]):
        if value is UNSET:
            return
        yval, xval = value
        if isinstance(yval, slice):
            y0 = yval.start
            y1 = yval.stop
            if y0 is None:
                raise ValueError("Y slice must have a start value")
            if y1 is None:
                raise ValueError("Y slice must have a stop value")
            yval = (y0, y1)
        if isinstance(xval, slice):
            x0 = xval.start
            x1 = xval.stop
            if x0 is None:
                raise ValueError("X slice must have a start value")
            if x1 is None:
                raise ValueError("X slice must have a stop value")
            xval = (x0, x1)
        self._yrange.value = sorted(yval)
        self._xrange.value = sorted(xval)

    @property
    def mode(self) -> Mode:
        return self._mode

    @mode.setter
    def mode(self, mode: Mode | str):
        mode = Mode(mode)
        self._mode = mode
        if mode is Mode.idle:
            self._deactivate()
        elif mode is Mode.selecting:
            self._activate()
        else:
            raise RuntimeError(f"Unreachable: {mode}")

    def _activate(self):
        self._btn.text = "..."
        viewer = napari.current_viewer()
        self._current_viewer = viewer
        for layer in viewer.layers.selection:
            self._layer_states.append((layer, layer.interactive))
            layer.interactive = False

        viewer.overlays.interaction_box.points = None
        viewer.overlays.interaction_box.show = True
        viewer.mouse_drag_callbacks.append(self._on_drag)

    def _deactivate(self):
        viewer = self._current_viewer

        # update values
        points = viewer.overlays.interaction_box.points
        self.value = (
            (points[0, 0], points[1, 0]),
            (points[0, 1], points[1, 1]),
        )

        viewer.mouse_drag_callbacks.remove(self._on_drag)
        for layer, interactive in self._layer_states:
            layer.interactive = interactive
        self._current_viewer = None
        self._layer_states.clear()
        self._btn.text = "Select"

    def _on_drag(self, viewer: napari.Viewer, event: MouseEvent):
        try:
            pos0 = event.position
            pos1 = pos0
            yield
            while event.type == "mouse_move":
                pos1 = event.position
                viewer.overlays.interaction_box.points = np.stack(
                    [pos0, pos1], axis=0
                )
                yield
        finally:
            self.mode = Mode.idle

    def _on_button_clicked(self):
        self.mode = self.mode.switched()

    def _setup_container(self, xlim, ylim):
        if xlim is None:
            xlim = (0.0, 10000.0)
        if ylim is None:
            ylim = (0.0, 10000.0)

        self._xrange = TupleEdit(
            (xlim[0], xlim[0]),
            options={"min": xlim[0], "max": xlim[1]},
            label="X",
        )
        self._yrange = TupleEdit(
            (ylim[0], ylim[0]),
            options={"min": ylim[0], "max": ylim[1]},
            label="Y",
        )
        range_container = Container(
            widgets=[self._xrange, self._yrange], labels=True
        )
        range_container.margins = (0, 0, 0, 0)
        self._range_container = range_container
        return None

    def _init_signals(self):
        # disconnect unused signals
        self._range_container.changed.disconnect()
        self._btn.changed.disconnect()

        # connect signals
        self._range_container.changed.connect(
            lambda: self.changed.emit(self.value)
        )
        self._btn.changed.connect(self._on_button_clicked)

        return None


class BoxSliceSelector(BoxSelector):
    def __init__(
        self,
        value: tuple[_IntRangeLike, _IntRangeLike] = UNSET,
        xlim: tuple[int, int] | None = None,
        ylim: tuple[int, int] | None = None,
        nullable: bool = False,
        **kwargs,
    ):
        super().__init__(value, xlim, ylim, nullable, **kwargs)

    @property
    def value(self) -> tuple[tuple[int, int], tuple[int, int]]:
        """(Y, X) ranges in form of slices."""
        return (slice(*self._yrange.value), slice(*self._xrange.value))

    @value.setter
    def value(self, value: tuple[_IntRangeLike, _IntRangeLike]):
        if value is UNSET:
            return
        yval, xval = value
        if isinstance(yval, slice):
            y0 = yval.start
            y1 = yval.stop
            if y0 is None:
                raise ValueError("Y slice must have a start value")
            if y1 is None:
                raise ValueError("Y slice must have a stop value")
            yval = (int(y0), int(y1))
        else:
            y0, y1 = yval
            yval = (int(np.ceil(y0)), int(y1))
        if isinstance(xval, slice):
            x0 = xval.start
            x1 = xval.stop
            if x0 is None:
                raise ValueError("X slice must have a start value")
            if x1 is None:
                raise ValueError("X slice must have a stop value")
            xval = (int(x0), int(x1))
        else:
            x0, x1 = xval
            xval = (int(np.ceil(x0)), int(x1))
        self._yrange.value = sorted(yval)
        self._xrange.value = sorted(xval)

    def _setup_container(self, xlim, ylim):
        if xlim is None:
            xlim = (0, 10000)
        if ylim is None:
            ylim = (0, 10000)

        self._xrange = TupleEdit(
            (xlim[0], xlim[0]),
            options={"min": xlim[0], "max": xlim[1]},
            label="X",
        )
        self._yrange = TupleEdit(
            (ylim[0], ylim[0]),
            options={"min": ylim[0], "max": ylim[1]},
            label="Y",
        )
        range_container = Container(
            widgets=[self._xrange, self._yrange], labels=True
        )
        range_container.margins = (0, 0, 0, 0)
        self._range_container = range_container
        return None
