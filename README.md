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
