.PHONY: install api seed tick worker test test-js check docker

install:
	python -m pip install -e .[api]

api:
	python -m pulsecse api

seed:
	python -m pulsecse seed

tick:
	python -m pulsecse tick

worker:
	python -m pulsecse worker --interval 60

test:
	PYTHONPATH=backend python -m unittest discover -s backend/tests

test-js:
	npm test

check:
	PYTHONPATH=backend python -m compileall -q backend && npm run check && npm test && PYTHONPATH=backend python -m unittest discover -s backend/tests

docker:
	docker compose up --build
