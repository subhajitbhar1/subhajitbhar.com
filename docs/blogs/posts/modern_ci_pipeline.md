---
authors:
    - subhajit
title: How you can set up a Python Code Quality CI Pipeline in 5 minutes
description: Step-by-step guide to set up a Python Code Quality CI Pipeline using uv, Ruff, and ty.
slug: modern-ci-pipeline
date:
    created: 2025-09-24
categories:
    - Software Engineering
tags:
    - Ruff
    - CI/CD
    - DevOps
meta:
    - name: keywords
      content: uv, Ruff, ty, GitHub Actions, CI pipeline, Python tooling, code quality
---
You can create a Python Code Quality CI pipeline using uv, Ruff, and ty within 5 minutes.

<!-- more -->
Most of us begin a Python project with high hopes. We set up a clean virtual environment, organize a requirements file, and plan to add a linter—then forget.

But as we add more dependencies, the requirements file can get messy.  The same thing happens with our tests and documentation. They start out organized but quickly become hard to manage. So, we end up with a codebase that is difficult to maintain and understand.

Before long, we start wondering why the code is breaking, tests are failing, or the documentation is out of date. So, we need to add a CI pipeline to help us catch these errors early and make sure everything works as it should.

In this article, we’ll set up a fast CI pipeline for code quality using `uv`, `Ruff`, and `ty` from Astral. We’ll use a single lockfile (`uv.lock`), one linter/formatter (`ruff`), and one type checker (`ty`). 

- **lockfile consistency** ensures the lockfile is in sync with `pyproject.toml` so installs are reproducible. We will use `uv lock --locked` for this.
- **lint check** spots potential bugs and code smells before they cause problems and helps write better code. We will use `ruff` for this.
- **formatter check** keeps your code style consistent across the entire project and across different editors making it easier to review code. We will use `ruff` for this.
- **type checker** makes sure your functions use the right data types and avoid type errors early. We will use `ty` for this.

## Dependency check
When we initialize a new project with `uv init`, it creates an empty `uv.lock` alongside `pyproject.toml`. This lockfile ensures everyone installs identical dependency graphs. If we modify `pyproject.toml` directly, the lock can drift out of sync. We can verify the lock is up to date with `uv lock --locked` (fails if regeneration would be required).

So in our CI pipeline, we add a step to check that the lockfile is in sync with `pyproject.toml`. If it isn’t, CI fails. Create `.github/workflows/code-quality.yml` and add:

```yaml
name: Python Code Quality
on: [push, pull_request]
jobs:
  lockfile-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: install uv
        uses: astral-sh/setup-uv@v6
        with:
          version: 0.6.12
      - run: uv lock --locked
```

Since we’ll run lint and format checks in parallel, extract uv setup to a composite action. Create `.github/actions/setup/action.yml` with:

```yaml
name: Install UV
description: Install UV package manager
runs:
  using: composite
  steps:
    - name: install uv
      uses: astral-sh/setup-uv@v6
      with:
        version: 0.6.12

```

You can then use this action in other workflows via the `uses` keyword:
```yaml
name: Python Code Quality
on: [push, pull_request]
jobs:
  lockfile-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: ./.github/actions/setup
      - run: uv lock --locked
```

## Lint check
The second step is linting. We’ll use `ruff` to enforce standards and catch likely bugs. Add a `lint-check` job to `.github/workflows/code-quality.yml`:

```yaml
lint-check:
    runs-on: ubuntu-latest
    needs: [lockfile-check]
    steps:
      - uses: actions/checkout@v4
      - uses: ./.github/actions/setup
      - run: uvx ruff check .
```

## Formatter check
Use `ruff format` to enforce consistent formatting. Import sorting is handled by Ruff’s isort rules during linting (not by the formatter). To validate formatting in CI, run `ruff format --check`. Add a `format-check` job to `.github/workflows/code-quality.yml`:
```yaml
format-check:
    runs-on: ubuntu-latest
    needs: [lockfile-check]
    steps:
      - uses: actions/checkout@v4
      - uses: ./.github/actions/setup
      - run: uvx ruff format --check .
```

## Type check
Use `ty check` to run static type checks. `ty` is a fast, modern type checker. Add a `type-check` job to `.github/workflows/code-quality.yml`:
```yaml
type-check:
    runs-on: ubuntu-latest
    needs: [lockfile-check]
    steps:
      - uses: actions/checkout@v4
      - uses: ./.github/actions/setup
      - run: uvx ty check .
```

!!! warning "Note"
    `ty` is in preview state. Use this with caution. Another good alternative for static type checking is `pyright`.


## Full CI pipeline

```yaml
name: Python Code Quality
on: [push, pull_request]
jobs:
  lockfile-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: ./.github/actions/setup
      - run: uv lock --locked

  lint-check:
    runs-on: ubuntu-latest
    needs: [lockfile-check]
    steps:
      - uses: actions/checkout@v4
      - uses: ./.github/actions/setup
      - run: uvx ruff check .

  format-check:
    runs-on: ubuntu-latest
    needs: [lockfile-check]
    steps:
      - uses: actions/checkout@v4
      - uses: ./.github/actions/setup
      - run: uvx ruff format --check .

  type-check:
    runs-on: ubuntu-latest
    needs: [lockfile-check]
    steps:
      - uses: actions/checkout@v4
      - uses: ./.github/actions/setup
      - run: uvx ty check .
```
### Quick walkthrough

- **lockfile-check**: Verifies `uv.lock` is in sync with `pyproject.toml` using `uv lock --locked`. Fails early if the lock needs regeneration.
- **lint-check**: Runs `uvx ruff check .` to catch bugs and style issues. Import sorting is enforced by Ruff’s isort rules here.
- **format-check**: Runs `uvx ruff format --check .` to ensure consistent formatting without modifying files.
- **type-check**: Runs `uvx ty check .` for fast static type analysis. `ty` is preview; `pyright` is a stable alternative.
- Parallelism: `needs: [lockfile-check]` means lint, format, and type checks run in parallel after the lockfile passes.
## Conclusion
With just a few lines of YAML, you now have reproducible installs with `uv lock --locked`, fast linting and formatting via Ruff, and type checks with `ty` running on every push and pull request. This keeps drift in check, makes reviews calmer, and stops easy-to-miss issues from slipping into main.

If you want to take it further, add tests with `pytest`, coverage thresholds, caching for `uv` and lint artifacts, and a build matrix across Python versions. Keep it fast and opinionated—the best CI is the one that runs on every change without friction.
