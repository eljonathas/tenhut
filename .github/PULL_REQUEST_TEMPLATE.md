## What and why

<!-- One or two sentences. Link the issue if there is one: Fixes #123 -->

## Checked on

- [ ] Linux
- [ ] Windows
- [ ] macOS

## Checklist

- [ ] `uv run ruff check . && uv run ruff format --check .` pass
- [ ] `uv run pytest` passes (new behaviour has a test)
- [ ] New or changed UI text uses `t("area.context.name")` with a key in both `en.json` and `pt.json` (`uv run python tools/check_i18n.py --unused`)
- [ ] Anything touching `helper/hosts-helper`, sudoers or the install flow is called out below (it runs as root)

## Screenshots

<!-- For visual changes: `uv run python tools/make_screenshots.py` -->
