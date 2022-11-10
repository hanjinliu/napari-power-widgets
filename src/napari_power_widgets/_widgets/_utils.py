from __future__ import annotations

from magicgui.widgets import Widget
import napari


def find_viewer_ancestor(widget: Widget) -> napari.Viewer | None:
    from napari.utils._magicgui import find_viewer_ancestor

    return find_viewer_ancestor(widget)
