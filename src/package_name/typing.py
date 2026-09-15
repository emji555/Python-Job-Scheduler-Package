"""Shared typing helpers."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")
T = TypeVar("T")

JobCallable = Callable[..., Any]
JSONPrimitive = None | bool | int | float | str
JSONValue = JSONPrimitive | list["JSONValue"] | dict[str, "JSONValue"]

__all__ = ["JSONPrimitive", "JSONValue", "JobCallable", "P", "R", "T"]
