from __future__ import annotations

from magicgui.widgets import Container, PushButton
from magicgui.widgets._bases import ValueWidget


class ButtonedValueWidget(Container):
    """Container that wraps a magic widget and provides a button."""

    def __init__(
        self,
        widget: ValueWidget,
        text: str = None,
        **kwargs,
    ):
        self._inner_value_widget = widget
        self._btn = PushButton(text=text)
        super().__init__(
            widgets=[self._inner_value_widget, self._btn],
            layout="horizontal",
            labels=False,
            **kwargs,
        )
        self.margins = (0, 0, 0, 0)

        # Emit the value
        self._inner_value_widget.changed.disconnect()
        self._inner_value_widget.changed.connect(
            lambda: self.changed.emit(self.value)
        )

        # Button clicked event
        self._btn.changed.disconnect()
        self._btn.changed.connect(self._on_button_clicked)

    def __repr__(self) -> str:
        """Return string representation."""
        return f"Buttoned{self._inner_value_widget!r}"

    @property
    def button(self) -> PushButton:
        """The button widget."""
        return self._btn

    @property
    def value(self):
        """Return range."""
        return self._inner_value_widget.value

    @value.setter
    def value(self, value):
        """Set value"""
        self._inner_value_widget.value = value

    def _on_button_clicked(self):
        pass
