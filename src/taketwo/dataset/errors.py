"""Actionable errors shared by the dataset API and CLI."""

from typing import Any


class DatasetError(Exception):
    def __init__(self, code: str, message: str, recovery: str, affected: str | None = None):
        super().__init__(message)
        self.code = code
        self.recovery = recovery
        self.affected = affected

    def as_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "message": str(self),
            "recovery": self.recovery,
            "affected": self.affected,
        }
