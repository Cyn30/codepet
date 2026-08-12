# Contributing to CodePet

Thank you for helping make consistent coding more joyful.

## Development workflow

1. Fork the repository and create a branch from `main`.
2. Install the development dependencies with `python -m pip install -e ".[desktop,dev]"`.
3. Make one focused change and add tests for changed behavior.
4. Run `python -m unittest discover -s tests -v` and `ruff check src tests`.
5. Open a pull request that explains the user-visible result and test coverage.

## Project rules

- Never collect keystrokes, source code, commit messages, or unrelated activity.
- Never persist GitHub tokens in the save file or repository.
- Keep domain rules independent from Qt, HTTP, and file-system code.
- Prefer small modules and delete obsolete code when replacing behavior.
- New random rewards must be deterministic from an auditable event ID.
- New pet art must be original and licensed for redistribution.

## Good first issues

- Add a new test for an edge case.
- Improve setup documentation for one operating system.
- Add an accessible high-contrast theme.
- Redraw and review one complete eight-frame animation row for an existing breed.
