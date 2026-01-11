validate:
	ruff check .
	ruff format --check
	mypy . --check-untyped-defs
	codespell personal_compile_tools setup.py tests .ruff.toml README.md

test:
	pytest --cov=personal_compile_tools --cov-report term-missing
