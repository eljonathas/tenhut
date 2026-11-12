"""The Translator: loads the locale files and resolves keys with a safe fallback chain."""

from __future__ import annotations

import json
import logging
import os
import random
from pathlib import Path

from ..asset_paths import AssetPaths

log = logging.getLogger(__name__)

SUPPORTED = ("pt", "en")
DEFAULT_LANGUAGE = "pt"
FALLBACK_LANGUAGE = "en"
LOCALE_ENV_VARS = ("LC_ALL", "LC_MESSAGES", "LANG", "LANGUAGE")
NEUTRAL_LOCALES = ("C", "POSIX", "C.UTF-8")

Variants = str | list[str]


def locales_dir() -> Path:
    """Folder with the `<language>.json` files (inside the bundle when frozen with PyInstaller)."""
    return AssetPaths.root() / "locales"


def detect() -> str:
    """Language of the operating system session: `pt` for any Portuguese locale, `en` otherwise."""
    for var in LOCALE_ENV_VARS:
        value = os.environ.get(var, "")
        if value and value not in NEUTRAL_LOCALES:
            return "pt" if value.lower().startswith("pt") else "en"
    return "en"


class Translator:
    """Resolves translation keys for one active language.

    A key is looked up in the active language, then in English, and finally the key itself is
    returned. Nothing here ever raises: a missing key is logged once at WARNING level.
    """

    def __init__(self, directory: Path | None = None, language: str = DEFAULT_LANGUAGE) -> None:
        self._directory = directory if directory is not None else locales_dir()
        self._catalogs: dict[str, dict[str, Variants]] = {}
        self._reported: set[tuple[str, str]] = set()
        self.language = language

    # ------------------------------------------------------------------ language
    def set_language(self, preference: str | None) -> str:
        """Select the language: `auto` (or empty) detects it from the environment. Returns the code."""
        if preference in (None, "", "auto"):
            self.language = detect()
        else:
            self.language = preference if preference in SUPPORTED else FALLBACK_LANGUAGE
        return self.language

    # ------------------------------------------------------------------ catalogs
    def catalog(self, language: str) -> dict[str, Variants]:
        """The key -> text (or list of variants) mapping of a language; empty if the file is missing."""
        if language not in self._catalogs:
            self._catalogs[language] = self._load(language)
        return self._catalogs[language]

    def _load(self, language: str) -> dict[str, Variants]:
        path = self._directory / f"{language}.json"
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            log.warning("cannot load locale file %s: %s", path, exc)
            return {}
        return {k: v for k, v in data.items() if isinstance(v, (str, list))}

    # ------------------------------------------------------------------ lookup
    def variants(self, key: str) -> Variants:
        """Raw value of a key following the fallback chain (active language, English, the key)."""
        for language in (self.language, FALLBACK_LANGUAGE):
            value = self.catalog(language).get(key)
            if value:
                return value
        marker = (self.language, key)
        if marker not in self._reported:
            self._reported.add(marker)
            log.warning("missing translation key %r (language %r)", key, self.language)
        return key

    def translate(self, key: str, **params: object) -> str:
        """Text of a key with `str.format` parameters applied. A list value yields its first variant."""
        value = self.variants(key)
        text = value if isinstance(value, str) else (value[0] if value else key)
        return self._format(text, params)

    def choice(self, key: str, **params: object) -> str:
        """One random variant of a list value (one `random.choice` call); a plain string is returned as is."""
        value = self.variants(key)
        text = value if isinstance(value, str) else (random.choice(value) if value else key)
        return self._format(text, params)

    @staticmethod
    def _format(text: str, params: dict[str, object]) -> str:
        if not params:
            return text
        try:
            return text.format(**params)
        except (KeyError, IndexError, ValueError):
            log.warning("cannot format %r with %s", text, sorted(params))
            return text
