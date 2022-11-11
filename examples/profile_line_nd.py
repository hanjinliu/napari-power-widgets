from matplotlib import pyplot as plt
import numpy as np
import napari
from napari_power_widgets.types import LineData
from napari.types import ImageData
from skimage.measure import profile_line


def profile_line_on_image(
    viewer: napari.Viewer, img: ImageData, line: LineData, linewidth: int = 1
):
    step = viewer.dims.current_step[:-2]
    prof = profile_line(img[step], line[0], line[1], linewidth=linewidth)
    plt.plot(prof)
    plt.show()


if __name__ == "__main__":
    viewer = napari.Viewer()
    arr = np.random.normal(size=(20, 100, 100))
    arr[5:16, 20:80, 20:80] += 10
    viewer.add_image(arr, name="image")
    viewer.window.add_function_widget(profile_line_on_image)
    napari.run()
