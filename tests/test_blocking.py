import time

import pytest

from fakes import FakeBackend, FakeClock, FakeRunner
from tenhut.core import BlockGroup, BlockList, SystemClock
from tenhut.services.blocking import (
    Blocker,
    DryRunBackend,
    HostsBackendFactory,
    PosixHelperBackend,
    ProcessKiller,
    WindowsDirectBackend,
)
from tenhut.services.platform import CommandResult, HelperLocator, OperatingSystem, ReadyRuntimeCheck


def wait_until(condition, timeout=5.0):
    end = time.time() + timeout
    while time.time() < end:
        if condition():
            return True
        time.sleep(0.02)
    return False


def test_root_domains_cover_www_and_m_variants():
    assert BlockList.expand("Reddit.com") == ["reddit.com", "www.reddit.com", "m.reddit.com"]
    assert BlockList.expand("old.reddit.com") == ["old.reddit.com"]
    assert BlockList.expand("  ") == []


def test_block_list_domains_and_apps():
    groups = [BlockGroup("A", ("a.com",), ("a-app",)), BlockGroup("B", ("b.org", "x.b.org"))]
    block_list = BlockList(groups)
    assert block_list.domains_for({"A", "B"}) == [
        "a.com",
        "b.org",
        "m.a.com",
        "m.b.org",
        "www.a.com",
        "www.b.org",
        "x.b.org",
    ]
    assert block_list.domains_for({"missing"}) == []
    assert block_list.apps_for({"A", "B"}) == ["a-app"]
    assert block_list.names == ["A", "B"]


def test_factory_picks_the_backend_for_the_platform():
    factory = HostsBackendFactory(FakeRunner(), SystemClock())
    assert isinstance(factory.create(OperatingSystem.LINUX), PosixHelperBackend)
    assert isinstance(factory.create(OperatingSystem.MACOS), PosixHelperBackend)
    assert isinstance(factory.create(OperatingSystem.WINDOWS), WindowsDirectBackend)
    for system in OperatingSystem:
        assert isinstance(factory.create(system, dry_run=True), DryRunBackend)


def test_dry_run_backend_only_logs():
    lines = []
    backend = DryRunBackend(lines.append)
    backend.apply(["a.com"])
    backend.clear()
    assert lines == ["[dry-run] blocking 1 domains", "[dry-run] blocking 0 domains"] and backend.available()


class StubLocator(HelperLocator):
    def __init__(self, path):
        super().__init__()
        self.path = path

    def installed_path(self):
        return self.path


def test_posix_backend_runs_sudo_with_the_domains(tmp_path):
    helper = tmp_path / "hosts-helper"
    helper.write_text("")
    runner = FakeRunner()
    backend = PosixHelperBackend(
        OperatingSystem.LINUX,
        runner,
        locator=StubLocator(str(helper)),
        runtime_check=ReadyRuntimeCheck(),
        clock=FakeClock(),
    )
    assert backend.available() and backend.status_message() == ""
    backend.apply(["a.com", "b.com"])
    backend.apply([])
    assert runner.ran[0].argv == ("sudo", "-n", str(helper), "apply") and runner.ran[0].stdin_text == "a.com\nb.com"
    assert runner.ran[1].argv[-1] == "clear"


def test_posix_backend_without_the_helper_explains_how_to_install(tmp_path):
    backend = PosixHelperBackend(
        OperatingSystem.LINUX,
        FakeRunner(),
        locator=StubLocator(str(tmp_path / "nope")),
        runtime_check=ReadyRuntimeCheck(),
        clock=FakeClock(),
    )
    assert not backend.available() and backend.status_message()


def test_posix_backend_translates_a_sudo_password_request(tmp_path):
    from tenhut.services.blocking import HostsError

    helper = tmp_path / "h"
    helper.write_text("")
    runner = FakeRunner(CommandResult(1, "", "sudo: a password is required"))
    backend = PosixHelperBackend(
        OperatingSystem.LINUX,
        runner,
        locator=StubLocator(str(helper)),
        runtime_check=ReadyRuntimeCheck(),
        clock=FakeClock(),
    )
    with pytest.raises(HostsError):
        backend.apply(["a.com"])


def test_blocker_applies_asynchronously_and_deduplicates():
    backend = FakeBackend()
    blocker = Blocker(backend, SystemClock())
    blocker.apply(["a.com"])
    blocker.apply(["a.com"])
    assert wait_until(lambda: blocker.applied == ["a.com"])
    time.sleep(0.2)
    assert backend.calls == [["a.com"]]
    blocker.clear()
    assert wait_until(lambda: blocker.applied == [])


def test_blocker_retries_after_a_failure():
    backend = FakeBackend(failures=1)
    blocker = Blocker(backend, SystemClock(), retry_seconds=0.1)
    blocker.apply(["a.com"])
    assert wait_until(lambda: blocker.last_error == "boom")
    assert wait_until(lambda: blocker.applied == ["a.com"], timeout=6)
    assert len(backend.calls) == 2 and blocker.last_error == ""


def test_blocker_retry_now_skips_the_wait():
    backend = FakeBackend(failures=1)
    blocker = Blocker(backend, SystemClock(), retry_seconds=3600)
    blocker.apply(["a.com"])
    assert wait_until(lambda: blocker.last_error == "boom")
    blocker.retry_now()
    assert wait_until(lambda: blocker.applied == ["a.com"])


def test_blocker_apply_now_is_synchronous_and_reports_status():
    backend = FakeBackend()
    blocker = Blocker(backend, SystemClock())
    assert blocker.apply_now(["x.com"]) is True and backend.calls == [["x.com"]]
    backend.is_available = False
    assert blocker.helper_installed() is False and blocker.helper_msg == "not installed"
    failing = Blocker(FakeBackend(failures=1), SystemClock())
    assert failing.apply_now(["x.com"]) is False and failing.last_error == "boom"


class FakeProcess:
    def __init__(self, pid, name, user="me", dies=True):
        self.pid, self._name, self._user, self.terminated = pid, name, user, False
        self._dies = dies

    def name(self):
        return self._name

    def username(self):
        return self._user

    def terminate(self):
        self.terminated = True


class FakeSource:
    def __init__(self, processes):
        self._processes = processes

    def processes(self):
        return self._processes

    def own_pid(self):
        return 1

    def own_username(self):
        return "me"


def test_process_killer_closes_matching_processes_of_the_user_only():
    mine, theirs, me = FakeProcess(2, "Discord.EXE"), FakeProcess(3, "discord", user="root"), FakeProcess(1, "discord")
    other = FakeProcess(4, "firefox")
    killer = ProcessKiller(FakeSource([mine, theirs, me, other]))
    assert killer.kill(["discord", ""]) == ["discord"]
    assert mine.terminated and not theirs.terminated and not me.terminated and not other.terminated


def test_process_killer_with_nothing_to_kill():
    assert ProcessKiller(FakeSource([FakeProcess(2, "x")])).kill([]) == []
    assert ProcessKiller.normalize("Steam.EXE ") == "steam"
