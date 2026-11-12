# Translating Tenhut

Tenhut has no text in its code: every sentence the user sees is a **translation key** that the active language turns
into text. English and Brazilian Portuguese ship today.

```python
from tenhut.i18n import t, t_choice

t("button.request_pass")  # a plain string
t("speech.mission.task_done_remaining", n=3)  # {n} is filled in with str.format
t_choice("speech.work.idle_remarks")  # a list value: one variant picked at random
```

The catalogs are `src/tenhut/assets/locales/<language>.json`: flat dotted keys, sorted, UTF-8, 2-space indent.
`en.json` is the reference and the fallback (a key missing from your language falls back to English, then to the key
itself, and is logged once).

## Add a language

Say you are adding Spanish (`es`).

1. Copy `src/tenhut/assets/locales/en.json` to `es.json` and translate **the values**, never the keys.
   - Keep every `{placeholder}` exactly as it is (`{n}`, `{target}`, `{time}`...), in any position in the sentence.
   - A value that is a list holds variants of the same line: keep the list and translate each item.
   - The General is a gruff, funny drill-sergeant who calls the user "soldier". Translate the voice, not word by word.
   - Buttons are narrow. Prefer short words (`REQUEST PASS`, not `REQUEST PERMISSION TO ACCESS`). Text that doesn't fit
     is shrunk and then cut with "…", so look at the result.
2. Add the language name, written in that language, as `language.name.es` in **every** locale file
   (`"language.name.es": "Español"`).
3. Register it in code:
   - `SUPPORTED` in `src/tenhut/i18n/translator.py`, and teach `detect()` to recognise the system locale (`es_*`).
   - `LANG_NAME` and `LANG_FOR_JUDGE` in `src/tenhut/i18n/__init__.py`. `LANG_FOR_JUDGE` is the English name of the
     language, used to tell the AI judge which language to answer in.
4. Check it:
   ```bash
   uv run python tools/check_i18n.py --unused   # same keys in every locale, same placeholders, nothing unused
   uv run pytest tests/test_i18n.py
   uv run python tools/make_screenshots.py      # then look at docs/screenshots (set the language in the script)
   ```
5. Open a pull request with the new file and the two small code edits. Add the language to the README.

## Change an existing text

Edit the value in the JSON files. Don't rename keys for wording: keys describe the *meaning*.

## Add a new text in code

1. Pick a key: `<area>.<context>.<name>`, lowercase snake_case. The areas (`button`, `speech`, `status`, `settings`,
   `notify`, `error`...) are listed in the docstring of `src/tenhut/i18n/__init__.py`.
2. Add it to **all** locale files, then call `t("area.context.name")`.
3. Never concatenate translated fragments into a sentence when word order differs between languages. Use one key
   with placeholders instead.
4. Run `tools/check_i18n.py`. CI runs it too.
