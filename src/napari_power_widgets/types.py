from typing import NewType, Tuple

from magicgui import register_type

from ._widgets import BoxSelector, BoxSliceSelector

__all__ = ["BoxSelection", "BoxSlices"]


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
register_type(BoxSelection, widget_type=BoxSelector)


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
register_type(BoxSlices, widget_type=BoxSliceSelector)
