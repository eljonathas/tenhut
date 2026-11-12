from __future__ import annotations

import json
import shutil
from pathlib import Path

from ..platform import CommandError, CommandSpec, CommandTimeoutError
from .ai_judge import AiJudge
from .judge_error import JudgeError
from .judge_prompts import JudgePrompts
from .judge_timeout_error import JudgeTimeoutError


class CodexJudge(AiJudge):
    """Judges through `codex exec` with an output schema."""

    name_key = "judge.name.codex"

    def available(self) -> bool:
        return shutil.which(self.options.codex_binary) is not None

    def command(self, schema_file: Path, answer_file: Path, stdin_text: str) -> CommandSpec:
        binary = self.options.codex_binary
        argv = [
            shutil.which(binary) or binary,
            "exec",
            "--skip-git-repo-check",
            "--sandbox",
            "read-only",
            "--output-schema",
            str(schema_file),
            "-o",
            str(answer_file),
        ]
        if self.options.codex_model:
            argv += ["-m", self.options.codex_model]
        argv.append("-")
        return CommandSpec(tuple(argv), stdin_text=stdin_text, timeout=self.options.timeout_seconds, cwd=self._work_dir)

    def run(self, system: str, prompt: str) -> dict[str, object]:
        folder = self._work_dir or Path(".")
        schema_file, answer_file = folder / "judge-schema.json", folder / "judge-answer.json"
        schema_file.write_text(json.dumps(JudgePrompts.SCHEMA), encoding="utf-8")
        answer_file.unlink(missing_ok=True)
        try:
            self._runner.run(self.command(schema_file, answer_file, f"{system}\n\n---\n\n{prompt}"))
        except CommandTimeoutError as error:
            raise JudgeTimeoutError(str(error)) from error
        except CommandError as error:
            raise JudgeError(str(error)) from error
        return self._read_answer(answer_file)

    @staticmethod
    def _read_answer(answer_file: Path) -> dict[str, object]:
        try:
            raw = answer_file.read_text(encoding="utf-8").strip()
            return json.loads(raw[raw.find("{") : raw.rfind("}") + 1])
        except (OSError, json.JSONDecodeError) as error:
            raise JudgeError(str(error)) from error
