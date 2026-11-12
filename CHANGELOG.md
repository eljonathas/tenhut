# Changelog

All notable changes are listed here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and the project uses [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [1.0.0] - 2026-11-12

First stable release.

### Added

- Aggressive pomodoro with a pixel-art general who watches you work and blocks distracting sites
  until every task of the mission is done.
- Site blocking through the hosts file: a root helper on Linux and macOS, administrator rights on Windows.
- Judge for access requests: Claude Code or Codex decide what to unblock and for how long, with an offline
  fallback when neither is installed.
- Campaign scenery that advances with your progress: HQ office, training grounds, front line and a victory parade.
- Optional camera surveillance (opt-in) that notices when you look down or away from the screen.
- Ranks earned with pomodoros and missions.
- Portuguese and English interface, following the system language.
- Responsive window with integer pixel scaling; a compact mini mode for a corner of the screen.
- Release builds for Linux (x86-64), Windows (x86-64) and macOS (Apple silicon), each with and without camera support.

### Platform status

- **Linux:** stable.
- **Windows and macOS:** beta. Built and tested by CI on each system, but not yet exercised on real hardware.
  Please report problems with details.
