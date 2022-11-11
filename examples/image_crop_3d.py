import numpy as np
import napari
from napari_power_widgets.types import BoxSelection, ZRange
from napari.layers import Image


def crop_3d(img: Image, xy: BoxSelection, z: ZRange) -> Image:
    if img.ndim != 3:
        raise ValueError("Input image must be 3D.")
    arr = img.data
    (ystart, ystop), (xstart, xstop) = xy
    *_, y0, x0 = np.ceil(img.world_to_data([ystart, xstart])).astype(int)
    *_, y1, x1 = np.floor(img.world_to_data([ystop, xstop])).astype(int)
    z0, z1 = z
    z1 += 1  # ZRange is inclusive
    print(f"img[{z0}:{z1}, {y0}:{y1}, {x0}:{x1}]")
    arr_cropped = arr[z0:z1, y0:y1, x0:x1]
    return Image(arr_cropped, name=f"{img.name}-cropped")


if __name__ == "__main__":
    viewer = napari.Viewer()
    arr = np.random.normal(size=(20, 100, 100))
    arr[5:16, 20:80, 20:80] += 10
    viewer.add_image(arr, name="image")
    viewer.window.add_function_widget(crop_3d)
    napari.run()
