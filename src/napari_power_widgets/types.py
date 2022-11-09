from typing import NewType, Tuple, Any, TYPE_CHECKING

import numpy as np
from magicgui import register_type

from . import _widgets as wdt

__all__ = ["BoxSelection", "BoxSlices", "ShapeType"]

if TYPE_CHECKING:
    import pandas as pd

    _DataFrame = pd.DataFrame
    _Series = pd.Series
else:
    _DataFrame = NewType("_DataFrame", Any)
    _Series = NewType("_Series", Any)

BoxSelection = NewType(
    "BoxSelection", Tuple[Tuple[float, float], Tuple[float, float]]
)
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


BoxSlices = NewType("BoxSlices", Tuple[slice, slice])
BoxSlices.__doc__ = """
Alias of (slice, slice) for the 2D box selection in a napari viewer.

Unlike `BoxSelection`, this type can directly used for image slicing.

Examples
--------
>>> from napari_power_widgets.types import BoxSlices
>>> from napari.layers import Image
>>> from magicgui import magicgui
>>> # create a magicgui widget
>>> @magicgui
>>> def crop_image(image: Image, sl: BoxSlices) -> Image:
>>>     arr = image.data
>>>     return Image(arr[sl])
"""
register_type(BoxSlices, widget_type=wdt.BoxSliceSelector)

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


class ShapeType:
    """Avaliable annotations for one of the layer's shape types."""

    __fields__ = (
        "ANY",
        "LINE",
        "POLYGON",
        "RECTANGLE",
        "ELLIPSE",
        "PATH",
    )

    ANY = NewType("ANY", np.ndarray)
    LINE = NewType("LINE", np.ndarray)
    ELLIPSE = NewType("ELLIPSE", np.ndarray)
    RECTANGLE = NewType("RECTANGLE", np.ndarray)
    POLYGON = NewType("POLYGON", np.ndarray)
    PATH = NewType("PATH", np.ndarray)


for name in ShapeType.__fields__:
    _type = getattr(ShapeType, name)
    _type.__doc__ = f"""
    Alias of numpy.ndarray for a {name.title()!r} shape data.

    Examples
    --------
    >>> from napari_power_widgets.types import ShapeType
    >>> from magicgui import magicgui
    >>> # create a magicgui widget
    >>> @magicgui
    >>> def print_shape_coordinates(shape: ShapeType.{name}):
    >>>     print(shape)
    """

register_type(ShapeType.ANY, widget_type=wdt.ShapeComboBox)
register_type(ShapeType.LINE, widget_type=wdt.LineShapeComboBox)
register_type(ShapeType.ELLIPSE, widget_type=wdt.EllipseShapeComboBox)
register_type(ShapeType.RECTANGLE, widget_type=wdt.RectangleShapeComboBox)
register_type(ShapeType.POLYGON, widget_type=wdt.PolygonShapeComboBox)
register_type(ShapeType.PATH, widget_type=wdt.PathShapeComboBox)

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
