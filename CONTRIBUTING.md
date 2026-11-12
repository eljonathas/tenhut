# Contributing to Tenhut

Thanks for helping. Bug reports, translations, docs and code are all welcome.

## Quick start

You need Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/eljonathas/tenhut && cd tenhut
uv sync --group dev                 # add --extra camera to work on camera surveillance
uv run pytest                       # tests run headless
uv run ruff check . && uv run ruff format --check .
uv run tenhut --dry-run             # run the app without touching your hosts file
```

**Always use `--dry-run` while developing.** Without it the app really edits your hosts file.

## Working on the code

- The code map is in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md). Read it before a large change.
- Tests live in `tests/` and run without a display (`SDL_VIDEODRIVER=dummy`) and without touching your real
  config: `tests/conftest.py` points the `XDG_*` folders at a temporary directory. Do the same in any script you
  write, because the app otherwise reads and may migrate your real data folders.
- New behaviour needs a test. UI changes need a screenshot in the PR (`uv run python tools/make_screenshots.py`).
- All user-facing text goes through the translation catalog, never a hard-coded string:
  see [docs/TRANSLATING.md](docs/TRANSLATING.md).
- Code, comments and commit messages are in **English**.

### The root helper needs extra care

`helper/hosts-helper` runs as root (Linux, macOS). Rules for any change to it:

1. It stays a single standalone file. It must not import the `tenhut` package.
2. It must not read environment variables or any user-writable file to decide what to write.
3. Every domain is validated against a strict pattern before it reaches `/etc/hosts`.
4. Say in the PR description that you touched it.

### Platforms

Linux is the reference platform. Windows and macOS are beta: if you can, test your change there. If you can't, say
so in the PR and CI will still run the tests on all three.

## Commits and pull requests

- Use [Conventional Commits](https://www.conventionalcommits.org/): `feat:`, `fix:`, `docs:`, `refactor:`,
  `test:`, `ci:`, `build:`, `chore:`. Add a scope when it helps (`fix(camera): ...`). Breaking changes get a `!`
  and a `BREAKING CHANGE:` footer.
- Keep a pull request to one subject. Small PRs get reviewed faster.
- CI must be green (lint, tests on Linux, Windows and macOS).
- Add a line to `CHANGELOG.md` under *Unreleased* for anything a user would notice.

## Releasing (maintainers)

1. Move the *Unreleased* entries in `CHANGELOG.md` under a new version heading and bump `version` in `pyproject.toml`.
2. Tag and push: `git tag v0.2.0 && git push origin v0.2.0`.
3. The *Release* workflow builds Linux, Windows and macOS (with and without camera) and publishes the GitHub Release
   with checksums. The camera builds may fail without blocking the rest; fix or re-run them.
