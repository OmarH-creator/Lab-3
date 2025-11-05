from __future__ import annotations

import pytest

from PyQt6 import QtCore

from src.ui.main_window import CalculatorWindow


@pytest.fixture
def calculator(qtbot):
    window = CalculatorWindow()
    qtbot.addWidget(window)
    window.show()
    qtbot.waitExposed(window)
    return window


def click_button(window: CalculatorWindow, qtbot, label: str) -> None:
    button = window.buttons[label]
    qtbot.mouseClick(button, QtCore.Qt.MouseButton.LeftButton)


def test_addition_flow(calculator: CalculatorWindow, qtbot) -> None:
    click_button(calculator, qtbot, "2")
    click_button(calculator, qtbot, "+")
    click_button(calculator, qtbot, "3")
    click_button(calculator, qtbot, "=")

    assert calculator.display.text() == "5"


def test_division_by_zero_shows_error(calculator: CalculatorWindow, qtbot) -> None:
    click_button(calculator, qtbot, "8")
    click_button(calculator, qtbot, "÷")
    click_button(calculator, qtbot, "0")
    click_button(calculator, qtbot, "=")

    assert calculator.display.text() == "Error"

    click_button(calculator, qtbot, "C")
    assert calculator.display.text() == "0"
