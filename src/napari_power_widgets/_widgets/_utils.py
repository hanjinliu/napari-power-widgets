from __future__ import annotations

from magicgui import use_app
from magicgui.widgets import Widget, Label
import napari


def find_viewer_ancestor(widget: Widget) -> napari.Viewer | None:
    """Find the napari viewer ancestor of a magicgui widget."""
    # lazy import version
    from napari.utils._magicgui import find_viewer_ancestor

    return find_viewer_ancestor(widget)


def minimize_label_width(widget: Label) -> None:
    _measure = use_app().get_obj("get_text_width")
    widget.max_width = _measure(widget.value)
    return None
