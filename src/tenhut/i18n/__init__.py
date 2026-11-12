"""Internationalisation: semantic translation keys backed by JSON locale files.

User-facing text never appears in the code. The code asks for a key and the active language
provides the text::

    from tenhut.i18n import t, t_choice

    t("notify.mission_started.title")                       # a plain string
    t("speech.mission.task_done_remaining", n=3)            # `str.format` parameters
    t_choice("speech.work.idle_remarks")                    # one random variant of a list value

The catalogs live in `assets/locales/<language>.json` (flat dotted keys sorted alphabetically,
UTF-8, 2-space indent). `en.json` is the reference and the fallback; `pt.json` is complete as well.
A value is a string, or a list of strings (variants picked by `t_choice`, one `random.choice` per call).
Lookup order: active language, English, the key itself (never raises; a missing key is logged once).

Key naming convention: `<area>.<context>.<name>`, lowercase snake_case. The key describes the
meaning, never the wording, and the text is never part of the key.

Areas:
    phase         the pomodoro phase labels                  phase.in_combat
    button        button captions                            button.request_pass
    field         text input placeholders                    field.task.placeholder
    speech        what the General says (balloons)           speech.work.watching_you
    status        HUD / status-line fragments                status.line.next_request
    settings      the settings page                          settings.row.work_minutes
    calibration   the camera calibration pages               calibration.step.look_down
    camera        camera surveillance states and errors      camera.status.looking_down
    judge         judge names and offline verdicts           judge.name.none
    board         the chalkboard (tasks, request, desertion) board.request.title
    notify        desktop notifications (title and body)     notify.mission_started.title
    stamp         the big rubber stamps                      stamp.approved
    popup         floating texts                             popup.promoted
    theme         the stage titles                           theme.office.title
    rank          the military ranks                         rank.sergeant
    error         failure explanations                       error.helper.file_missing
    hint          short help lines and command-line help     hint.cli.dry_run
    language      language names (always in their language)  language.name.pt

Variant lists get one key holding a list (`speech.work.idle_remarks`). Reuse a key when the meaning
and the text are identical in several places. Module-level tables that must be translated at
display time (themes, ranks, camera states...) hold *keys*; the drawing code calls `t(...)` on them.
`tools/check_i18n.py` verifies that code and catalogs agree.
"""

from __future__ import annotations

from .translator import DEFAULT_LANGUAGE, FALLBACK_LANGUAGE, SUPPORTED, Translator, detect

LANGS = ["auto", *SUPPORTED]
# Language names are keys too (always written in their own language, so the picker is readable).
LANG_NAME = {
    "pt": "language.name.pt",
    "en": "language.name.en",
    "auto": "language.name.auto",
}
# Language names for the AI judge prompt (model-facing, not a UI string).
LANG_FOR_JUDGE = {"pt": "Brazilian Portuguese", "en": "English"}

_translator = Translator()


def set_language(pref: str | None) -> str:
    """Select the UI language (`pt`, `en` or `auto`) and return the resulting code."""
    return _translator.set_language(pref)


def lang() -> str:
    """The active language code."""
    return _translator.language


def t(key: str, /, **params: object) -> str:
    """Translate a key, applying `str.format` parameters."""
    return _translator.translate(key, **params)


def t_choice(key: str, /, **params: object) -> str:
    """Translate a key whose value is a list of variants: one is picked with `random.choice`."""
    return _translator.choice(key, **params)


def translator() -> Translator:
    """The Translator behind the module-level helpers (tools and tests inspect its catalogs)."""
    return _translator


__all__ = [
    "DEFAULT_LANGUAGE",
    "FALLBACK_LANGUAGE",
    "LANGS",
    "LANG_FOR_JUDGE",
    "LANG_NAME",
    "SUPPORTED",
    "Translator",
    "detect",
    "lang",
    "set_language",
    "t",
    "t_choice",
    "translator",
]
