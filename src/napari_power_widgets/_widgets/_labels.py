from __future__ import annotations

from typing import TYPE_CHECKING
import numpy as np
from magicgui.widgets import (
    Container,
    ComboBox,
    Label,
    SpinBox,
    PushButton,
    Widget,
)
from magicgui.widgets._bases.value_widget import UNSET
import napari

from ._utils import find_viewer_ancestor, minimize_label_width
from ._mouse import Mode, MouseInteractivityMixin
from ._typing import MouseEvent

if TYPE_CHECKING:
    from napari.layers import Labels


def _get_labels_layer(w: Widget) -> list[Labels]:
    from napari.layers import Labels

    if viewer := find_viewer_ancestor(w.native):
        return [x for x in viewer.layers if isinstance(x, Labels)]
    return []


class LabelComboBox(Container, MouseInteractivityMixin):
    def __init__(
        self,
        value=UNSET,
        include_zero: bool = False,
        nullable: bool = False,
        **kwargs,
    ):
        self._layer_cbox = ComboBox(choices=_get_labels_layer, nullable=False)
        min = 0 if include_zero else 1
        self._spinbox = SpinBox(value=min, min=min, max=1e6, step=1)
        self._btn = PushButton(text="Select")
        self._include_zero = include_zero
        label = Label(value="==")
        minimize_label_width(label)
        super().__init__(
            widgets=[self._layer_cbox, label, self._spinbox, self._btn],
            layout="horizontal",
            **kwargs,
        )
        self._layer_cbox.changed.disconnect()
        self._spinbox.changed.disconnect()
        self._btn.changed.disconnect()
        self._spinbox.changed.connect(self._index_changed)
        self._btn.changed.connect(self._switch_mode)

        self.value = value
        self._mode = Mode.idle

    @property
    def value(self) -> np.ndarray:
        """Boolean array of the selected label."""
        layer: Labels = self._layer_cbox.value
        return layer.data == self._spinbox.value

    @value.setter
    def value(self, shape: tuple[Labels, int]):
        if shape is UNSET:
            return
        self._layer_cbox.value = shape[0]
        self._spinbox.value = shape[1]

    @property
    def include_zero(self) -> bool:
        """True if the zero label is included."""
        return self._include_zero

    def _get_index_list(self, w: Widget):
        layer: Labels = self._layer_cbox.value
        if layer is None:
            return []
        return np.unique(layer.data)[1:]

    def _index_changed(self, idx: int):
        layer: Labels = self._layer_cbox.value
        try:
            layer.selected_label = idx
        except Exception:
            pass

    def _activate(self):
        self._btn.text = "Selecting"
        viewer = napari.current_viewer()
        self._freeze_layers(viewer)
        viewer.mouse_drag_callbacks.append(self._on_click)

    def _deactivate(self):
        viewer = self._current_viewer
        self._unfreeze_layers()
        viewer.mouse_drag_callbacks.remove(self._on_click)
        self._btn.text = "Select"

    def _on_click(self, viewer: napari.Viewer, event: MouseEvent):
        init = False
        try:
            px0 = event.pos
            position = event.position
            yield
            while event.type == "mouse_move":
                yield  # do nothing
            px1 = event.pos

            if np.sum(px0 - px1) < 2:
                if out := self._get_layer_value_under_cursor(viewer, position):
                    labels, val = out
                    self._layer_cbox.value = labels
                    self._spinbox.value = val
                    init = True

        finally:
            if init:
                self.mode = Mode.idle

    def _get_layer_value_under_cursor(
        self,
        viewer: napari.Viewer,
        pos: tuple[int, int],
    ) -> tuple[Labels, int] | None:
        from napari.layers import Labels

        for layer in reversed(viewer.layers):
            if not isinstance(layer, Labels) or not layer.visible:
                continue
            val = layer.get_value(pos, world=True)

            if val is None:
                continue
            if val != 0 or self.include_zero:
                return layer, val
        return None
