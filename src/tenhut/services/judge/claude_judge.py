from __future__ import annotations

import json
import shutil

from ..platform import CommandError, CommandSpec, CommandTimeoutError
from .ai_judge import AiJudge
from .judge_error import JudgeError
from .judge_prompts import JudgePrompts
from .judge_timeout_error import JudgeTimeoutError


class ClaudeJudge(AiJudge):
    """Judges through `claude -p` with a JSON schema."""

    name_key = "judge.name.claude"

    def available(self) -> bool:
        return shutil.which(self.options.claude_binary) is not None

    def command(self, system: str, prompt: str) -> CommandSpec:
        binary = self.options.claude_binary
        argv = (
            shutil.which(binary) or binary,  # Windows: finds claude.cmd/.exe through PATHEXT
            "-p",
            "--model",
            self.options.claude_model,
            "--tools",
            "",
            "--no-session-persistence",
            "--output-format",
            "json",
            "--system-prompt",
            system,
            "--json-schema",
            json.dumps(JudgePrompts.SCHEMA),
        )
        return CommandSpec(argv, stdin_text=prompt, timeout=self.options.timeout_seconds, cwd=self._work_dir)

    def run(self, system: str, prompt: str) -> dict[str, object]:
        try:
            result = self._runner.run(self.command(system, prompt))
        except CommandTimeoutError as error:
            raise JudgeTimeoutError(str(error)) from error
        except CommandError as error:
            raise JudgeError(str(error)) from error
        try:
            return self._structured_output(json.loads(result.stdout))
        except json.JSONDecodeError as error:
            raise JudgeError(str(error)) from error

    @staticmethod
    def _structured_output(data: dict[str, object]) -> dict[str, object]:
        if data.get("is_error"):
            raise JudgeError(str(data.get("result", "claude error"))[:200])
        output = data.get("structured_output")
        return output if isinstance(output, dict) else json.loads(data.get("result") or "{}")
