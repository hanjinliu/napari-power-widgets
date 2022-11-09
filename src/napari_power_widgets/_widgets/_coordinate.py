from __future__ import annotations

from typing import TYPE_CHECKING, Union, NamedTuple

import napari
import numpy as np
from magicgui.widgets import Container, PushButton, TupleEdit, FloatSpinBox
from magicgui.widgets._bases.value_widget import UNSET

from ._typing import MouseEvent
from ._mouse import MouseInteractivityMixin, Mode

if TYPE_CHECKING:
    _RangeLike = Union[tuple[float, float], slice]
    # _IntRangeLike = Union[tuple[int, int], slice]


class BoxRange(NamedTuple):
    y: _RangeLike
    x: _RangeLike


class BoxSelector(Container, MouseInteractivityMixin):
    def __init__(
        self,
        value: tuple[_RangeLike, _RangeLike] = UNSET,
        nullable: bool = False,
        **kwargs,
    ):
        self._setup_container()
        self._btn = PushButton(
            text="Select", tooltip="Get a box selection from the viewer"
        )

        self._mode = Mode.idle

        super().__init__(
            layout="horizontal",
            widgets=[self._range_container, self._btn],
            **kwargs,
        )

        self.value = value

        self._init_signals()

    @property
    def value(self) -> BoxRange:
        """(Y, X) ranges."""
        return BoxRange(y=self._yrange.value, x=self._xrange.value)

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

    def _activate(self):
        self._btn.text = "..."
        viewer = napari.current_viewer()
        self._freeze_layers(viewer)
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
        self._unfreeze_layers()
        self._btn.text = "Select"

    def _on_drag(self, viewer: napari.Viewer, event: MouseEvent):
        try:
            pos0 = event.position
            pos1 = pos0
            yield
            while event.type == "mouse_move":
                pos1 = event.position
                points = np.stack([pos0, pos1], axis=0)
                viewer.overlays.interaction_box.points = points
                self.value = (
                    (points[0, 0], points[1, 0]),
                    (points[0, 1], points[1, 1]),
                )
                yield
        finally:
            self.mode = Mode.idle

    def _setup_container(self):
        self._xrange = TupleEdit(
            (0.0, 0.0),
            options={"min": -1e6, "max": 1e6},
            label="X",
        )
        self._yrange = TupleEdit(
            (0.0, 0.0),
            options={"min": -1e6, "max": 1e6},
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
        self._btn.changed.connect(self._switch_mode)

        return None


# TODO: `BoxSliceSelector` does not consider layer transformation at the
# moment.
# class BoxSliceSelector(BoxSelector):
#     @property
#     def value(self) -> tuple[tuple[int, int], tuple[int, int]]:
#         """(Y, X) ranges in form of slices."""
#         return (slice(*self._yrange.value), slice(*self._xrange.value))

#     @value.setter
#     def value(self, value: tuple[_IntRangeLike, _IntRangeLike]):
#         if value is UNSET:
#             return
#         yval, xval = value
#         if isinstance(yval, slice):
#             y0 = yval.start
#             y1 = yval.stop
#             if y0 is None:
#                 raise ValueError("Y slice must have a start value")
#             if y1 is None:
#                 raise ValueError("Y slice must have a stop value")
#             yval = (int(y0), int(y1))
#         else:
#             y0, y1 = yval
#             yval = (int(np.ceil(y0)), int(y1))
#         if isinstance(xval, slice):
#             x0 = xval.start
#             x1 = xval.stop
#             if x0 is None:
#                 raise ValueError("X slice must have a start value")
#             if x1 is None:
#                 raise ValueError("X slice must have a stop value")
#             xval = (int(x0), int(x1))
#         else:
#             x0, x1 = xval
#             xval = (int(np.ceil(x0)), int(x1))
#         self._yrange.value = sorted(yval)
#         self._xrange.value = sorted(xval)

#     def _setup_container(self):
#         self._xrange = TupleEdit(
#             (0, 0),
#             options={"min": -1e6, "max": 1e6},
#             label="X",
#         )
#         self._yrange = TupleEdit(
#             (0, 0),
#             options={"min": -1e6, "max": 1e6},
#             label="Y",
#         )
#         range_container = Container(
#             widgets=[self._xrange, self._yrange], labels=True
#         )
#         range_container.margins = (0, 0, 0, 0)
#         self._range_container = range_container
#         return None


class CoordinateSelector(Container, MouseInteractivityMixin):
    def __init__(
        self,
        value: tuple[_RangeLike, _RangeLike] = UNSET,
        nullable: bool = False,
        **kwargs,
    ):
        self._xpos = FloatSpinBox(value=0.0, label="X", min=-1e6, max=1e6)
        self._ypos = FloatSpinBox(value=0.0, label="Y", min=-1e6, max=1e6)
        self._btn = PushButton(
            text="Select", tooltip="Get a point from viewer"
        )

        self._mode = Mode.idle

        super().__init__(
            layout="horizontal",
            widgets=[self._xpos, self._ypos, self._btn],
            **kwargs,
        )

        self.value = value
        self._xpos.changed.disconnect()
        self._ypos.changed.disconnect()
        self._btn.changed.disconnect()

        self._btn.changed.connect(self._switch_mode)
        self._xpos.changed.connect(lambda: self.changed.emit(self.value))
        self._ypos.changed.connect(lambda: self.changed.emit(self.value))

    @property
    def value(self) -> np.ndarray:
        """Coordinate in (Y, X) order."""
        return np.array([self._ypos.value, self._xpos.value], dtype=np.float64)

    @value.setter
    def value(self, pos):
        """Set coordinate."""
        if pos is UNSET:
            return
        self._ypos.value, self._xpos.value = pos

    def _activate(self):
        self._btn.text = "..."
        viewer = napari.current_viewer()
        viewer.overlays.interaction_box.show = False
        self._freeze_layers(viewer)
        viewer.mouse_drag_callbacks.append(self._on_click)

    def _deactivate(self):
        viewer = self._current_viewer
        viewer.mouse_drag_callbacks.remove(self._on_click)
        self._unfreeze_layers()
        self._btn.text = "Select"

    def _on_click(self, viewer: napari.Viewer, event: MouseEvent):
        init = True
        try:
            pos0 = event.position
            px0 = event.pos
            yield
            while event.type == "mouse_move":
                yield  # do nothing
            px1 = event.pos
            if np.sum(px0 - px1) < 2:
                self.value = pos0
                viewer.overlays.interaction_box.show = True
                viewer.overlays.interaction_box.points = pos0
            else:
                init = False
        finally:
            if init:
                self.mode = Mode.idle
