# make up | data | run | rebuild-check | test | lint | check | audit | down   (make help lists all)
PYTHON ?= $(shell command -v python3.13 || command -v python3.12 || command -v python3)
VENV := .venv
PY := $(VENV)/bin/python
STAMP := $(VENV)/.installed
PKG := eval_set_builder

-include .env
export

$(STAMP): requirements-dev.lock pyproject.toml
	$(PYTHON) -m venv $(VENV)
	$(VENV)/bin/pip install -q --require-hashes -r requirements-dev.lock
	$(VENV)/bin/pip install -q --no-deps -e .
	touch $@

install: $(STAMP) ## create .venv from the hash-pinned lock file

env:
	@[ -f .env ] || { cp .env.example .env; echo "created .env from .env.example"; }

lint: $(STAMP) ## ruff check, ruff format check, mypy, import-linter
	$(VENV)/bin/ruff check .
	$(VENV)/bin/ruff format --check .
	$(VENV)/bin/mypy
	$(VENV)/bin/lint-imports

format: $(STAMP) ## apply ruff's formatting and safe fixes
	$(VENV)/bin/ruff check --fix .
	$(VENV)/bin/ruff format .

audit: $(STAMP) ## check the locked dependencies for known vulnerabilities
	$(VENV)/bin/pip-audit --no-deps --disable-pip -r requirements-dev.lock

lock: ## re-resolve requirements.lock and requirements-dev.lock with hashes (needs uv)
	uv pip compile pyproject.toml --universal --generate-hashes -q -o requirements.lock
	uv pip compile pyproject.toml --universal --extra dev --generate-hashes -q -o requirements-dev.lock

.PHONY: help install env up data run load scrub dedup sample label synthesize compare contamination freeze rebuild-check \
        record-synthetic cassette test test-live lint format audit check down clean

help: ## list the targets
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | sed -E 's/:.*## /\t/' | sort

EVAL := $(PY) -m eval_set_builder.interfaces.cli

up: env install ## prepare the environment: .env, .venv and the folders the stages write to
	mkdir -p work reports
	@echo "ready: run 'make run' to build the eval set from the committed raw traces"

data: install ## regenerate data/raw/traces.jsonl and answer_key.json from the seed (deterministic)
	$(EVAL) generate

run: install ## build eval-set/v1 from data/raw with the recorded model (offline) and print the manifest
	$(EVAL) run-all

load scrub dedup sample label synthesize compare contamination freeze: install ## run one stage (needs the stages before it)
	$(EVAL) $(subst sample,sample-and-guide,$@)

rebuild-check: install ## rebuild in a temp folder from the same traces and seed; the manifest must be identical
	$(EVAL) rebuild-check

cassette: install ## re-author the sample cassette of synthetic replies (offline, from templates)
	$(PY) scripts/author_synthetic_cassette.py

record-synthetic: install ## call the real model for every seed and write the cassette (needs ANTHROPIC_API_KEY)
	MODEL_ADAPTER=claude $(EVAL) record-synthetic

test: install ## offline tests with coverage; domain and application stay at 95% or more
	$(PY) -m pytest tests -m "not live" --cov=$(PKG) --cov-report=term
	$(PY) -m coverage report --include='src/$(PKG)/domain/*,src/$(PKG)/application/*' --fail-under=95

test-live: install ## the opt-in test that calls the real model (needs ANTHROPIC_API_KEY)
	RUN_LIVE=1 $(PY) -m pytest tests/live -m live

check: lint test ## everything that needs no key and no network

down: ## remove the work folder (intermediate files, including the raw scrub map)
	rm -rf work

clean: down
	rm -rf $(VENV) .pytest_cache .mypy_cache .ruff_cache .import_linter_cache .coverage coverage.xml
