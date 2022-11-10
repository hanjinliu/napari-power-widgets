from typing import NewType, Tuple, List, Any, TYPE_CHECKING

import numpy as np
from magicgui import register_type

from . import _widgets as wdt

__all__ = [
    "BoxSelection",
    "FeatureColumn",
    "ShapeOf",
    "ShapesOf",
    "Coordinate",
    "ZStep",
    "ZRange",
]

if TYPE_CHECKING:
    import pandas as pd

    _Series = pd.Series
else:
    _Series = NewType("_Series", Any)

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


class ShapeOf:
    """Avaliable annotations for one of the layer's shapes."""

    __fields__ = ("Any", "Line", "Polygon", "Rectangle", "Ellipse", "Path")  # noqa

    Any = NewType("Any", np.ndarray)
    Line = NewType("Line", np.ndarray)
    Ellipse = NewType("Ellipse", np.ndarray)
    Rectangle = NewType("Rectangle", np.ndarray)
    Polygon = NewType("Polygon", np.ndarray)
    Path = NewType("Path", np.ndarray)


class ShapesOf(ShapeOf):
    """Avaliable annotations for some of the layer's shapes."""

    Any = NewType("Any", List[np.ndarray])
    Line = NewType("Line", List[np.ndarray])
    Ellipse = NewType("Ellipse", List[np.ndarray])
    Rectangle = NewType("Rectangle", List[np.ndarray])
    Polygon = NewType("Polygon", List[np.ndarray])
    Path = NewType("Path", List[np.ndarray])


_TEMPLATE = """
Alias of a list of numpy.ndarray for {name!r} shape data.

Examples
--------
>>> from napari_power_widgets.types import {type_name}
>>> from magicgui import magicgui
>>> # create a magicgui widget
>>> @magicgui
>>> def print_shape_coordinates(shape: {type_name}.{name}):
>>>     print(shape)
"""

for name in ShapeOf.__fields__:
    _type = getattr(ShapesOf, name)
    _type.__doc__ = _TEMPLATE.format(name=name, type_name=_type.__name__)

    _type = getattr(ShapesOf, name)
    _type.__doc__ = _TEMPLATE.format(name=name, type_name=_type.__name__)

register_type(ShapeOf.Any, widget_type=wdt.ShapeComboBox)
register_type(ShapeOf.Line, widget_type=wdt.ShapeComboBox, filter="line")  # noqa
register_type(ShapeOf.Ellipse, widget_type=wdt.ShapeComboBox, filter="ellipse")  # noqa
register_type(ShapeOf.Rectangle, widget_type=wdt.ShapeComboBox, filter="rectangle")  # noqa
register_type(ShapeOf.Polygon, widget_type=wdt.ShapeComboBox, filter="polygon")  # noqa
register_type(ShapeOf.Path, widget_type=wdt.ShapeComboBox, filter="path")  # noqa

register_type(ShapesOf.Any, widget_type=wdt.ShapeSelect)
register_type(ShapesOf.Line, widget_type=wdt.ShapeSelect, filter="line")  # noqa
register_type(ShapesOf.Ellipse, widget_type=wdt.ShapeSelect, filter="ellipse")  # noqa
register_type(ShapesOf.Rectangle, widget_type=wdt.ShapeSelect, filter="rectangle")  # noqa
register_type(ShapesOf.Polygon, widget_type=wdt.ShapeSelect, filter="polygon")  # noqa
register_type(ShapesOf.Path, widget_type=wdt.ShapeSelect, filter="path")  # noqa

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

del NewType, Tuple, List, Any, TYPE_CHECKING, np, register_type, wdt
