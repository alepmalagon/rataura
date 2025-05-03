.PHONY: install test lint format clean docker-build docker-run

install:
	pip install -r requirements.txt
	pip install -e .

test:
	pytest

lint:
	flake8 eve_wiggin tests

format:
	black eve_wiggin tests
	isort eve_wiggin tests

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	find . -name __pycache__ -exec rm -rf {} +
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	find . -name "*.pyd" -delete
	find . -name ".coverage" -delete
	find . -name ".pytest_cache" -exec rm -rf {} +

docker-build:
	docker build -t eve_wiggin .

docker-run:
	docker run -it eve_wiggin

