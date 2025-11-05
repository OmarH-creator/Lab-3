"""Keyboard mapping helpers for the calculator UI."""
from __future__ import annotations

from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeyEvent

# Mapping for keys that do not provide a helpful text representation.
_SPECIAL_KEY_MAP = {
    Qt.Key.Key_Return: "=",
    Qt.Key.Key_Enter: "=",
    Qt.Key.Key_Equal: "=",
    Qt.Key.Key_Backspace: "⌫",
    Qt.Key.Key_Escape: "C",
    Qt.Key.Key_Delete: "CE",
    Qt.Key.Key_Percent: "%",
    Qt.Key.Key_Plus: "+",
    Qt.Key.Key_Minus: "−",
    Qt.Key.Key_Slash: "÷",
    Qt.Key.Key_Asterisk: "×",
    Qt.Key.Key_Period: ".",
    Qt.Key.Key_Comma: ".",
}

_TEXT_KEY_MAP = {
    "+": "+",
    "-": "−",
    "×": "×",
    "*": "×",
    "x": "×",
    "X": "×",
    "÷": "÷",
    "/": "÷",
    "=": "=",
}


def key_to_button_text(event: QKeyEvent) -> Optional[str]:
    """Translate a ``QKeyEvent`` into a calculator button label."""

    key = event.key()
    if key in _SPECIAL_KEY_MAP:
        return _SPECIAL_KEY_MAP[key]

    text = event.text()
    if not text:
        return None

    if text.isdigit():
        return text

    if text == ".":
        return "."
    if text == ",":
        return "."

    mapped = _TEXT_KEY_MAP.get(text)
    if mapped:
        return mapped

    if text.lower() == "c":
        return "C"
    if text.lower() == "p":  # support Shift+5 alternative if needed
        return "%"

    return None
