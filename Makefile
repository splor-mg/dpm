.PHONY: coverage

coverage:
	python -m pytest -s --cov-config=.coveragerc --cov-report html --cov-branch --cov=dpm tests/