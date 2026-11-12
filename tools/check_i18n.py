#!/usr/bin/env python3
"""Check the translation catalogs (assets/locales/*.json) against the code.

Checks, all via `ast` (no code is imported or executed):

  a. every `t("...")` / `t_choice("...")` literal key under src/tenhut exists in BOTH locale files;
  b. every other string literal in the source that equals a catalog key counts as an indirect
     reference (module-level tables of keys such as PHASE_LABEL, THEME_TITLE, RANKS...), and
     must obviously exist in both files too;
  c. keys defined in en.json that nothing references are reported (`--unused` makes it an error);
  d. en.json and pt.json define the same keys, with the same kind of value (text or list of the
     same length) and the same `{placeholders}`; placeholders also match the keyword arguments
     of the call sites when those are statically visible;
  e. `t()` / `t_choice()` called with an f-string, a concatenation or any other non-literal key is
     flagged, except for the allow-listed indirect call sites below.

Usage: uv run python tools/check_i18n.py [--unused]
Exits with a non-zero status when there is a problem.
"""

from __future__ import annotations

import ast
import json
import re
import string
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src" / "tenhut"
LOCALES = SRC / "assets" / "locales"
REFERENCE = "en"
LANGUAGES = ("en", "pt")
HELPERS = ("t", "t_choice")
KEY_SHAPE = re.compile(r"^[a-z]+(\.[a-z0-9_]+)+$")

# `t(<expression>)` calls whose key is not a literal on purpose: the expression looks the key up
# in a table of keys (checked by rule b) or a value object that carries its key. Entries are "<file>: <source of the argument>".
ALLOWED_DYNAMIC = {
    "services/blocking/install_hint.py: InstallHint.KEYS[system.is_windows]",
    "services/judge/ai_judge.py: self.name_key",
    "services/vision/camera_watcher.py: self._capture_api.open_error_key",
    "cli/command_line.py: flag.help_key",
    "controllers/calibration/calibration_controller.py: reason",
    "controllers/calibration/calibration_planner.py: side.label_key",
    "controllers/camera/camera_controller.py: self.SCOLDS[state]",
    "controllers/camera/camera_controller.py: self.WARNINGS[state]",
    "controllers/camera/gaze_status.py: key",
    "controllers/career_controller.py: self._profile.rank.name_key",
    "controllers/chatter_controller.py: rule.key",
    "controllers/greeter.py: greeting.key",
    "controllers/greeter.py: self.FIRST_TIME.key",
    "controllers/request_outcome.py: self.denied_speech_key",
    "controllers/settings/language_editor.py: i18n.LANG_NAME[value]",
    "controllers/settings/settings_controller.py: backend.name_key",
    "controllers/settings/settings_row_catalog.py: backend.name_key",
    "ui/pages/calibration_page.py: side.label_key",
    "ui/pages/calibration_test_page.py: reading.label_key",
    "ui/pages/calibration_test_page.py: reading.verdict_key",
    "ui/pages/request_page.py: backend.name_key",
    "ui/pages/settings_page.py: key",
    "ui/stage/stage_announcer.py: self.SPEECH[theme]",
    "ui/stage/stage_transitions.py: theme.title_key",
    "ui/widgets/hud_plate.py: session.phase.label_key",
    "ui/widgets/mission_board.py: session.phase.label_key",
    "ui/widgets/rank_plate.py: self._profile.rank.name_key",
}


def load(language: str) -> dict[str, str | list[str]]:
    return json.loads((LOCALES / f"{language}.json").read_text(encoding="utf-8"))


def placeholders(text: str) -> list[str]:
    """Sorted replacement fields of a `str.format` template (name, conversion and spec)."""
    out = []
    for _literal, field, spec, conv in string.Formatter().parse(text):
        if field is not None:
            out.append(field + ("!" + conv if conv else "") + (":" + spec if spec else ""))
    return sorted(out)


def variants(value: str | list[str]) -> list[str]:
    return value if isinstance(value, list) else [value]


def field_names(text: str) -> set[str]:
    return {p.split("!")[0].split(":")[0] for p in placeholders(text)}


class CallSite:
    def __init__(self, where: str, key: str, kwargs: set[str] | None) -> None:
        self.where, self.key, self.kwargs = where, key, kwargs


def source_files() -> list[Path]:
    return sorted(p for p in SRC.rglob("*.py") if "__pycache__" not in p.parts)


