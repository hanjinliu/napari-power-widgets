"""Widgets that use temporal shapes layer for the input."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
import numpy as np

from magicgui.widgets import Table
from magicgui.widgets._bases.value_widget import UNSET

import napari

from ._buttoned import ButtonedValueWidget
from ._mouse import MouseInteractivityMixin, Mode
from ._typing import MouseEvent

if TYPE_CHECKING:
    from numpy.typing import ArrayLike
    from napari.layers import Shapes


class _ShapeDataEdit(ButtonedValueWidget, MouseInteractivityMixin):
    SHAPE_MODE: str = ""

    def __init__(self, value=UNSET, nullable=False, **kwargs):
        self._table_data = self._init_data()
        data_table = Table(
            value=self._table_data, columns=["Y", "X"], name="data"
        )
        data_table.min_height = 30
        data_table.read_only = True
        self._table = data_table
        super().__init__(data_table, text="Draw", **kwargs)

        self.value = value
        self._layer: Shapes | None = None
        self._mode = Mode.idle

    def _init_data(self) -> np.ndarray:
        raise NotImplementedError()

    def _validate_data(self, value: Any) -> np.ndarray:
        raise NotImplementedError()

    @property
    def value(self) -> np.ndarray:
        """Line data array in [[Ystart, Xstart], [Yend, Xend]] format."""
        return self._table_data

    @value.setter
    def value(self, value: np.ndarray):
        if value is UNSET:
            return
        value = self._validate_data(value)
        self._table_data = value
        self._table.value = value

    def _activate(self):
        self._btn.text = "Drawing"
        viewer = napari.current_viewer()
        self._layer = viewer.add_shapes(
            ndim=2,
            face_color=[0, 0, 0, 0],
            edge_color=[0, 0.6, 1, 1],  # same as napari interaction box
            opacity=1.0,
            edge_width=1.0,
            name="Temporal Layer",
        )
        self._force_layer_mode()
        self._layer.events.data.connect(self._on_data_added)
        self._layer.events.mode.connect(self._force_layer_mode)
        self._current_viewer = viewer
        self._layer.mouse_drag_callbacks.append(self._on_drag)

    def _deactivate(self):
        # update values
        if self._layer.nshapes > 0:
            self.value = self._layer.data[0]
        self._remove_temp_layer()

        self._btn.text = "Draw"

    def _remove_temp_layer(self):
        viewer = self._current_viewer
        viewer.layers.remove(self._layer)
        self._layer.mouse_drag_callbacks.remove(self._on_drag)
        self._layer = None

    def _on_data_added(self):
        if self._layer.nshapes > 1:
            self.mode = Mode.idle

    def _force_layer_mode(self):
        if self._layer.nshapes == 1:
            if self._layer.mode != "SELECT":
                self._layer.mode = "SELECT"
            if self._layer.nshapes > 0:
                self._layer.selected_data = {0}
        else:
            if self._layer.mode != self.SHAPE_MODE:
                self._layer.mode = self.SHAPE_MODE

    def _on_drag(self, layer: Shapes, event: MouseEvent):
        try:
            yield
            if layer.nshapes > 0 and layer.selected_data == set():
                # if shape selection is lost, switch to idle mode
                self.mode = Mode.idle
                return
            while event.type == "mouse_move":
                if layer.nshapes > 0:
                    self.value = layer.data[0]
                yield
            self._force_layer_mode()
            layer.selected_data = {0}
        except Exception:
            self.mode = Mode.idle

    def _on_button_clicked(self):
        self._switch_mode()


class LineDataEdit(_ShapeDataEdit):
    SHAPE_MODE = "ADD_LINE"

    def _init_data(self) -> np.ndarray:
        return np.zeros((2, 2), dtype=np.float64)

    def _validate_data(self, value: ArrayLike) -> np.ndarray:
        value = np.asarray(value, dtype=np.float64)
        if value.shape != (2, 2):
            raise ValueError("Line data must be (2, 2) array")
        return value


class PathDataEdit(_ShapeDataEdit):
    SHAPE_MODE = "ADD_PATH"

    def _init_data(self) -> np.ndarray:
        return np.zeros((1, 2), dtype=np.float64)

    def _validate_data(self, value: ArrayLike) -> np.ndarray:
        value = np.asarray(value, dtype=np.float64)
        if value.ndim != 2 or value.shape[1] != 2:
            raise ValueError("Line data must be (N, 2) array")
        return value


class RectangleDataEdit(_ShapeDataEdit):
    SHAPE_MODE = "ADD_RECTANGLE"

    def _init_data(self) -> np.ndarray:
        return np.zeros((4, 2), dtype=np.float64)

    def _validate_data(self, value: ArrayLike) -> np.ndarray:
        value = np.asarray(value, dtype=np.float64)
        if value.shape != (4, 2):
            raise ValueError("Line data must be (N, 2) array")
        return value


class PolygonDataEdit(_ShapeDataEdit):
    SHAPE_MODE = "ADD_POLYGON"

    def _init_data(self) -> np.ndarray:
        return np.zeros((1, 2), dtype=np.float64)

    def _validate_data(self, value: ArrayLike) -> np.ndarray:
        value = np.asarray(value, dtype=np.float64)
        if value.shape != (4, 2):
            raise ValueError("Line data must be (N, 2) array")
        return value


class EllipseDataEdit(_ShapeDataEdit):
    SHAPE_MODE = "ADD_ELLIPSE"

    def _init_data(self) -> np.ndarray:
        return np.zeros((4, 2), dtype=np.float64)

    def _validate_data(self, value: ArrayLike) -> np.ndarray:
        value = np.asarray(value, dtype=np.float64)
        if value.shape != (4, 2):
            raise ValueError("Line data must be (N, 2) array")
        return value
