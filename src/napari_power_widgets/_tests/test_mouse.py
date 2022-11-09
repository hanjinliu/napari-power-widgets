import pytest
from magicgui import magicgui

import napari_power_widgets as NpW


@pytest.mark.parametrize(
    "widget_cls",
    [
        NpW.BoxSelector,
        NpW.ShapeComboBox,
        NpW.ColumnChoice,
        NpW.CoordinateSelector,
    ],
)
def test_magicgui_construction(widget_cls):
    @magicgui
    def f(x: widget_cls):
        return x
