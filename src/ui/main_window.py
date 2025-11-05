from __future__ import annotations

from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Dict, List

from PyQt6 import QtCore, QtGui, QtWidgets

from src.core.evaluator import EvaluationError, ExpressionEvaluator
from src.core.keypad import key_to_button_text


class CalculatorWindow(QtWidgets.QMainWindow):
    """Main window for the neumorphic calculator application."""

    _OPERATOR_MAP = {"+": "+", "−": "-", "×": "*", "÷": "/"}
    _DISPLAY_OPERATOR = {"+": "+", "-": "−", "*": "×", "/": "÷"}

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Neumorphic Calculator")
        self.setMinimumSize(360, 520)
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)

        self._evaluator = ExpressionEvaluator()
        self._expression_tokens: List[str] = []
        self._current_input: str = ""
        self._last_output: str = "0"
        self._last_value: Decimal = Decimal("0")
        self._just_evaluated: bool = False
        self._error_state: bool = False

        self._load_styles()
        self._build_ui()
        self._update_display()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------
    def _load_styles(self) -> None:
        style_path = Path(__file__).with_name("styles.qss")
        if style_path.exists():
            self.setStyleSheet(style_path.read_text(encoding="utf-8"))

    def _build_ui(self) -> None:
        central = QtWidgets.QWidget()
        central.setObjectName("CentralWidget")
        central_layout = QtWidgets.QVBoxLayout(central)
        central_layout.setContentsMargins(24, 30, 24, 24)
        central_layout.setSpacing(20)
        self.setCentralWidget(central)
        central.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
        central.setFocus()

        self.display = QtWidgets.QLineEdit("0")
        self.display.setObjectName("Display")
        self.display.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.display.setReadOnly(True)
        self.display.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        self.display.setMinimumHeight(80)
        self.display.setClearButtonEnabled(False)
        font = QtGui.QFont("Inter", 28)
        font.setStyleStrategy(QtGui.QFont.StyleStrategy.PreferAntialias)
        self.display.setFont(font)
        self._apply_shadow(self.display, blur=35, dx=-4, dy=-4, alpha=120)
        central_layout.addWidget(self.display)

        button_layout = QtWidgets.QGridLayout()
        button_layout.setSpacing(16)
        central_layout.addLayout(button_layout)

        buttons = [
            ["C", "CE", "±", "⌫"],
            ["7", "8", "9", "÷"],
            ["4", "5", "6", "×"],
            ["1", "2", "3", "−"],
            ["0", ".", "%", "+"],
        ]

        self.buttons: Dict[str, QtWidgets.QPushButton] = {}
        for row, row_values in enumerate(buttons):
            for col, label in enumerate(row_values):
                button = self._create_button(label)
                button_layout.addWidget(button, row, col)
                self.buttons[label] = button

        equals_button = self._create_button("=")
        equals_button.setObjectName("EqualsButton")
        equals_button.setMinimumHeight(70)
        button_layout.addWidget(equals_button, 5, 0, 1, 4)
        self.buttons["="] = equals_button

        self.setTabOrder(self.display, self.buttons["C"])

    def _create_button(self, label: str) -> QtWidgets.QPushButton:
        button = QtWidgets.QPushButton(label)
        button.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        button.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        button.clicked.connect(lambda checked=False, text=label: self._handle_button(text))
        self._apply_shadow(button)
        return button

    @staticmethod
    def _apply_shadow(
        widget: QtWidgets.QWidget,
        *,
        blur: float = 30,
        dx: float = 4,
        dy: float = 4,
        alpha: int = 160,
    ) -> None:
        effect = QtWidgets.QGraphicsDropShadowEffect(widget)
        effect.setBlurRadius(blur)
        effect.setXOffset(dx)
        effect.setYOffset(dy)
        effect.setColor(QtGui.QColor(163, 177, 198, alpha))
        widget.setGraphicsEffect(effect)

    # ------------------------------------------------------------------
    # Event handling
    # ------------------------------------------------------------------
    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:  # noqa: N802
        mapped = key_to_button_text(event)
        if mapped:
            self._handle_button(mapped)
            event.accept()
        else:
            super().keyPressEvent(event)

    def _handle_button(self, label: str) -> None:
        if label.isdigit():
            self._append_digit(label)
            return
        if label == ".":
            self._append_decimal()
            return
        if label in {"+", "−", "×", "÷"}:
            self._apply_operator(label)
            return
        if label == "=":
            self._calculate_result()
            return
        if label == "C":
            self._clear_all()
            return
        if label == "CE":
            self._clear_entry()
            return
        if label == "⌫":
            self._backspace()
            return
        if label == "±":
            self._toggle_sign()
            return
        if label == "%":
            self._apply_percent()
            return

    # ------------------------------------------------------------------
    # Calculator behaviour
    # ------------------------------------------------------------------
    def _append_digit(self, digit: str) -> None:
        if self._error_state:
            self._clear_all()
        if self._just_evaluated:
            self._expression_tokens.clear()
            self._current_input = ""
            self._just_evaluated = False
        if self._current_input in {"0", "-0"}:
            if digit == "0":
                self._update_display()
                return
            if self._current_input.startswith("-"):
                self._current_input = f"-{digit}"
            else:
                self._current_input = digit
        else:
            self._current_input += digit
        if not self._current_input:
            self._current_input = digit
        self._last_output = self._current_input
        self._update_display()

    def _append_decimal(self) -> None:
        if self._error_state:
            self._clear_all()
        if self._just_evaluated:
            self._expression_tokens.clear()
            self._current_input = ""
            self._just_evaluated = False
        target = self._current_input or "0"
        if "." in target:
            self._update_display()
            return
        if target == "-0":
            self._current_input = "-0."
        elif target.startswith("-") and target != "-0":
            self._current_input = f"{target}."
        else:
            self._current_input = f"{target}."
        self._last_output = self._current_input
        self._update_display()

    def _apply_operator(self, symbol: str) -> None:
        if self._error_state:
            self._clear_all()
            return
        operator = self._OPERATOR_MAP[symbol]

        if self._just_evaluated:
            self._expression_tokens.clear()
            self._just_evaluated = False
        if self._current_input:
            self._push_current_to_tokens()
        if not self._expression_tokens:
            self._expression_tokens.append(self._decimal_to_string(self._last_value))
        if self._expression_tokens and self._expression_tokens[-1] in self._OPERATOR_MAP.values():
            self._expression_tokens[-1] = operator
        else:
            self._expression_tokens.append(operator)
        self._update_display()

    def _calculate_result(self) -> None:
        if self._error_state:
            self._clear_all()
            return
        if self._current_input:
            self._push_current_to_tokens()
        elif self._expression_tokens and self._expression_tokens[-1] in self._OPERATOR_MAP.values():
            self._expression_tokens.pop()
        expression = "".join(self._expression_tokens)
        if not expression:
            self._update_display()
            return
        try:
            result = self._evaluator.evaluate(expression)
        except (EvaluationError, ZeroDivisionError):
            self._show_error()
            return
        self._last_value = result
        self._current_input = ExpressionEvaluator.format_decimal(result)
        self._last_output = self._current_input
        self._expression_tokens.clear()
        self._just_evaluated = True
        self._update_display()

    def _clear_all(self) -> None:
        self._expression_tokens = []
        self._current_input = ""
        self._last_output = "0"
        self._last_value = Decimal("0")
        self._just_evaluated = False
        self._error_state = False
        self._update_display()

    def _clear_entry(self) -> None:
        if self._error_state:
            self._clear_all()
            return
        self._current_input = ""
        self._last_output = "0"
        self._just_evaluated = False
        self._update_display()

    def _backspace(self) -> None:
        if self._error_state:
            self._clear_all()
            return
        if not self._current_input:
            self._update_display()
            return
        self._current_input = self._current_input[:-1]
        if self._current_input in {"", "-"}:
            self._current_input = ""
        self._last_output = self._current_input or "0"
        self._just_evaluated = False
        self._update_display()

    def _toggle_sign(self) -> None:
        if self._error_state:
            self._clear_all()
            return
        if not self._current_input:
            if self._just_evaluated:
                self._current_input = self._last_output
            else:
                self._current_input = "0"
        if self._current_input.startswith("-"):
            self._current_input = self._current_input[1:]
        else:
            self._current_input = f"-{self._current_input}"
        if self._current_input == "-0":
            self._current_input = "-0"
        self._last_output = self._current_input
        self._just_evaluated = False
        self._update_display()

    def _apply_percent(self) -> None:
        if self._error_state:
            self._clear_all()
            return
        target_source = "current" if self._current_input else "tokens"
        try:
            if target_source == "current":
                value = Decimal(self._current_input or "0") / Decimal("100")
                self._current_input = self._decimal_to_string(value)
            else:
                index = self._find_last_number_index()
                if index is None:
                    self._current_input = "0"
                    value = Decimal("0")
                else:
                    value = Decimal(self._expression_tokens[index]) / Decimal("100")
                    self._expression_tokens[index] = self._decimal_to_string(value)
                    self._current_input = self._expression_tokens[index]
        except (InvalidOperation, EvaluationError):
            self._show_error()
            return
        self._last_value = value
        self._last_output = ExpressionEvaluator.format_decimal(value)
        self._just_evaluated = False
        self._update_display()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _push_current_to_tokens(self) -> bool:
        if not self._current_input or self._current_input == "-":
            return False
        try:
            value = Decimal(self._current_input)
        except InvalidOperation:
            self._show_error()
            return False
        canonical = self._decimal_to_string(value)
        self._expression_tokens.append(canonical)
        self._last_value = value
        self._last_output = ExpressionEvaluator.format_decimal(value)
        self._current_input = ""
        return True

    def _find_last_number_index(self) -> int | None:
        for index in range(len(self._expression_tokens) - 1, -1, -1):
            if self._expression_tokens[index] not in self._OPERATOR_MAP.values():
                return index
        return None

    def _decimal_to_string(self, value: Decimal) -> str:
        text = format(value.normalize(), "f")
        if "." in text:
            text = text.rstrip("0").rstrip(".")
        if text in {"", "-0", "-0.0"}:
            return "0"
        if text == "-":
            return "0"
        return text

    def _canonical_to_display(self, value: str) -> str:
        try:
            decimal_value = Decimal(value)
        except InvalidOperation:
            return value
        return ExpressionEvaluator.format_decimal(decimal_value)

    def _update_display(self) -> None:
        if self._error_state:
            self.display.setText("Error")
            return
        if self._current_input:
            text = self._current_input
        elif self._expression_tokens:
            last = self._expression_tokens[-1]
            if last in self._OPERATOR_MAP.values():
                text = self._last_output
            else:
                text = self._canonical_to_display(last)
        else:
            text = self._last_output
        if text in {"-0", "-0."}:
            text = text.replace("-", "")
        if text in {"", "-"}:
            text = "0"
        self.display.setText(text)

    def _show_error(self) -> None:
        self._expression_tokens.clear()
        self._current_input = ""
        self._last_output = "Error"
        self._error_state = True
        self._just_evaluated = False
        self.display.setText("Error")
