# Convenience targets. Everything here is a one-line command you could type by hand; the Makefile
# exists so the same command is used locally and in CI, and nobody has to remember the flags.

.PHONY: help setup test lint format check-notebooks build-modules self-test clean

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

setup:  ## Create a virtual environment and install everything
	python -m venv .venv
	. .venv/bin/activate && pip install --upgrade pip && pip install -e ".[dev,notebook]"

test:  ## Run the test suite
	pytest

test-cov:  ## Run the tests with a coverage report
	pytest --cov=dpm --cov-report=term-missing

lint:  ## Lint the hand-written code
	ruff check .

format:  ## Apply formatting fixes
	ruff check --fix .
	ruff format .

build-modules:  ## Regenerate src/dpm/*.py from the notebooks
	python tools/nb_to_module.py

check-notebooks:  ## Fail if a module has drifted from its notebook
	python tools/nb_to_module.py --check

self-test:  ## Run every pipeline on synthetic data
	dpm self-test

clean:  ## Remove build and test artefacts
	rm -rf .pytest_cache .ruff_cache **/__pycache__ src/*.egg-info .coverage htmlcov
	find . -type d -name '.ipynb_checkpoints' -prune -exec rm -rf {} +
