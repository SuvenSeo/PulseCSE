PYTHONPATH=backend

.PHONY: help install dev test check migrate seed api tick poller docker-up docker-down

help:
	@echo "PulseCSE commands: install dev test check migrate seed api tick poller docker-up docker-down"

install:
	pip install -e ".[prod]"

dev:
	pip install -e ".[prod,dev]"
	touch data/.keep || true

test:
	npm run fullcheck

check:
	npm run fullcheck

migrate:
	PYTHONPATH=backend python -m pulsecse migrate

seed:
	PYTHONPATH=backend python -m pulsecse seed

api:
	PYTHONPATH=backend python -m pulsecse api

tick:
	PYTHONPATH=backend python -m pulsecse tick --force

poller:
	PYTHONPATH=backend python -m pulsecse poller --force

docker-up:
	docker compose up --build

docker-down:
	docker compose down
