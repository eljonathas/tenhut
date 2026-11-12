import pytest

from tenhut.cli import (
    CommandLine,
    InstallDesktopCommand,
    InstallHelperCommand,
    RunCommand,
    UninstallDesktopCommand,
    UninstallHelperCommand,
)


def pick(*arguments):
    return CommandLine(list(arguments)).command()


def test_without_flags_the_game_runs():
    command = pick()
    assert isinstance(command, RunCommand) and not command.dry_run


def test_dry_run_is_passed_to_the_game():
    command = pick("--dry-run")
    assert isinstance(command, RunCommand) and command.dry_run


@pytest.mark.parametrize(
    ("flag", "expected"),
    [
        ("--install-helper", InstallHelperCommand),
        ("--uninstall-helper", UninstallHelperCommand),
        ("--install-desktop", InstallDesktopCommand),
        ("--uninstall-desktop", UninstallDesktopCommand),
    ],
)
def test_each_flag_selects_its_command(flag, expected):
    assert isinstance(pick(flag), expected)


def test_helper_flags_win_over_desktop_flags_and_uninstall_over_install():
    assert isinstance(pick("--install-desktop", "--install-helper"), InstallHelperCommand)
    assert isinstance(pick("--install-helper", "--uninstall-helper"), UninstallHelperCommand)
    assert isinstance(pick("--uninstall-desktop", "--install-desktop"), InstallDesktopCommand)


def test_unknown_flags_are_rejected():
    with pytest.raises(SystemExit):
        pick("--nope")
