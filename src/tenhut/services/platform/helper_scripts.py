from __future__ import annotations

import re
import shlex

from .operating_system import OperatingSystem


class HelperScripts:
    """Builds the shell scripts that install and remove the root helper and its sudo rule.

    The scripts contain only fixed text, paths escaped with `shlex.quote` and a user name validated
    by `USER_RE`: nothing from the user enters them unvalidated.
    """

    HELPER_DIR = "/usr/local/libexec/tenhut"
    HELPER_DEST = f"{HELPER_DIR}/hosts-helper"
    SUDOERS_DEST = "/etc/sudoers.d/tenhut"
    OLD_HELPER_DIR = "/usr/local/libexec/general-foco"
    OLD_HELPER_DEST = f"{OLD_HELPER_DIR}/hosts-helper"
    OLD_SUDOERS = "/etc/sudoers.d/general-foco"
    USER_RE = re.compile(r"^[a-z_][a-z0-9_-]*\$?$")
    PATH_RE = re.compile(r"/[A-Za-z0-9_./-]+")

    @classmethod
    def valid_username(cls, name: str) -> bool:
        return bool(cls.USER_RE.fullmatch(name or ""))

    @classmethod
    def sudoers_line(cls, user: str, helper: str | None = None) -> str:
        helper = helper or cls.HELPER_DEST
        if not cls.valid_username(user):
            raise ValueError(f"unsupported user name: {user!r}")
        if not cls.PATH_RE.fullmatch(helper):
            raise ValueError(f"invalid helper path: {helper!r}")
        return f"{user} ALL=(root) NOPASSWD: {helper}"

    @staticmethod
    def root_group(system: OperatingSystem) -> str:
        return "wheel" if system.is_mac else "root"

    @classmethod
    def install(cls, user: str, source: str, system: OperatingSystem) -> str:
        """One-line `sh` script (steps chained with &&) that installs the helper and the sudo rule."""
        group = cls.root_group(system)
        quote = shlex.quote
        steps = [
            f"rm -f {cls.OLD_SUDOERS} {cls.OLD_HELPER_DEST}",
            f"{{ rmdir {cls.OLD_HELPER_DIR} 2>/dev/null || true; }}",
            f"install -d -o root -g {group} -m 0755 {cls.HELPER_DIR}",
            f"install -o root -g {group} -m 0755 {quote(source)} {cls.HELPER_DEST}",
            f"{{ [ -d /etc/sudoers.d ] || install -d -o root -g {group} -m 0750 /etc/sudoers.d; }}",
            "T=$(mktemp /tmp/tenhut-sudoers.XXXXXX)",
            f"printf '%s\\n' {quote(cls.sudoers_line(user))} > \"$T\"",
            '{ visudo -cf "$T" >/dev/null || { rm -f "$T"; exit 1; }; }',
            f'install -o root -g {group} -m 0440 "$T" {cls.SUDOERS_DEST}',
            'rm -f "$T"',
        ]
        return " && ".join(steps)

    @classmethod
    def uninstall(cls) -> str:
        steps = [
            f"{{ [ -x {cls.HELPER_DEST} ] && {cls.HELPER_DEST} clear || true; }}",
            f"rm -f {cls.SUDOERS_DEST} {cls.HELPER_DEST} {cls.OLD_SUDOERS} {cls.OLD_HELPER_DEST}",
            f"{{ rmdir {cls.HELPER_DIR} 2>/dev/null || true; }}",
            f"{{ rmdir {cls.OLD_HELPER_DIR} 2>/dev/null || true; }}",
        ]
        return " && ".join(steps)
