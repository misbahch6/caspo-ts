all: test typecheck lint

lint:
	# TODO: remove --fail-under once all issues are addressed
	pylint --fail-under=7 caspots tests

typecheck:
	# TODO: remove || true once all issues are addressed
	mypy --strict -p caspots -p tests || true

test:
	coverage run -m pytest
	# TODO: remove --fail-under once all issues are addressed
	coverage report -m --fail-under=15

.PHONY: all lint typecheck test
.NOTPARALLEL:
