from typing import NewType, Tuple, List, Any, TYPE_CHECKING

import numpy as np
from magicgui import register_type

from . import _widgets as wdt

if TYPE_CHECKING:
    import pandas as pd

    _Series = pd.Series
else:
    _Series = Any

# fmt: off
BoxSelection = NewType("BoxSelection", Tuple[Tuple[float, float], Tuple[float, float]])  # noqa
BoxSelection.__doc__ = """
Alias of ((float, float), (float, float)) for a box selection.

Examples
--------
>>> from napari_power_widgets.types import BoxSelection
>>> from napari.layers import Image
>>> from magicgui import magicgui
>>> # create a magicgui widget
>>> @magicgui
>>> def crop_image(image: Image, selection: BoxSelection) -> Image:
>>>     arr = image.data
>>>     (y0, y1), (x0, x1) = selection
>>>     arr_cropped = arr[int(y0):int(y1), int(x0):int(x1)]
>>>     return Image(arr_croped)
"""
register_type(BoxSelection, widget_type=wdt.BoxSelector)


# BoxSlices = NewType("BoxSlices", Tuple[slice, slice])
# BoxSlices.__doc__ = """
# Alias of (slice, slice) for the 2D box selection in a napari viewer.

# Unlike `BoxSelection`, this type can directly used for image slicing.

# Examples
# --------
# >>> from napari_power_widgets.types import BoxSlices
# >>> from napari.layers import Image
# >>> from magicgui import magicgui
# >>> # create a magicgui widget
# >>> @magicgui
# >>> def crop_image(image: Image, sl: BoxSlices) -> Image:
# >>>     arr = image.data
# >>>     return Image(arr[sl])
# """
# register_type(BoxSlices, widget_type=wdt.BoxSliceSelector)

FeatureColumn = NewType("FeatureColumn", _Series)
FeatureColumn.__doc__ = """
Alias of pandas.Series for a feature column.

Annotated argument will be one of the columns that can be found in any
of the layers that have a `features` attribute.

Examples
--------
>>> from napari_power_widgets.types import FeatureColumn
>>> import matplotlib.pyplot as plt
>>> from magicgui import magicgui
>>>
>>> @magicgui
>>> def plot_feature(column: FeatureColumn):
>>>     plt.plot(column)
>>>     plt.show()
"""

register_type(FeatureColumn, widget_type=wdt.ColumnChoice)


OneOfShapes = NewType("OneOfShapes", np.ndarray)
OneOfLines = NewType("OneOfLines", np.ndarray)
OneOfEllipses = NewType("OneOfEllipses", np.ndarray)
OneOfRectangles = NewType("OneOfRectangles", np.ndarray)
OneOfPolygons = NewType("OneOfPolygons", np.ndarray)
OneOfPaths = NewType("OneOfPaths", np.ndarray)

_OneOfs = [OneOfShapes, OneOfLines, OneOfEllipses, OneOfRectangles, OneOfPolygons, OneOfPaths]  # noqa

SomeOfShapes = NewType("SomeOfShapes", List[np.ndarray])
SomeOfLines = NewType("SomeOfLines", List[np.ndarray])
SomeOfEllipses = NewType("SomeOfEllipses", List[np.ndarray])
SomeOfRectangles = NewType("SomeOfRectangles", List[np.ndarray])
SomeOfPolygons = NewType("SomeOfPolygons", List[np.ndarray])
SomeOfPaths = NewType("SomeOfPaths", List[np.ndarray])

_SomeOfs = [SomeOfShapes, SomeOfLines, SomeOfEllipses, SomeOfRectangles, SomeOfPolygons, SomeOfPaths]  # noqa

_TEMPLATE_ONEOF = """
Alias of a list of numpy.ndarray for shape data.

Examples
--------
>>> from napari_power_widgets.types import {type_name}
>>> from magicgui import magicgui
>>> # create a magicgui widget
>>> @magicgui
>>> def print_shape_coordinates(shape: {type_name}):
>>>     print(shape)
"""

