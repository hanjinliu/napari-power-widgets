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
        NpW.LabelComboBox,
        NpW.LineDataEdit,
        NpW.PolygonDataEdit,
        NpW.RectangleDataEdit,
        NpW.PathDataEdit,
        NpW.EllipseDataEdit,
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
        (NpT.OneOfShapes, NpW.ShapeComboBox),
        (NpT.OneOfLines, NpW.ShapeComboBox),
        (NpT.OneOfRectangles, NpW.ShapeComboBox),
        (NpT.OneOfEllipses, NpW.ShapeComboBox),
        (NpT.OneOfPaths, NpW.ShapeComboBox),
        (NpT.OneOfPolygons, NpW.ShapeComboBox),
        (NpT.SomeOfShapes, NpW.ShapeSelect),
        (NpT.SomeOfLines, NpW.ShapeSelect),
        (NpT.SomeOfRectangles, NpW.ShapeSelect),
        (NpT.SomeOfEllipses, NpW.ShapeSelect),
        (NpT.SomeOfPaths, NpW.ShapeSelect),
        (NpT.SomeOfPolygons, NpW.ShapeSelect),
        (NpT.OneOfLabels, NpW.LabelComboBox),
        (NpT.FeatureColumn, NpW.ColumnChoice),
        (NpT.LineData, NpW.LineDataEdit),
        (NpT.PolygonData, NpW.PolygonDataEdit),
        (NpT.RectangleData, NpW.RectangleDataEdit),
        (NpT.PathData, NpW.PathDataEdit),
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
