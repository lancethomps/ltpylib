init:
	pip install pipenv --upgrade
	pipenv install --dev

format-python:
	pipenv run yapf --in-place --parallel --recursive --verbose ltpylib ltpylibtests setup.py

coverage:
	pipenv run pytest --verbose --cov=ltpylib --cov-report=xml --junit-xml=report.xml

lint-flake8:
	pipenv run flake8

lint-python-style:
	# Fail if yapf formatter needs to reformat code
	pipenv run yapf --diff --recursive ltpylib ltpylibtests setup.py

lint: lint-flake8 lint-python-style

test:
	pipenv run pytest --cov=ltpylib

tests:
	pipenv run tox

ci: lint
	pipenv run pytest -n 8 --boxed --cov=ltpylib --cov-report=xml --junit-xml=report.xml
