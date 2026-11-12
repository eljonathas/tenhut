from __future__ import annotations


class Task:
    """One item of the mission."""

    __slots__ = ("_done", "_text")

    def __init__(self, text: str, done: bool = False) -> None:
        self._text = text
        self._done = done

    @property
    def text(self) -> str:
        return self._text

    @property
    def done(self) -> bool:
        return self._done

    def toggle(self) -> bool:
        self._done = not self._done
        return self._done

    def to_dict(self) -> dict[str, object]:
        return {"text": self._text, "done": self._done}

    @classmethod
    def from_dict(cls, data: object) -> Task:
        if not isinstance(data, dict) or not isinstance(data.get("text"), str):
            raise ValueError("invalid task")
        return cls(data["text"], bool(data.get("done", False)))

    def __repr__(self) -> str:
        return f"Task({self._text!r}, done={self._done})"