_TEMPLATE_SOMEOF = """
Alias of a list of numpy.ndarray for a set of shape data.

Examples
--------
>>> from napari_power_widgets.types import {type_name}
>>> from magicgui import magicgui
>>> # create a magicgui widget
>>> @magicgui
>>> def print_shape_coordinates(shape: {type_name}):
>>>     print(shape)
"""

for _type in _OneOfs:
    _type.__doc__ = _TEMPLATE_ONEOF.format(type_name=_type.__name__)
for _type in _SomeOfs:
    _type.__doc__ = _TEMPLATE_SOMEOF.format(type_name=_type.__name__)

register_type(OneOfShapes, widget_type=wdt.ShapeComboBox)
register_type(OneOfLines, widget_type=wdt.ShapeComboBox, filter="line")  # noqa
register_type(OneOfEllipses, widget_type=wdt.ShapeComboBox, filter="ellipse")  # noqa
register_type(OneOfRectangles, widget_type=wdt.ShapeComboBox, filter="rectangle")  # noqa
register_type(OneOfPolygons, widget_type=wdt.ShapeComboBox, filter="polygon")  # noqa
register_type(OneOfPaths, widget_type=wdt.ShapeComboBox, filter="path")  # noqa

register_type(SomeOfShapes, widget_type=wdt.ShapeSelect)
register_type(SomeOfLines, widget_type=wdt.ShapeSelect, filter="line")  # noqa
register_type(SomeOfEllipses, widget_type=wdt.ShapeSelect, filter="ellipse")  # noqa
register_type(SomeOfRectangles, widget_type=wdt.ShapeSelect, filter="rectangle")  # noqa
register_type(SomeOfPolygons, widget_type=wdt.ShapeSelect, filter="polygon")  # noqa
register_type(SomeOfPaths, widget_type=wdt.ShapeSelect, filter="path")  # noqa

Coordinate = NewType("Coordinate", np.ndarray)
Coordinate.__doc__ = """
Alias of numpy.ndarray of shape (2,) for a physical point coordinate.

Examples
--------
>>> from napari_power_widgets.types import Coordinate
>>> from magicgui import magicgui
>>>
>>> @magicgui
>>> def measure_distance(pos0: Coordinate, pos1: Coordinate):
>>>     return np.sqrt(np.sum((pos0 - pos1)**2))
"""

register_type(Coordinate, widget_type=wdt.CoordinateSelector)

ZStep = NewType("ZStep", int)
ZStep.__doc__ = """
Alias of int for z-step of the viewer.

Examples
--------
>>> from napari_power_widgets.types import ZStep
>>> from napari.layers import Image
>>> from magicgui import magicgui
>>>
>>> @magicgui
>>> def get_slice(img: Image, z: ZStep) -> Image:
>>>     return Image(img.data[z], name=f"{img.name} (z={z})")
"""
register_type(ZStep, widget_type=wdt.ZStepSpinBox)

ZRange = NewType("ZRange", Tuple[int, int])
ZRange.__doc__ = """
Alias of (int, int) for an **inclusive** range of z-step.

By default, the first value is smaller than the second value. If you
want to disable the order check, use `ordered=False` in magicgui
configuration for this parameter.

Examples
--------
>>> from napari_power_widgets.types import ZRange
>>> from napari.layers import Image
>>> from magicgui import magicgui
>>>
>>> @magicgui
>>> def get_clipped(img: Image, zrange: ZRange) -> Image:
>>>     zmin, zmax = zrange
>>>     return Image(img.data[zmin:zmax+1])
"""
register_type(ZRange, widget_type=wdt.ZRangeEdit)

LineData = NewType("LineData", np.ndarray)
RectangleData = NewType("RectangleData", np.ndarray)
PathData = NewType("PathData", np.ndarray)
PolygonData = NewType("PolygonData", np.ndarray)

register_type(LineData, widget_type=wdt.LineDataEdit)
register_type(RectangleData, widget_type=wdt.RectangleDataEdit)
register_type(PathData, widget_type=wdt.PathDataEdit)
register_type(PolygonData, widget_type=wdt.PolygonDataEdit)

# delete all the variables that are not needed
del NewType, Tuple, List, Any, TYPE_CHECKING, np, register_type, wdt
