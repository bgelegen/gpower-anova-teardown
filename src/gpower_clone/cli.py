"""Command line adapter (CONTRACT.md). ``evaluate`` is shared with the MCP server."""
from __future__ import annotations

import json
import sys
from typing import Any, Mapping, Sequence

from . import engine
from .contract import (DEFAULT_DIGITS, FLAG_ALIASES, INTEGER_FIELDS,
                       MODE_ALIASES, MODE_PARAMS, OUTPUT_FIELDS, TEST_ALIASES, TEST_NAME)

EXIT_OK, EXIT_INTERNAL, EXIT_INVALID = 0, 1, 2
MAX_DIGITS = 15

_FLAG_TO_NAME = {
    flag.replace("_", "-"): name
    for name, flags in FLAG_ALIASES.items() for flag in flags
}


def _flag(name: str) -> str:
    return FLAG_ALIASES[name][0]


class InvalidInput(ValueError):
    pass


def _canonical_mode(value: Any) -> str:
    text = str(value).strip().lower() if value is not None else ""
    for mode, spellings in MODE_ALIASES.items():
        if text in spellings:
            return mode
    raise InvalidInput(f"Unknown mode: {value}")


def _digits(value: Any) -> int:
    try:
        if isinstance(value, bool):
            raise ValueError
        x = float(value)
        if x != int(x) or not 0 <= x <= MAX_DIGITS:
            raise ValueError
    except (TypeError, ValueError, OverflowError):
        raise InvalidInput(f"{_flag('digits')} must be an integer "
                           f"between 0 and {MAX_DIGITS}.") from None
    return int(x)


def format_payload(result: engine.Result, digits: int) -> dict:
    payload = {}
    for attr, field in OUTPUT_FIELDS.items():
        value = getattr(result, attr)
        if attr in INTEGER_FIELDS:
            payload[field] = int(value)
        else:
            r = round(value, digits)
            # digits=0 and whole-valued per-group sizes are written as integers
            whole = digits == 0 or (attr == "per_group" and r == int(r))
            payload[field] = int(r) if whole else r
    return payload


def evaluate(raw: Mapping[str, Any]) -> tuple[dict, list[str], int]:
    """raw: canonical parameter name -> value (None = not given).

    Returns (payload, warnings, exit_code); payload is the JSON object.
    """
    try:
        given = {k: v for k, v in raw.items() if v is not None}
        if str(given.get("test", TEST_NAME)).strip().lower().replace("_", "-") not in TEST_ALIASES:
            raise InvalidInput(f"Unsupported test: {given['test']}")
        if "mode" not in given:
            raise InvalidInput(f"Missing required parameter: {_flag('mode')}")
        mode = _canonical_mode(given["mode"])
        spec = MODE_PARAMS[mode]
        allowed = {"test", "mode", *spec["required"], *spec["optional"]}
        for name in FLAG_ALIASES:
            if name in given and name not in allowed:
                raise InvalidInput("Parameter not applicable to this mode: "
                                   f"{_flag(name)}")
        for name in spec["required"]:
            if name not in given:
                raise InvalidInput(f"Missing required parameter: {_flag(name)}")
        digits = _digits(given.get("digits", DEFAULT_DIGITS))
        result = engine.calculate(
            mode, given["f"], given["alpha"], given["groups"],
            power=given.get("power"), total_n=given.get("total_n"))
        return format_payload(result, digits), list(result.warnings), EXIT_OK
    except (InvalidInput, engine.GPowerError) as exc:
        return {"error": str(exc)}, [], EXIT_INVALID
    except Exception as exc:  # noqa: BLE001 - contract: internal errors -> exit 1
        return {"error": f"internal: {exc}"}, [], EXIT_INTERNAL


def parse_args(argv: Sequence[str]) -> dict:
    raw: dict[str, str] = {}
    i = 0
    while i < len(argv):
        token = argv[i]
        i += 1
        if not token.startswith("--"):
            raise InvalidInput(f"Unexpected argument: {token}")
        flag, eq, value = token.partition("=")
        name = _FLAG_TO_NAME.get(flag.replace("_", "-"))
        if name is None:
            raise InvalidInput(f"Unknown parameter: {flag}")
        if name in raw:
            raise InvalidInput(f"Duplicate parameter: {_flag(name)}")
        if not eq:
            if i >= len(argv):
                raise InvalidInput(f"Missing value for parameter: {flag}")
            value = argv[i]
            i += 1
        raw[name] = value
    return raw


def emit(payload: dict, warnings: Sequence[str], code: int) -> int:
    sys.stdout.write(json.dumps(payload, separators=(",", ":")) + "\n")
    sys.stdout.flush()
    for w in warnings:
        sys.stderr.write(w + "\n")
    return code


def main(argv: Sequence[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    try:
        raw = parse_args(args)
    except InvalidInput as exc:
        return emit({"error": str(exc)}, [], EXIT_INVALID)
    return emit(*evaluate(raw))


if __name__ == "__main__":
    sys.exit(main())
