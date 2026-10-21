"""CLI contract tests; every case runs the CLI as a subprocess."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

from gpower_clone.contract import (DEFAULT_DIGITS, FLAG_ALIASES, MODE_ALIASES,
                                   OUTPUT_FIELDS, TEST_NAME)
from helpers import cli_args, cli_json, field, run_cli

ORDER = list(OUTPUT_FIELDS.values())


def apriori_args(**over):
    p = dict(test=TEST_NAME, mode="a-priori", f=0.25, alpha=0.05, power=0.95, groups=3)
    p.update(over)
    return {k: v for k, v in p.items() if v is not None}


def posthoc_args(**over):
    p = dict(test=TEST_NAME, mode="post-hoc", f=0.25, alpha=0.05, total_n=60, groups=3)
    p.update(over)
    return {k: v for k, v in p.items() if v is not None}


def test_apriori_contract_example_exact_line():
    code, out, err = run_cli(cli_args(**apriori_args()))
    assert code == 0 and err == ""
    obj = json.loads(out)
    assert out.strip() == json.dumps(obj, separators=(",", ":"))
    assert len(out.strip().splitlines()) == 1
    assert list(obj) == ORDER
    assert obj == {
        field("per_group"): 84, field("total_n"): 252, field("power"): 0.9515,
        field("critical"): 3.0321, field("df1"): 2, field("df2"): 249,
        field("ncp"): 15.75}


def test_posthoc_contract_example():
    code, obj, _ = cli_json(**posthoc_args())
    assert code == 0
    assert obj == {
        field("per_group"): 20, field("total_n"): 60, field("power"): 0.3744,
        field("critical"): 3.1588, field("df1"): 2, field("df2"): 57,
        field("ncp"): 3.75}


def test_field_order_both_modes():
    for args in (apriori_args(), posthoc_args()):
        assert list(cli_json(**args)[1]) == ORDER


def test_integer_fields_are_integers():
    obj = cli_json(**apriori_args())[1]
    for attr in ("total_n", "df1", "df2"):
        assert isinstance(obj[field(attr)], int)


@pytest.mark.parametrize("digits,expected", [(2, 0.95), (6, 0.951489), (0, 1)])
def test_digits(digits, expected):
    code, obj, _ = cli_json(**apriori_args(digits=digits))
    assert code == 0 and obj[field("power")] == expected
    assert obj[field("total_n")] == 252


def test_default_digits_is_four():
    obj = cli_json(**apriori_args())[1]
    assert len(str(obj[field("critical")]).split(".")[1]) <= DEFAULT_DIGITS


@pytest.mark.parametrize("digits", ["-1", "16", "x", "2.5"])
def test_digits_invalid(digits):
    code, obj, _ = cli_json(**apriori_args(digits=digits))
    assert code == 2 and list(obj) == ["error"]


def test_mode_aliases():
    base = cli_json(**apriori_args())[1]
    for canon, spellings in MODE_ALIASES.items():
        for sp in spellings:
            args = apriori_args(mode=sp) if canon == "a-priori" else posthoc_args(mode=sp)
            code, obj, _ = cli_json(**args)
            assert code == 0, sp
            if canon == "a-priori":
                assert obj == base


def test_flag_aliases_every_spelling():
    for name, flags in FLAG_ALIASES.items():
        if name in ("test", "mode", "digits"):
            continue
        mode_args = apriori_args() if name != "total_n" else posthoc_args()
        want = cli_json(**mode_args)[1]
        for flag in flags:
            for spelled in {flag, "--" + flag[2:].replace("-", "_")}:
                argv = []
                for n, v in mode_args.items():
                    argv += [spelled if n == name else FLAG_ALIASES[n][0], str(v)]
                code, out, _ = run_cli(argv)
                assert code == 0, (spelled, out)
                assert json.loads(out) == want, spelled


def test_equals_syntax_and_negative_values():
    code, out, _ = run_cli([FLAG_ALIASES["mode"][0] + "=post-hoc",
                            FLAG_ALIASES["f"][0] + "=0.25",
                            FLAG_ALIASES["alpha"][0], "0.05",
                            FLAG_ALIASES["total_n"][0], "60",
                            FLAG_ALIASES["groups"][0], "3"])
    assert code == 0
    code, obj, _ = cli_json(**posthoc_args(f=-0.1))
    assert code == 2 and obj["error"].endswith("(0, 50).")


def test_missing_test_flag_is_accepted_and_wrong_test_rejected():
    assert cli_json(**apriori_args(test=None))[0] == 0
    code, obj, _ = cli_json(**apriori_args(test="t2-indep"))
    assert code == 2 and "error" in obj


def test_invalid_input_json_error_and_exit_2():
    code, out, err = run_cli(cli_args(**apriori_args(power=0.03)))
    assert code == 2
    assert json.loads(out) == {"error": "Power must be greater than or equal to alpha."}
    assert out.strip() == '{"error":"Power must be greater than or equal to alpha."}'


def test_validation_order_single_message():
    code, obj, _ = cli_json(**apriori_args(groups=1, f=0))
    assert code == 2 and obj == {"error": "There must be at least 2 groups."}


def test_warning_on_stderr_exit_zero():
    code, out, err = run_cli(cli_args(**posthoc_args(total_n=61)))
    assert code == 0
    assert "not a multiple of" in err and len(err.strip().splitlines()) == 1
    assert "not a multiple of" not in out
    assert json.loads(out)[field("total_n")] == 61


def test_no_warning_stream_noise_on_success():
    assert run_cli(cli_args(**apriori_args()))[2] == ""


@pytest.mark.parametrize("extra", [["--tails", "2"], ["--ratio", "1"], ["--d", "0.5"]])
def test_foreign_flags_rejected(extra):
    code, out, _ = run_cli(cli_args(**apriori_args()) + extra)
    assert code == 2 and list(json.loads(out)) == ["error"]


def test_unused_flag_per_mode_rejected():
    assert cli_json(**apriori_args(total_n=60))[0] == 2
    assert cli_json(**posthoc_args(power=0.9))[0] == 2


def test_duplicate_parameter_rejected():
    argv = cli_args(**apriori_args())
    argv += [FLAG_ALIASES["groups"][1], "3"]
    code, out, _ = run_cli(argv)
    assert code == 2 and "Duplicate" in json.loads(out)["error"]


def test_missing_required_and_missing_mode():
    assert cli_json(**apriori_args(power=None))[0] == 2
    assert cli_json(**posthoc_args(total_n=None))[0] == 2
    assert cli_json(**apriori_args(mode=None))[0] == 2
    assert run_cli([])[0] == 2


def test_unknown_mode_and_bad_values():
    assert cli_json(**apriori_args(mode="sensitivity"))[0] == 2
    code, obj, _ = cli_json(**apriori_args(f="abc"))
    assert code == 2 and obj["error"] == "Input error (illegal character?)"
    code, out, _ = run_cli(["positional"])
    assert code == 2


def test_missing_flag_value():
    code, out, _ = run_cli([FLAG_ALIASES["mode"][0]])
    assert code == 2 and "error" in json.loads(out)


def test_fractional_groups_rounded_silently():
    code, out, err = run_cli(cli_args(**apriori_args(groups=2.5)))
    assert code == 0 and err == ""
    assert out == run_cli(cli_args(**apriori_args(groups=3)))[1]


def test_installed_console_scripts_exist():
    scripts = Path(sys.executable).parent
    names = ("gpower-clone", "gpower-clone-mcp")
    for n in names:
        assert (scripts / n).exists() or (scripts / f"{n}.exe").exists(), n
    exe = scripts / "gpower-clone.exe"
    if exe.exists():
        proc = subprocess.run([str(exe), *cli_args(**posthoc_args())],
                              capture_output=True, text=True)
        assert proc.returncode == 0 and json.loads(proc.stdout)[field("total_n")] == 60
