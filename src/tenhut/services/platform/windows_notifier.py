from __future__ import annotations

from .command_spec import CommandSpec
from .notifier import Notifier

# The PowerShell AUMID: the only one that makes a toast show up without a Start-menu shortcut.
TOAST_APP_ID = r"{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}\WindowsPowerShell\v1.0\powershell.exe"


class WindowsNotifier(Notifier):
    """Notifications as PowerShell toasts."""

    TOAST_SCRIPT = (
        "[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType=WindowsRuntime] | Out-Null;"
        "$x=[Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent('ToastText02');"
        "$t=$x.GetElementsByTagName('text');"
        "$t.Item(0).AppendChild($x.CreateTextNode($env:TENHUT_TITLE)) | Out-Null;"
        "$t.Item(1).AppendChild($x.CreateTextNode($env:TENHUT_BODY)) | Out-Null;"
        f"[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier('{TOAST_APP_ID}')"
        ".Show([Windows.UI.Notifications.ToastNotification]::new($x))"
    )

    def build_command(self, title: str, body: str, urgent: bool = False) -> CommandSpec:
        # title and body travel in environment variables so none of the text enters the script (no injection)
        argv = (
            "powershell",
            "-NoProfile",
            "-NonInteractive",
            "-WindowStyle",
            "Hidden",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            self.TOAST_SCRIPT,
        )
        return CommandSpec(argv, extra_env={"TENHUT_TITLE": title, "TENHUT_BODY": body})
