.PHONY: fixcode
fixcode: fixcode
	autopep8 --in-place --aggressive --aggressive --recursive ../app 

.PHONY: lint
lint: lint
	pylint ../app 

.PHONY: test
test: test
	export ENV_FILE=environment.test \
	python -m pytest tests/unit --capture=sys -vv

.PHONY: test-integration
test-integration: test-integration
	ENV_FILE=environment.test \
	python -m pytest tests/integration --capture=sys -vv