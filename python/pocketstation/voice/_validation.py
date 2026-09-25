"""Shared runtime validation for provider-neutral voice values."""

from __future__ import annotations

from math import isfinite

MAX_SAFE_INTEGER = (1 << 53) - 1


def require_boolean(name: str, value: object) -> None:
    if not isinstance(value, bool):
        raise TypeError(f"{name} must be a boolean")


def require_integer(
    name: str,
    value: object,
    *,
    minimum: int,
    maximum: int | None = None,
) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an integer")
    if value < minimum:
        if maximum is None:
            raise ValueError(f"{name} must be at least {minimum}")
        raise ValueError(f"{name} must be between {minimum} and {maximum}")
    if maximum is not None and value > maximum:
        raise ValueError(f"{name} must be between {minimum} and {maximum}")


def require_nonnegative_integer(name: str, value: object) -> None:
    require_integer(name, value, minimum=0)


def require_positive_integer(name: str, value: object) -> None:
    require_integer(name, value, minimum=1)


def require_optional_nonnegative_integer(name: str, value: object | None) -> None:
    if value is not None:
        require_nonnegative_integer(name, value)


def require_optional_positive_integer(name: str, value: object | None) -> None:
    if value is not None:
        require_positive_integer(name, value)


def require_nonempty(name: str, value: object) -> None:
    if not isinstance(value, str):
        raise TypeError(f"{name} must be a string")
    if not value.strip():
        raise ValueError(f"{name} must not be empty")


def require_optional_nonempty(name: str, value: object | None) -> None:
    if value is not None:
        require_nonempty(name, value)


def require_finite_number(
    name: str,
    value: object,
    *,
    minimum_exclusive: float,
    maximum_inclusive: float,
) -> None:
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not isfinite(value)
    ):
        raise TypeError(f"{name} must be a finite number")
    if not minimum_exclusive < value <= maximum_inclusive:
        raise ValueError(
            f"{name} must be greater than {minimum_exclusive:g} "
            f"and at most {maximum_inclusive:g}"
        )


def require_inclusive_number(
    name: str,
    value: object,
    *,
    minimum: float,
    maximum: float,
) -> None:
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not isfinite(value)
    ):
        raise TypeError(f"{name} must be a finite number")
    if not minimum <= value <= maximum:
        raise ValueError(f"{name} must be between {minimum:g} and {maximum:g}")
