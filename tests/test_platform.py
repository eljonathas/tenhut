import pytest

from fakes import FakeRunner
from tenhut.services.platform import (
    CommandError,
    CommandResult,
    DesktopFactory,
    ElevatorFactory,
    HelperInstaller,
    HelperLocator,
    HelperScripts,
    LinuxNotifier,
    MacNotifier,
    NoElevator,
    NotifierFactory,
    OperatingSystem,
    OsascriptElevator,
    PkexecElevator,
    ReadyRuntimeCheck,
    RootElevator,
    SystemIntegration,
    UnsupportedDesktop,
    WindowsNotifier,
)
from tenhut.services.platform.apple_script import AppleScript


@pytest.mark.parametrize(
    ("platform", "system"),
    [("linux", "LINUX"), ("darwin", "MACOS"), ("win32", "WINDOWS"), ("cygwin", "WINDOWS"), ("freebsd14", "LINUX")],
)
def test_operating_system_classification(platform, system):
    assert OperatingSystem.of(platform).name == system


def test_notifier_per_platform_and_commands():
    runner = FakeRunner()
    assert isinstance(NotifierFactory.create(OperatingSystem.LINUX, runner), LinuxNotifier)
    assert isinstance(NotifierFactory.create(OperatingSystem.MACOS, runner), MacNotifier)
    assert isinstance(NotifierFactory.create(OperatingSystem.WINDOWS, runner), WindowsNotifier)
    linux = LinuxNotifier(runner).build_command("T", "B", urgent=True)
    assert linux.argv[-4:] == ("critical", "T", "B") or linux.argv[3:5] == ("-u", "critical")
    assert LinuxNotifier(runner).build_command("T", "B").argv[4] == "normal"


def test_mac_notification_escapes_quotes_and_newlines():
    spec = MacNotifier(FakeRunner()).build_command('a "q"\nb', "body")
    assert spec.argv[0] == "osascript"
    assert '\\"q\\" b' in spec.argv[2]
    assert AppleScript.quote("x\\y") == '"x\\\\y"'


def test_windows_notification_passes_the_text_through_the_environment_only():
    spec = WindowsNotifier(FakeRunner()).build_command("My title", "My body")
    assert spec.extra_env == {"TENHUT_TITLE": "My title", "TENHUT_BODY": "My body"}
    assert "My title" not in " ".join(spec.argv)


def test_notify_launches_and_swallows_failures():
    runner = FakeRunner()
    LinuxNotifier(runner).notify("t", "b")
    assert len(runner.launched) == 1
    LinuxNotifier(FakeRunner(error=CommandError("no notify-send"))).notify("t", "b")


def test_elevator_per_platform():
    assert isinstance(ElevatorFactory.create(OperatingSystem.WINDOWS, False), NoElevator)
    assert isinstance(ElevatorFactory.create(OperatingSystem.LINUX, True), RootElevator)
    assert isinstance(ElevatorFactory.create(OperatingSystem.LINUX, False), PkexecElevator)
    assert isinstance(ElevatorFactory.create(OperatingSystem.MACOS, False), OsascriptElevator)


def test_osascript_elevator_wraps_the_script():
    spec = OsascriptElevator().command("echo hi")
    assert spec.argv[:2] == ("osascript", "-e") and "with administrator privileges" in spec.argv[2]
    assert NoElevator().command("x") is None
    assert RootElevator().command("echo hi").argv == ("/bin/sh", "-c", "echo hi")


def test_cancelled_elevation_is_recognised():
    assert PkexecElevator().cancelled(126, "")
    assert OsascriptElevator().cancelled(1, "user canceled. (-128)")
    assert not OsascriptElevator().cancelled(1, "other")


def test_install_script_is_built_from_validated_parts():
    script = HelperScripts.install("alice", "/opt/my helper/hosts-helper", OperatingSystem.LINUX)
    assert "alice ALL=(root) NOPASSWD: /usr/local/libexec/tenhut/hosts-helper" in script
    assert "'/opt/my helper/hosts-helper'" in script
    assert "-g wheel" in HelperScripts.install("alice", "/x", OperatingSystem.MACOS)
    with pytest.raises(ValueError):
        HelperScripts.install("bad user; rm -rf /", "/x", OperatingSystem.LINUX)


@pytest.mark.parametrize("name", ["alice", "_svc", "a-b_c", "user$"])
def test_valid_usernames(name):
    assert HelperScripts.valid_username(name)


@pytest.mark.parametrize("name", ["", "Alice", "a b", "a;b", "$x", "-x"])
def test_invalid_usernames(name):
    assert not HelperScripts.valid_username(name)


def make_installer(system, elevator, runner):
    return HelperInstaller(system, elevator, runner, runtime_check=ReadyRuntimeCheck(), locator=HelperLocator())


def test_install_runs_the_elevated_script():
    runner = FakeRunner()
    result = make_installer(OperatingSystem.LINUX, RootElevator(), runner).install(username="alice")
    assert result.ok and runner.ran[0].argv[:2] == ("/bin/sh", "-c")


def test_install_reports_a_failure_message():
    runner = FakeRunner(CommandResult(1, "", "boom\nlast line"))
    result = make_installer(OperatingSystem.LINUX, RootElevator(), runner).install(username="alice")
    assert not result.ok and result.message == "last line"


def test_install_on_windows_needs_admin_and_never_runs_anything():
    runner = FakeRunner()
    result = make_installer(OperatingSystem.WINDOWS, NoElevator(), runner).install()
    assert not result.ok and runner.ran == []
    assert make_installer(OperatingSystem.WINDOWS, NoElevator(), runner).uninstall().ok


def test_uninstall_runs_the_removal_script():
    runner = FakeRunner()
    assert make_installer(OperatingSystem.LINUX, RootElevator(), runner).uninstall().ok
    assert "rm -f /etc/sudoers.d/tenhut" in runner.ran[0].argv[2]


def test_desktop_integration_is_linux_only(tmp_path):
    runner = FakeRunner()
    assert isinstance(DesktopFactory.create(OperatingSystem.WINDOWS, runner), UnsupportedDesktop)
    assert DesktopFactory.create(OperatingSystem.MACOS, runner).install() == []
    from tenhut.services.platform import LinuxDesktop

    desktop = LinuxDesktop(tmp_path, runner)
    written = desktop.install()
    assert (tmp_path / "applications" / "tenhut.desktop").exists() and len(written) == 9
    desktop.uninstall()
    assert not (tmp_path / "applications" / "tenhut.desktop").exists()
    assert "StartupWMClass=tenhut" in desktop.desktop_entry()


def test_window_identity_sets_the_class_without_overriding():
    env = {"SDL_APP_NAME": "custom"}
    UnsupportedDesktop(env).window_identity()
    assert env["SDL_VIDEO_X11_WMCLASS"] == "tenhut" and env["SDL_APP_NAME"] == "custom"


def test_open_path_uses_the_platform_command():
    runner = FakeRunner()
    assert SystemIntegration(OperatingSystem.LINUX, runner).open_path("/tmp/x")
    assert SystemIntegration(OperatingSystem.MACOS, runner).open_command("/tmp/x").argv[0] == "open"
    assert SystemIntegration(OperatingSystem.WINDOWS, runner).open_command("x") is None
    assert runner.launched[0].argv == ("xdg-open", "/tmp/x")
