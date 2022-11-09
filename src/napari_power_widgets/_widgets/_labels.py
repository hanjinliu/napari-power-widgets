from __future__ import annotations

from napari.layers import Labels
from napari.utils._magicgui import find_viewer_ancestor
import numpy as np
from magicgui import application as app
from magicgui.widgets import Container, ComboBox, Label, SpinBox, PushButton
from magicgui.widgets._bases import CategoricalWidget
from magicgui.widgets._bases.value_widget import UNSET
import napari

from ._mouse import Mode, MouseInteractivityMixin
from ._typing import MouseEvent


def _get_labels_layer(w: CategoricalWidget):
    if viewer := find_viewer_ancestor(w.native):
        return [x for x in viewer.layers if isinstance(x, Labels)]
    return []


class LabelComboBox(Container, MouseInteractivityMixin):
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
        self._layer_cbox = ComboBox(choices=_get_labels_layer, nullable=False)
        self._index_cbox = SpinBox(0, max=1e6, step=1)
        self._btn = PushButton(text="Select")
        label = Label(value="==")
        _measure = app.use_app().get_obj("get_text_width")
        label.max_width = _measure(label.value)
        super().__init__(
            widgets=[self._layer_cbox, label, self._index_cbox, self._btn],
            layout="horizontal",
            **kwargs,
        )
        self._layer_cbox.changed.disconnect()
        self._index_cbox.changed.disconnect()
        self._btn.changed.disconnect()
        self._layer_cbox.changed.connect(self._layer_changed)
        self._index_cbox.changed.connect(self._index_changed)
        self._btn.changed.connect(self._switch_mode)

        self.value = value

    @property
    def value(self) -> np.ndarray:
        layer: Labels = self._layer_cbox.value
        return layer.data == self._index_cbox.value

    @value.setter
    def value(self, shape: tuple[Labels, int]):
        if shape is UNSET:
            return
        self._layer_cbox.value = shape[0]
        self._index_cbox.value = shape[1]

    def _get_index_list(self, w: CategoricalWidget):
        layer: Labels = self._layer_cbox.value
        if layer is None:
            return []
        return np.unique(layer.data)[1:]

    def _layer_changed(self, layer: Labels):
        # self._index_cbox.reset_choices()
        # if old_layer := self._get_event_connected_layer():
        #     try:
        #         old_layer.events.data.disconnect(
        #             self._index_cbox.reset_choices
        #         )
        #     except Exception:
        #         pass
        # self._event_connected_layer = weakref.ref(layer)
        # layer.events.data.connect(self._index_cbox.reset_choices)
        return None

    def _index_changed(self, idx: int):
        layer: Labels = self._layer_cbox.value
        try:
            layer.selected_label = idx
        except Exception:
            pass

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
