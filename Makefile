all: test typecheck lint

lint:
	pylint caspots tests

typecheck:
	mypy --strict -p caspots -p tests

test:
	coverage run -m pytest
	coverage report -m --fail-under=15

.PHONY: all lint typecheck test
.NOTPARALLEL:
