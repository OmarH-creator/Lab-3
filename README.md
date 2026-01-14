# Neumorphic Calculator

A desktop calculator application built with Python and PyQt6 featuring a soft
neumorphism-inspired user interface and a robust calculation engine. The
application offers mouse and keyboard input, standard calculator operations,
and comprehensive automated tests.

## Requirements

- Python 3.9+

## Getting started

It is recommended to work inside a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

## Running the app

Launch the calculator window with:

```bash
python src/app.py
```

## Running tests

Execute the full automated test suite using `pytest`:

```bash
pytest
```

The tests cover the calculation engine with many arithmetic scenarios and
include a smoke test of the GUI using `pytest-qt`.

## IntelliJ IDEA / PyCharm Setup

This project includes pre-configured run configurations for IntelliJ IDEA (with Python plugin) and PyCharm:

1. Open the project folder in IntelliJ IDEA or PyCharm
2. Enable the Python plugin if needed (usually enabled by default in PyCharm)
3. Set the Project Interpreter to `.venv` or a system Python 3.9+:
   - Go to File → Settings → Project → Python Interpreter
   - Click the gear icon → Add Interpreter
   - Select "Existing environment" and choose your virtual environment or system Python
4. Use the pre-defined Run Configurations from the Run/Debug dropdown:
   - **Run Calculator**: Launches the desktop calculator application
   - **Pytest**: Runs the automated test suite

Alternatively, you can use the Makefile targets:

```bash
make venv      # Create virtual environment
make install   # Install dependencies
make run       # Run the calculator
make test      # Run tests
```
