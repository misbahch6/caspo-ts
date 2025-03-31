# Development

To set up your environment for development, follow these steps. This
configuration ensures that all necessary dependencies are installed and code
quality tools are properly set up.

```sh
conda create -n caspots-test -c potassco -c bioasp -c colomoto caspo nusmv clingo pip
conda activate caspots-test
pip install -e .[dev]
pre-commit install
```

This setup provides a reproducible environment with essential tools and
dependencies, while pre-commit hooks help enforce coding standards before
committing changes to the repository.

The `pip install -e .[dev]` command installs the project in editable mode,
allowing you to modify the codebase and test changes seamlessly, while also
installing additional development dependencies.

## Testing

Before running tests, ensure that you have activated the caspots-test
environment using `conda activate caspots-test`. This ensures that all
necessary dependencies are available. We provide a Makefile to simplify running
tests, type checking, and linting. You can use the following commands:

```sh
make all
make test
make typecheck
make lint
```
