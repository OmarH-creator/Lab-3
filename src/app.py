from __future__ import annotations

import sys

from PyQt6.QtWidgets import QApplication

from src.ui.main_window import CalculatorWindow


def main() -> int:
    app = QApplication(sys.argv)
    window = CalculatorWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
