from __future__ import annotations

from typing import TYPE_CHECKING
from magicgui.widgets import Container, ComboBox, Label, Widget
from magicgui.widgets._bases.value_widget import UNSET

from ._utils import find_viewer_ancestor, minimize_label_width

if TYPE_CHECKING:
    import pandas as pd


def get_features(widget: Widget) -> list[tuple[str, pd.DataFrame]]:
    """Get all the non-empty feature data from the viewer."""
    viewer = find_viewer_ancestor(widget)
    if viewer is None:
        return []
    features: list[pd.DataFrame] = []
    for layer in viewer.layers:
        if len(feat := getattr(layer, "features", [])) > 0:
            features.append((layer.name, feat))
    return features


class ColumnChoice(Container):
    def __init__(
        self,
        value=UNSET,
        nullable=False,
        **kwargs,
    ):
        self._dataframe_cbox = ComboBox(choices=get_features, value=value)
        self._column_cbox = ComboBox(choices=self._get_available_columns)
        _label_l = Label(value='.features["')
        minimize_label_width(_label_l)
        _label_r = Label(value='"]')
        minimize_label_width(_label_r)

        super().__init__(
            layout="horizontal",
            widgets=[
                self._dataframe_cbox,
                _label_l,
                self._column_cbox,
                _label_r,
            ],
            labels=False,
            name=kwargs.pop("name", None),
            **kwargs,
        )
        self.margins = (0, 0, 0, 0)
        self._dataframe_cbox.changed.connect(self._set_available_columns)

    def _get_available_columns(self, w: Widget = None):
        df: pd.DataFrame = self._dataframe_cbox.value
        cols = getattr(df, "columns", [])
        return cols

    def _set_available_columns(self, w: Widget = None):
        cols = self._get_available_columns()
        self._column_cbox.choices = cols
        return None

    @property
    def value(self) -> pd.Series:
        df = self._dataframe_cbox.value
        return df[self._column_cbox.value]
