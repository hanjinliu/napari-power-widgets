import pytest
from magicgui import magicgui

import napari_power_widgets as NpW
from napari_power_widgets import types as NpT


@pytest.mark.parametrize(
    "widget_cls",
    [
        NpW.BoxSelector,
        NpW.ShapeComboBox,
        NpW.ShapeSelect,
        NpW.ColumnChoice,
        NpW.CoordinateSelector,
        NpW.ZStepSpinBox,
        NpW.ZRangeEdit,
    ],
)
def test_magicgui_construction(widget_cls):
    @magicgui(x={"widget_type": widget_cls})
    def f(x):
        return x


@pytest.mark.parametrize(
    ["tp", "widget_cls"],
    [
        (NpT.BoxSelection, NpW.BoxSelector),
        (NpT.ShapeOf.Any, NpW.ShapeComboBox),
        (NpT.ShapeOf.Line, NpW.ShapeComboBox),
        (NpT.ShapeOf.Ellipse, NpW.ShapeComboBox),
        (NpT.ShapeOf.Path, NpW.ShapeComboBox),
        (NpT.ShapeOf.Polygon, NpW.ShapeComboBox),
        (NpT.ShapesOf.Any, NpW.ShapeSelect),
        (NpT.ShapesOf.Line, NpW.ShapeSelect),
        (NpT.ShapesOf.Ellipse, NpW.ShapeSelect),
        (NpT.ShapesOf.Path, NpW.ShapeSelect),
        (NpT.ShapesOf.Polygon, NpW.ShapeSelect),
        (NpT.FeatureColumn, NpW.ColumnChoice),
        (NpT.ZStep, NpW.ZStepSpinBox),
        (NpT.ZRange, NpW.ZRangeEdit),
        (NpT.Coordinate, NpW.CoordinateSelector),
    ],
)
def test_magicgui_construction_with_type(tp, widget_cls):
    @magicgui
    def f(x: tp):
        return x

    assert type(f.x) is widget_cls
