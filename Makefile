install:
	pip install -e '.[dev]'

run:
	uvicorn api.main:app --reload

test:
	pytest -q

lint:
	ruff check .

format:
	ruff format .