def scan_source(catalog: dict[str, object]) -> tuple[list[CallSite], dict[str, list[str]], list[str]]:
    """(literal call sites, indirect references by key, problems about non-literal keys)."""
    calls: list[CallSite] = []
    indirect: dict[str, list[str]] = defaultdict(list)
    problems: list[str] = []
    for path in source_files():
        text = path.read_text(encoding="utf-8")
        tree = ast.parse(text, filename=str(path))
        rel = path.relative_to(SRC).as_posix()
        direct_args: set[int] = set()
        for node in ast.walk(tree):
            if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in HELPERS):
                continue
            if not node.args:
                problems.append(f"{rel}:{node.lineno}: {node.func.id}() without a key")
                continue
            arg = node.args[0]
            where = f"{rel}:{node.lineno}"
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                direct_args.add(id(arg))
                has_star = any(k.arg is None for k in node.keywords)
                kwargs = None if has_star else {k.arg for k in node.keywords}
                calls.append(CallSite(where, arg.value, kwargs))
                continue
            if isinstance(arg, ast.JoinedStr):
                problems.append(f'{where}: {node.func.id}() with an f-string (use t("a.b.c", x=...))')
                continue
            source = ast.get_source_segment(text, arg) or "?"
            if f"{rel}: {source}" not in ALLOWED_DYNAMIC:
                problems.append(f"{where}: {node.func.id}() with a non-literal key `{source}` (not allow-listed)")
        for node in ast.walk(tree):
            is_text = isinstance(node, ast.Constant) and isinstance(node.value, str)
            if is_text and id(node) not in direct_args and node.value in catalog:
                indirect[node.value].append(f"{rel}:{node.lineno}")
    return calls, indirect, problems


def check_catalogs(catalogs: dict[str, dict[str, str | list[str]]]) -> list[str]:
    problems: list[str] = []
    ref = catalogs[REFERENCE]
    for language, cat in catalogs.items():
        for key in sorted(set(ref) ^ set(cat)):
            side = "missing from" if key in ref else "only in"
            problems.append(f"key {key!r} is {side} {language}.json (en.json is the reference)")
        for key in cat:
            if not KEY_SHAPE.match(key):
                problems.append(f"{language}.json: bad key name {key!r} (use <area>.<context>.<name>, lowercase)")
        if list(cat) != sorted(cat):
            problems.append(f"{language}.json: keys are not sorted")
    for key in sorted(set.intersection(*(set(c) for c in catalogs.values()))):
        texts = {lang: variants(catalogs[lang][key]) for lang in catalogs}
        if len({len(v) for v in texts.values()}) > 1 or any(
            isinstance(catalogs[x][key], list) != isinstance(ref[key], list) for x in catalogs
        ):
            problems.append(f"{key!r}: the languages do not have the same number of variants")
            continue
        for index, ref_text in enumerate(texts[REFERENCE]):
            for lang, items in texts.items():
                text = items[index]
                if not text.strip():
                    problems.append(f"{lang}.json: empty text for {key!r}")
                try:
                    same = placeholders(text) == placeholders(ref_text)
                except ValueError as exc:
                    problems.append(f"{lang}.json: invalid format string in {key!r}: {exc}")
                    continue
                if not same:
                    problems.append(
                        f"{key!r}: placeholders differ: {REFERENCE} {placeholders(ref_text)} vs {lang} {placeholders(text)}"
                    )
                if (text[:1].isspace(), text[-1:].isspace()) != (ref_text[:1].isspace(), ref_text[-1:].isspace()):
                    problems.append(f"{key!r}: leading/trailing spaces differ between {REFERENCE} and {lang}")
    return problems


def check_calls(calls: list[CallSite], catalogs: dict[str, dict[str, str | list[str]]]) -> list[str]:
    problems: list[str] = []
    for call in calls:
        for lang, cat in catalogs.items():
            if call.key not in cat:
                problems.append(f"{call.where}: key {call.key!r} is missing from {lang}.json")
        ref = catalogs[REFERENCE].get(call.key)
        if ref is None or call.kwargs is None:
            continue
        needed = set().union(*(field_names(v) for v in variants(ref)))
        if call.kwargs != needed and not (not needed and not call.kwargs):
            problems.append(
                f"{call.where}: {call.key!r} takes {sorted(needed)} but the call passes {sorted(call.kwargs)}"
            )
    return problems


def main() -> int:
    catalogs = {lang: load(lang) for lang in LANGUAGES}
    calls, indirect, problems = scan_source(catalogs[REFERENCE])
    problems += check_catalogs(catalogs)
    problems += check_calls(calls, catalogs)

    used = {c.key for c in calls} | set(indirect)
    unused = sorted(k for k in catalogs[REFERENCE] if k not in used)
    if "--unused" in sys.argv:
        problems += [f"unused key {k!r} (defined in en.json, referenced nowhere)" for k in unused]
    else:
        for k in unused:
            print(f"(unused) {k!r}")

    for p in problems:
        print(p)
    print(
        f"{len(calls)} t() call sites, {len(indirect)} indirect keys, {len(catalogs[REFERENCE])} keys in en.json, "
        f"{len(unused)} unused, {len(problems)} problem(s)."
    )
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
