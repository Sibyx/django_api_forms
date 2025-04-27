# Contributing to Django API Forms

Thank you for your interest in contributing to Django API Forms! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

By participating in this project, you are expected to uphold our Code of Conduct, which is to be respectful and considerate of others.

## Getting Started

### Prerequisites

- Python 3.9+
- Django 2.0+
- Poetry (for dependency management)

### Setting Up the Development Environment

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```shell
   git clone https://github.com/YOUR-USERNAME/django_api_forms.git
   cd django_api_forms
   ```
3. Install dependencies using Poetry:
   ```shell
   poetry install
   ```

## Development Workflow

### Running Tests

We use Django's test framework for testing. To run the tests:

```shell
poetry run python runtests.py
```

To run tests with coverage:

```shell
poetry run coverage run runtests.py
poetry run coverage report
```

### Code Style

We follow PEP 8 style guidelines. We use flake8 for code style checking:

```shell
poetry run flake8 .
```

### Documentation

We use mkdocs-material for documentation. To build and serve the documentation locally:

```shell
poetry run mkdocs serve
```

Then open http://127.0.0.1:8000/ in your browser.

## Pull Request Process

1. Create a new branch for your feature or bugfix:
   ```shell
   git checkout -b feature/your-feature-name
   ```
   or
   ```shell
   git checkout -b fix/your-bugfix-name
   ```

2. Make your changes and commit them with a descriptive commit message:
   ```shell
   git commit -m "Add feature: your feature description"
   ```

3. Push your branch to your fork:
   ```shell
   git push origin feature/your-feature-name
   ```

4. Open a pull request against the `master` branch of the original repository.

5. Ensure that all tests pass and the documentation is updated if necessary.

6. Wait for a maintainer to review your pull request. They may request changes or improvements.

7. Once your pull request is approved, it will be merged into the main codebase.

## Reporting Issues

If you find a bug or have a feature request, please open an issue on the [GitHub issue tracker](https://github.com/Sibyx/django_api_forms/issues).

When reporting a bug, please include:

- A clear and descriptive title
- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- Django and Python versions
- Any relevant code snippets or error messages

## Feature Requests

Feature requests are welcome. Please provide a clear description of the feature and why it would be beneficial to the project.

## Versioning

We use [Semantic Versioning](https://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/Sibyx/django_api_forms/tags).

## License

By contributing to Django API Forms, you agree that your contributions will be licensed under the project's MIT License.

## Questions?

If you have any questions about contributing, feel free to open an issue or contact the maintainers.

Thank you for contributing to Django API Forms!
