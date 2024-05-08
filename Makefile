.PHONY: coverage


coverage:
	python -m pytest -s --cov-config=.coveragerc --cov-report xml --cov-branch --cov=dpm tests/