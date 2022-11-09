from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

import napari

if TYPE_CHECKING:
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


class MouseInteractivityMixin:
    @property
    def mode(self) -> Mode:
        """Get the interactivity mode."""
        return self._mode

    @mode.setter
    def mode(self, mode: Mode | str):
        """Set the interactivity mode."""
        mode = Mode(mode)
        self._mode = mode
        if mode is Mode.idle:
            self._deactivate()
        elif mode is Mode.selecting:
            self._activate()
        else:
            raise RuntimeError(f"Unreachable: {mode}")

    def _activate(self):
        raise NotImplementedError()

    def _deactivate(self):
        raise NotImplementedError()

    def _switch_mode(self):
        """Switch the interactivity mode."""
        self.mode = self.mode.switched()

    def _freeze_layers(self, viewer: napari.Viewer):
        from napari.layers import Shapes

        self._current_viewer = viewer
        self._layer_states: list[tuple[Layer, bool]] = []
        for layer in viewer.layers.selection:
            self._layer_states.append((layer, layer.interactive))
            layer.interactive = False
            if isinstance(layer, Shapes):
                # Shapes layer interactivity cannot be disabled if the layer
                # is in add_XXX mode.
                layer.mode = "pan_zoom"

    def _unfreeze_layers(self):
        for layer, interactive in self._layer_states:
            layer.interactive = interactive
        self._current_viewer = None
        self._layer_states.clear()
