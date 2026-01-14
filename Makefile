.PHONY: help venv install run test

help:
	@echo "Available targets:"
	@echo "  venv    - Create virtual environment (.venv)"
	@echo "  install - Install dependencies from requirements.txt"
	@echo "  run     - Run the calculator application"
	@echo "  test    - Run the test suite with pytest"

venv:
	python -m venv .venv

install:
	pip install -r requirements.txt

run:
	python src/app.py

test:
	pytest