from __future__ import annotations

from typing import Sequence, TYPE_CHECKING
import weakref

import numpy as np
from magicgui.widgets import Container, ComboBox, Select
from magicgui.widgets._bases import CategoricalWidget
from magicgui.widgets._bases.value_widget import UNSET

from ._utils import find_viewer_ancestor

if TYPE_CHECKING:
    from napari.layers import Shapes


def _get_shapes_layer(w: CategoricalWidget):
    from napari.layers import Shapes

    if viewer := find_viewer_ancestor(w.native):
        return [x for x in viewer.layers if isinstance(x, Shapes)]
    return []


class ShapeComboBox(Container):
    _shape_selection_widget_cls = ComboBox

    def __init__(
        self,
        value=UNSET,
        nullable=False,
        filter: list[str] | None = None,
        **kwargs,
    ):
        if filter is None:
            filter = ["line", "polygon", "rectangle", "ellipse", "path"]
        self._filter = filter
        self._layer_cbox = ComboBox(choices=_get_shapes_layer, nullable=False)
        self._shape_cbox = self._shape_selection_widget_cls(
            choices=self._get_available_shape_id, nullable=False
        )
        super().__init__(
            widgets=[self._layer_cbox, self._shape_cbox], **kwargs
        )
        self._layer_cbox.changed.disconnect()
        self._shape_cbox.changed.disconnect()
        self._layer_cbox.changed.connect(self._layer_changed)
        self._shape_cbox.changed.connect(self._focus_on_selected_shape)

        self._event_connected_layer: weakref.ReferenceType[Shapes] = None
        self.value = value

    @property
    def value(self) -> np.ndarray:
        return self.shapes_layer.data[self._shape_cbox.value]

    @value.setter
    def value(self, shape: tuple[Shapes, int]):
        if shape is UNSET:
            return
        self._layer_cbox.value = shape[0]
        self._shape_cbox.value = shape[1]

    @property
    def shapes_layer(self) -> Shapes:
        """Currently selected shapes layer."""
        return self._layer_cbox.value

    def _get_event_connected_layer(self) -> Shapes | None:
        if self._event_connected_layer is None:
            return None
        return self._event_connected_layer

    def _shape_filter(self, i: int, type: str) -> bool:
        return type in self._filter

    def _get_available_shape_id(self, w: CategoricalWidget):
        layer = self.shapes_layer
        if layer is None:
            return []
        return [
            (f"{idx}: {type}", idx)
            for idx, type in enumerate(layer.shape_type)
            if self._shape_filter(idx, type)
        ]

    def _focus_on_selected_shape(self, idx: int):
        layer = self.shapes_layer
        layer.selected_data = {idx}
        data: np.ndarray = layer.data[idx]
        ndim = data.shape[1]
        if ndim > 2:
            center = np.mean(data[:, :-2], axis=0)
            viewer = find_viewer_ancestor(self)
            viewer.dims.set_current_step(range(ndim - 2), center[0])

    def _layer_changed(self, layer: Shapes):
        self._shape_cbox.reset_choices()
        if old_layer := self._get_event_connected_layer():
            try:
                old_layer.events.data.disconnect(
                    self._shape_cbox.reset_choices
                )
            except Exception:
                pass
        self._event_connected_layer = weakref.ref(layer)
        layer.events.data.connect(self._shape_cbox.reset_choices)
        return None


class ShapeSelect(ShapeComboBox):
    _shape_selection_widget_cls = Select

    def _focus_on_selected_shape(self, indices: Sequence[int]):
        if len(indices) != 1:
            return
        idx = indices[0]
        layer = self.shapes_layer
        layer.selected_data = {idx}
        data: np.ndarray = layer.data[idx]
        ndim = data.shape[1]
        if ndim > 2:
            center = np.mean(data[:, :-2], axis=0)
            viewer = find_viewer_ancestor(self)
            viewer.dims.set_current_step(range(ndim - 2), center[0])
