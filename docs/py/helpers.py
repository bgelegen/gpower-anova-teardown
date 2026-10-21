"""Shared test helpers: CLI runner and oracle CSV comparison."""
from __future__ import annotations

import csv
import json
import os
import re
import subprocess
import sys
from pathlib import Path

from gpower_clone import engine
from gpower_clone.contract import FLAG_ALIASES, MODE_ALIASES, OUTPUT_FIELDS
from gpower_clone.display import format_fraction, format_integer

ROOT = Path(__file__).resolve().parent.parent


def oracle_dir() -> Path:
    env = os.environ.get("ORACLE_DIR")
    return Path(env) if env else ROOT / "oracle"


def read_csv(name: str) -> list[dict]:
    path = oracle_dir() / name
    if not path.is_file():
        return []
    with open(path, newline="", encoding="utf-8-sig") as fh:
        lines = fh.read().splitlines()
    if not lines:
        return []
    delim = ";" if lines[0].count(";") > lines[0].count(",") else ","
    return list(csv.DictReader(lines, delimiter=delim))


# ---------------------------------------------------------------- CLI

def cli_args(**params) -> list[str]:
    """Canonical parameter name -> value, rendered with the first contract flag."""
    args = []
    for name, value in params.items():
        args += [FLAG_ALIASES[name][0], str(value)]
    return args


def run_cli(args: list[str]):
    proc = subprocess.run([sys.executable, "-m", "gpower_clone.cli", *args],
                          capture_output=True, text=True, timeout=300)
    return proc.returncode, proc.stdout, proc.stderr


def cli_json(**params):
    code, out, err = run_cli(cli_args(**params))
    return code, json.loads(out, object_pairs_hook=dict), err


def field(attr: str) -> str:
    """Public output field of an engine result attribute."""
    return OUTPUT_FIELDS[attr]


# ---------------------------------------------------------------- oracle

def norm(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def strip_note(text: str) -> str:
    return norm(re.sub(r"^\s*Please note:?", "", text or "", flags=re.I))


def canonical_mode(text: str) -> str:
    t = text.strip().lower()
    for mode, spellings in MODE_ALIASES.items():
        if t in spellings:
            return mode
    raise ValueError(f"unknown oracle mode {text!r}")


def blank(v) -> bool:
    return v is None or str(v).strip() == ""


def engine_inputs(row: dict) -> dict:
    kw = dict(mode=canonical_mode(row["mode"]), f=row["f"], alpha=row["alpha"],
              groups=row["groups"])
    if not blank(row.get("power")):
        kw["power"] = row["power"]
    if not blank(row.get("n_total")):
        kw["total_n"] = row["n_total"]
    return kw


def compare_gui_row(row: dict) -> list[str]:
    """Mismatches between the engine and one G*Power GUI vector (empty = ok)."""
    vid = row.get("id", "?")
    bad = []
    mesaj = row.get("gp_mesaj", "")
    is_note = norm(mesaj).lower().startswith("please note")
    expects_error = blank(row.get("gp_n_total")) and not blank(mesaj) and not is_note
    try:
        res = engine.calculate(**engine_inputs(row))
    except engine.GPowerError as exc:
        if not expects_error:
            return [f"{vid}: engine error {str(exc)!r} but G*Power gave a result"]
        if norm(str(exc)) != norm(mesaj):
            bad.append(f"{vid}: message {norm(str(exc))!r} != {norm(mesaj)!r}")
        return bad
    if expects_error:
        return [f"{vid}: G*Power error {norm(mesaj)!r} but engine returned a result"]
    warn = " ".join(res.warnings)
    if is_note:
        if strip_note(warn) != strip_note(mesaj):
            bad.append(f"{vid}: warning {strip_note(warn)!r} != {strip_note(mesaj)!r}")
    elif warn:
        bad.append(f"{vid}: unexpected warning {norm(warn)!r}")
    shown = {
        "gp_n_total": format_integer(res.total_n),
        "gp_df1": format_integer(res.df1),
        "gp_df2": format_integer(res.df2),
        "gp_ncp": format_fraction(res.ncp),
        "gp_critical": format_fraction(res.critical),
        "gp_actual_power": format_fraction(res.power),
    }
    for col, text in shown.items():
        want = row.get(col)
        if not blank(want) and want.strip() != text:
            bad.append(f"{vid}: {col} engine {text!r} != G*Power {want.strip()!r}")
    k = engine._round_half_up(float(row["groups"]))
    if res.per_group * k != res.total_n:
        bad.append(f"{vid}: n_per_group inconsistent with n_total")
    return bad


def assert_vector(vid: str) -> None:
    """Gherkin helper: compare one oracle vector if the oracle is present."""
    for row in read_csv("gpower_gui_vectors.csv"):
        if row.get("id", "").strip().upper() == vid.upper():
            bad = compare_gui_row(row)
            assert not bad, "; ".join(bad)
