---
authors:
    - subhajit
title: "Ruff: Modern Python Linter & Formatter Walkthrough"
description: "Complete Ruff setup guide: Python linter and formatter with uv integration, pre-commit hooks, and CI integration from install to production."
slug: ruff-modern-linter
date:
    created: 2025-09-24
    updated: 2026-02-09
categories:
    - Software Engineering
tags:
    - Ruff
    - CI/CD
    - Automation
meta:
    - name: keywords
      content: ruff, uv, pre-commit, GitHub Actions, linter, formatter, code quality
---


<!-- more -->
Writing clean, readable code is essential for collaboration and maintainability. Linters and formatters help us keep our codebase consistent and easy to understand.

Linters like Flake8, Pylint, and mypy analyze your code and look for errors, stylistic issues, and suspicious constructs. On the other hand, formatters like Black and autopep8 help us format our code according to a consistent style.

Although we have many tools to choose from, the main issue is juggling too many tools, which can be time-consuming and confusing.

A better alternative is Ruff, a fast, easy-to-use tool that handles both linting and formatting. Similar to other tools, it has excellent defaults and a single, simple CLI.

In this walkthrough, we’ll set up Ruff with a simple, one-time configuration that works locally and integrates seamlessly with uv, pre-commit, and GitHub Actions.

## Installing Ruff

Let's start by installing Ruff. 

Ruff works out of the box, so we don’t need complicated setup steps. Here are several ways to install Ruff, depending on your system and preferences:



**Install Ruff globally using uv** (recommended):
```bash
uv tool install ruff@latest
```
**Or, add Ruff as a development dependency:**
```bash
uv add --dev ruff
```
**Or, install Ruff using pip:**
```bash
pip install ruff
```
**Or, install Ruff using pipx:**
```bash
pipx install ruff
```

If you use MacOS, you can use brew to install Ruff instead of uv. For other systems, the detailed installation instructions are available in the [installation guide](https://docs.astral.sh/ruff/installation/).


**Verify installation:** after installing Ruff, you can verify the installation by running the following command:

```bash
ruff --version
```
Once you see the version number, you know Ruff is installed correctly and we are ready to start using it.
 
## Linting Your Python Code
!!! note
    linter helps us to keep our code consistent and error-free, it does not mean that our code is bug free

`ruff check` is the primary entry point to the Ruff linter.t accepts a list of files or directories and lints all discovered Python files, optionally fixing any fixable errors. When linting a directory, Ruff recursively searches for Python files in that directory and all its subdirectories:

```bash
ruff check . # lint all files in the current directory
ruff check src/ # lint all files in the src directory
ruff check src/main.py # lint the main.py file
```
We can also fix the errors using the `--fix` flag:

```bash
ruff check --fix . # fix all fixableerrors in the current directory
```
we can also show only the changed files using the `--exit-non-zero-on-fix --quiet` flag:
```bash
ruff check --exit-non-zero-on-fix --quiet . # show only the changed files
```
When you’re actively working on code, Ruff can simplify your workflow even more by informing you of errors as you develop. This will speed up the overall process and make you more productive.  

To do this, we can use the `--watch` flag:
```bash
ruff check  --watch  # lint all files in the current directory and watch for changes
```
For the full list of supported options, run `ruff check --help`.

### Rule Selection
Ruff's linter mirrors Flake8's rule code system, in which each rule code consists of a one-to-three letter prefix, followed by three digits (e.g., F401). To know more about the rules we can use `ruff rule F401`

When you run this command, you get more details in Markdown format in your terminal:
<Insert image of the rule details>

To apply a specific rule, use the `--select` flag:
```bash
ruff check --select F401 . # lint all files in the current directory, focusing on the F401 rule
```
The set of active rules is managed through the `lint.select`, `lint.extend-select`, and `lint.ignore` configurations in the `ruff.toml` file:
```toml title="ruff.toml"
[lint]
select = ["E", "F"]
ignore = ["F401"]
```


## Formatting

## Formatting

Ruff also formats code. Use it exactly like a formatter:

```bash
# write changes to disk
ruff format .

# validate formatting without writing
ruff format --check .
```

Tip: Import sorting is enforced by Ruff’s lint rules (the `I` group), not by `ruff format`. Keep both `ruff check` and `ruff format` in your workflow.

## Configuration (pyproject.toml)

Create or update `pyproject.toml` with a minimal Ruff config:

```toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I"] # pycodestyle, pyflakes, isort
ignore = [
  # add rule codes to ignore here, e.g., "E203"
]

[tool.ruff.format]
docstring-code-format = true
docstring-code-line-length = 88
```

Notes:

- `select` adds rule families. `I` enables isort-style import rules.
- `line-length` and `target-version` align formatter and linter expectations.
- Keep ignores small and documented; prefer fixing code.

The Real Python article has more on configuration and rule groups: [`realpython.com/ruff-python`](https://realpython.com/ruff-python/).

## Pre-commit hooks

Add Ruff to `.pre-commit-config.yaml` to enforce locally before every commit:

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.9 # update to the latest stable
    hooks:
      - id: ruff
        args: ["--fix"]
      - id: ruff-format
```

Install hooks:

```bash
pre-commit install
```

## CI with GitHub Actions (using uv)

Create `.github/workflows/ruff.yml`:

```yaml
name: Ruff Quality
on: [push, pull_request]
jobs:
  ruff:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup uv
        uses: astral-sh/setup-uv@v6
      - name: Lint (no fixes)
        run: uvx ruff check .
      - name: Format check
        run: uvx ruff format --check .
```

If you’re not using `uv`, replace `uvx ruff …` with `ruff …` after setting up Python and installing Ruff.

## IDE integration

- VS Code: Install the “Ruff” extension and set it as the default linter/formatter.
- PyCharm: Enable the Ruff plugin for inspections and formatting.

## Summary

Ruff simplifies Python code quality by consolidating linting, import sorting, and formatting with exceptional performance. Start with the defaults, wire it into pre-commit and CI, and customize gradually via `pyproject.toml`.

Further reading: Real Python — “Ruff: A Modern Python Linter for Error-Free and Maintainable Code” [`realpython.com/ruff-python`](https://realpython.com/ruff-python/).


## Why Ruff ?
- **One tool**: Linting (Flake8 rules), import sorting (isort rules), and formatting (Black-like) in one binary.
- **Fast**: Written in Rust; great for local and CI.
- **Simple**: Sensible defaults; configure only what you need.