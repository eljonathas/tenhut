# Architecture

Tenhut is a pygame app split into layers that only depend downward. Everything is a small class in its own file
(`snake_case.py` named after the class); the `__init__.py` files only re-export.

```
tenhut/
  __init__.py, __main__.py   main(): hands over to the command line
  cli/                       CommandLine + one Command class per flag (run, install/uninstall helper or desktop entry)
  application.py             Application: the running app (builds the object graph, pumps events, ticks, draws)
  assembly/                  composition root: *Assembly classes that build and wire everything (no logic)
  controllers/               behaviour: mission, judge, settings, calibration, camera, blocking, speech, input...
  ui/                        what the user touches: layout, fonts, widgets, pages, the stage that composes a frame
  game/                      what is drawn on the canvas: character, scenes, animations, audio, painting primitives
  services/                  talking to the world: platform, blocking (hosts file), judge (Claude/Codex), vision (camera)
  core/                      pure rules: settings, session (state machine), profile/ranks, campaign themes
  i18n/                      translation keys; the catalogs are JSON in assets/locales/
  assets/                    icons, fonts, locale files (bundled into the release builds)
```

## Dependency rule

```
cli, application, assembly
        │
   controllers ──► ui (layout, painting, widgets)        pages and stage depend on controller *interfaces*
        │
   game, services ──► core
        │
      i18n, asset_paths
```

- `core/` and `services/` never import pygame. They can be tested without a display.
- `controllers/` talk to `core`, `services` and `game` through small interfaces (`Speech`, `Feedback`, `Gestures`,
  `Enforcement`, `Navigation`...). Pages and the stage depend on those interfaces, never on a concrete controller.
- Nothing below `assembly/` imports `application`.

## How a frame happens

`Application.run` pumps pygame events into the `InputRouter` (one `EventHandler` per event type), calls `tick(dt)` on
every `Tickable` (session timers, speech cadence, camera, blocking, animations) and then draws:
`SceneStage` composes background scene → character → foreground → overlays at the pixel-art resolution, the current
`Page` draws its chalkboard and buttons on top, and `FramePresenter` scales the result by an integer factor to the
window. Frame rate is 30 fps focused, 12 unfocused, 2 minimised.

## Main abstractions

| Area | Classes | Extend it by... |
|---|---|---|
| Scenery | `Scene` (template method) → `OfficeScene`, `FieldScene`, `TrenchScene`, `ParadeScene`; `SceneRegistry`; `PerspectiveGrid` holds the vanishing-point maths | subclass `Scene`, register it for a `Theme` |
| Character | `Character` (state) + `CharacterPainter`; `Pose` and `Expression` ABCs with one class per pose/mood | add a `Pose` or `Expression` subclass and its enum member |
| Animations | `Animation` ABC (`update`, `draw`, `finished`) → poke, slam, curtain, title card, stamp, floating text | subclass `Animation` |
| Pages | `Page` ABC → main, mission, request, desertion, settings, calibration, board | subclass `Page`, add a `PageId` |
| Judge | `JudgeBackend` ABC → `ClaudeJudge`, `CodexJudge`, `LocalJudge`; `JudgeFactory` picks one from the settings | subclass `JudgeBackend` |
| Blocking | `HostsBackend` ABC → `PosixHelperBackend`, `WindowsDirectBackend`, `DryRunBackend`; `Blocker` applies it on a worker thread | subclass `HostsBackend` |
| Per-OS | `Notifier`, `Elevator`, `DesktopIntegration`, `MonitorProvider` ABCs, each with a factory that picks by platform | add a subclass and a factory branch |
| Settings | `Settings` (typed, validated), `SettingsStore`, `SettingsDraft`; the CONFIG rows are `SettingRow`s edited by `RowEditor`s | add a field and a row |

## Conventions

- One public class per file, named after the file. Constructor injection; no module-level state.
- Private attributes with read-only properties; Enums and dataclasses instead of dicts and strings.
- No `if/elif` ladders over names or types: use a class per case.
- Comments explain *why*, never *what*. English only.
- User-visible text is a translation key (see [TRANSLATING.md](TRANSLATING.md)).
- Pixel maths gets named constants and small value objects (`Point`, `Rgb`, `Anchor`, `Viewport`), never bare numbers.

## The root helper

`helper/hosts-helper` is deliberately **not** part of the package: it is one standalone script that runs as root
(Linux, macOS) and is installed to `/usr/local/libexec/tenhut/`. It never imports `tenhut`, never trusts environment
variables and validates every domain. On Windows the app itself writes the hosts file (it asks for administrator
rights), reusing the same script through `WindowsDirectBackend`. See [SECURITY.md](../SECURITY.md).

## Data on disk

| What | Linux | macOS | Windows |
|---|---|---|---|
| Settings (`config.json`) | `~/.config/tenhut` | `~/Library/Application Support/tenhut` | `%APPDATA%\tenhut` |
| Session, profile, request log | `~/.local/state/tenhut` | same as settings | `%LOCALAPPDATA%\tenhut` |
| Face model (camera builds) | `~/.local/share/tenhut` | same as settings | `%LOCALAPPDATA%\tenhut` |

`XDG_CONFIG_HOME`, `XDG_STATE_HOME` and `XDG_DATA_HOME` override these on every system. The tests and the screenshot
tool use that to stay away from your real data.
