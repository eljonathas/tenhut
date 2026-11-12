import importlib.util
import json
import logging
import random
import subprocess
import sys
from pathlib import Path

import pytest

from tenhut import i18n
from tenhut.i18n import Translator, t, t_choice

ROOT = Path(__file__).resolve().parents[1]


def _load_checker():
    spec = importlib.util.spec_from_file_location("check_i18n", ROOT / "tools" / "check_i18n.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def locales(tmp_path):
    """A tiny catalog pair: `pt` lacks one English key, `en` has a list value."""
    (tmp_path / "en.json").write_text(
        json.dumps(
            {
                "a.b.hello": "Hello",
                "a.b.count": "{n} left",
                "a.b.only_en": "English only",
                "a.b.remarks": ["one", "two", "three"],
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "pt.json").write_text(
        json.dumps(
            {
                "a.b.hello": "Olá",
                "a.b.count": "faltam {n}",
                "a.b.remarks": ["um", "dois", "três"],
            }
        ),
        encoding="utf-8",
    )
    return tmp_path


def test_catalog_is_complete_and_consistent():
    """Every key used by the code exists in both locale files, nothing is unused, placeholders match."""
    r = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "check_i18n.py"), "--unused"], capture_output=True, text=True
    )
    assert r.returncode == 0, r.stdout + r.stderr


def test_translation_in_both_languages():
    i18n.set_language("en")
    assert t("phase.in_combat") == "IN COMBAT"
    i18n.set_language("pt")
    assert t("phase.in_combat") == "EM COMBATE"


def test_placeholders_are_formatted():
    i18n.set_language("en")
    assert t("speech.mission.task_done_remaining", n=3) == "One down. 3 to go."
    i18n.set_language("pt")
    assert t("speech.mission.task_done_remaining", n=3) == "Uma a menos. Faltam 3."


def test_fallback_goes_to_english_then_to_the_key(locales, caplog):
    tr = Translator(locales, "pt")
    assert tr.translate("a.b.hello") == "Olá"
    assert tr.translate("a.b.only_en") == "English only"  # missing in pt: English
    with caplog.at_level(logging.WARNING, logger="tenhut.i18n.translator"):
        assert tr.translate("a.b.nowhere") == "a.b.nowhere"  # missing everywhere: the key itself
        assert tr.translate("a.b.nowhere") == "a.b.nowhere"
    assert len([r for r in caplog.records if "a.b.nowhere" in r.getMessage()]) == 1  # logged once


def test_unknown_language_falls_back_to_english(locales):
    tr = Translator(locales)
    assert tr.set_language("xx") == "en"
    assert tr.translate("a.b.hello") == "Hello"


def test_missing_locale_files_never_raise(tmp_path):
    tr = Translator(tmp_path, "pt")
    assert tr.translate("a.b.hello") == "a.b.hello"


def test_bad_format_parameters_never_raise(locales):
    tr = Translator(locales, "en")
    assert tr.translate("a.b.count") == "{n} left"  # no parameters given: untouched
    assert tr.translate("a.b.count", other=1) == "{n} left"  # wrong parameters: untouched
    assert tr.translate("a.b.count", n=2) == "2 left"


def test_variants_use_one_random_choice_per_call(locales):
    tr = Translator(locales, "pt")
    random.seed(7)
    expected = random.choice(["um", "dois", "três"])
    random.seed(7)
    assert tr.choice("a.b.remarks") == expected
    assert random.random() == _after_one_choice(7)  # exactly one draw was consumed
    assert tr.translate("a.b.remarks") == "um"  # t() on a list value is the first variant
    random.seed(7)
    tr.choice("a.b.hello")  # a plain string consumes nothing
    assert random.random() == _fresh_random(7)


def _after_one_choice(seed):
    random.seed(seed)
    random.choice([1, 2, 3])
    return random.random()


def _fresh_random(seed):
    random.seed(seed)
    return random.random()


def test_module_level_variants_are_all_reachable():
    i18n.set_language("pt")
    seen = {t_choice("speech.work.idle_remarks") for _try in range(200)}
    assert len(seen) == len(i18n.translator().catalog("pt")["speech.work.idle_remarks"])


def test_languages_have_the_same_number_of_variants():
    for key, value in i18n.translator().catalog("en").items():
        if isinstance(value, list):
            assert len(i18n.translator().catalog("pt")[key]) == len(value), key


def test_auto_picks_a_supported_language(monkeypatch):
    for var in ("LC_ALL", "LC_MESSAGES", "LANGUAGE"):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setenv("LANG", "pt_BR.UTF-8")
    assert i18n.set_language("auto") == "pt"
    assert i18n.lang() == "pt"
    monkeypatch.setenv("LANG", "de_DE.UTF-8")
    assert i18n.set_language("auto") == "en"


def test_public_names_stay_available():
    assert i18n.LANGS == ["auto", "pt", "en"]
    assert set(i18n.LANG_NAME) == set(i18n.LANGS)
    assert all(code in i18n.LANG_FOR_JUDGE for code in ("pt", "en"))
    i18n.set_language("pt")
    assert t(i18n.LANG_NAME["pt"]) == "Português"


def test_checker_flags_broken_catalogs():
    check = _load_checker()
    good = {"en": {"a.b.x": "Hi {n}", "a.b.y": ["a", "b"]}, "pt": {"a.b.x": "Oi {n}", "a.b.y": ["a", "b"]}}
    assert check.check_catalogs(good) == []
    missing = {"en": dict(good["en"]), "pt": {"a.b.x": "Oi {n}"}}
    assert any("missing from pt.json" in p for p in check.check_catalogs(missing))
    wrong_placeholder = {"en": dict(good["en"]), "pt": {"a.b.x": "Oi {m}", "a.b.y": ["a", "b"]}}
    assert any("placeholders differ" in p for p in check.check_catalogs(wrong_placeholder))
    wrong_variants = {"en": dict(good["en"]), "pt": {"a.b.x": "Oi {n}", "a.b.y": ["a"]}}
    assert any("number of variants" in p for p in check.check_catalogs(wrong_variants))
    call = check.CallSite("f.py:1", "a.b.x", set())
    assert any("takes ['n']" in p for p in check.check_calls([call], good))
    assert any("missing from en.json" in p for p in check.check_calls([check.CallSite("f.py:2", "a.b.z", None)], good))


def test_checker_flags_non_literal_keys(tmp_path, monkeypatch):
    check = _load_checker()
    (tmp_path / "bad.py").write_text('def f(x):\n    return t(f"a.{x}") + t("a." + x) + t("a.b.x")\n', encoding="utf-8")
    monkeypatch.setattr(check, "SRC", tmp_path)
    calls, _indirect, problems = check.scan_source({"a.b.x": "Hi"})
    assert [c.key for c in calls] == ["a.b.x"]
    assert any("f-string" in p for p in problems)
    assert any("non-literal key" in p for p in problems)
