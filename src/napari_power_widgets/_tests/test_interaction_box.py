import pytest
from magicgui import magicgui

from napari_power_widgets import BoxSelector, BoxSliceSelector


@pytest.mark.parametrize(
    "widget_cls",
    [BoxSelector, BoxSliceSelector],
)
def test_magicgui(widget_cls):
    @magicgui
    def f(x: widget_cls):
        return x
