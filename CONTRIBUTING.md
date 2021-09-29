# Contributing to django-api-forms

If you like nice diagrams you can also check repository
[code map](https://app.codesee.io/maps/public/c7286640-20f6-11ec-a894-61b8cbaa0d26).

## Pull requests

Feel free to open pull requests but please keep in mind this checklist:

- write tests
- write changes to to `CHANGELOG.md`
- update `README.md` (if needed)
- update documentation (if needed)

## Development

We use [poetry](https://python-poetry.org/) for dependency management. Please write your source code according to the
[PEP8](https://www.python.org/dev/peps/pep-0008/) code-style. [flake8](https://github.com/pycqa/flake8) is used for
code-style and code-quality checks. Please, be sure that your IDE is following settings according to `.editorconfig`
file.

We use[Django-style tests](https://docs.djangoproject.com/en/3.1/topics/testing/overview/).

```shell script
# Run tests
poetry run python runtests.py

# Run flake8
poetry run flake8 .
```

## Documentation

Documentation is places in `docs` directory and it's generated using
[mkdocs-material](https://squidfunk.github.io/mkdocs-material/). You can build docs calling `poetry run mkdocs build`.
Docs will be in `sites` directory after build. Documentation is updated after every push to `origin/master` branch
using GitHub Actions.
