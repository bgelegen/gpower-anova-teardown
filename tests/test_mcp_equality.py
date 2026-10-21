"""MCP tool result must equal the CLI JSON object, valid and invalid inputs alike."""
import asyncio
import json
import sys
from concurrent.futures import ThreadPoolExecutor

import pytest

pytest.importorskip("mcp")
from mcp import ClientSession, StdioServerParameters  # noqa: E402
from mcp.client.stdio import stdio_client  # noqa: E402

from gpower_clone.contract import FLAG_ALIASES, TEST_NAME  # noqa: E402
from helpers import run_cli  # noqa: E402

AP = dict(mode="a-priori", f=0.25, alpha=0.05, power=0.95, groups=3)
PH = dict(mode="post-hoc", f=0.25, alpha=0.05, total_n=60, groups=3)

CASES = [
    # valid a priori
    AP, {**AP, "groups": 2}, {**AP, "groups": 10}, {**AP, "groups": 7},
    {**AP, "f": 0.4, "power": 0.8}, {**AP, "f": 50}, {**AP, "f": 5},
    {**AP, "power": 0.05}, {**AP, "groups": 2.5}, {**AP, "groups": 2.4},
    {**AP, "alpha": 0.01, "power": 0.99}, {**AP, "digits": 2}, {**AP, "digits": 0},
    {**AP, "digits": 8}, {**AP, "mode": "apriori"}, {**AP, "mode": "a_priori"},
    {**AP, "f": "0.25", "alpha": "0.05", "power": "0.95", "groups": "3"},
    # valid post hoc
    PH, {**PH, "total_n": 61}, {**PH, "total_n": 4}, {**PH, "f": 0},
    {**PH, "total_n": 60.5}, {**PH, "mode": "posthoc"}, {**PH, "mode": "post_hoc"},
    {**PH, "f": 0.5, "total_n": 600}, {**PH, "f": 0.01, "alpha": 0.005, "total_n": 30},
    {**PH, "digits": 3},
    # invalid
    {**AP, "power": 0.03}, {**AP, "groups": 1}, {**AP, "groups": 1, "f": 0},
    {**AP, "f": 0}, {**AP, "f": 50.01}, {**AP, "alpha": 0}, {**AP, "alpha": 1},
    {**AP, "power": 1}, {**AP, "f": "abc"}, {**AP, "digits": 99},
    {**AP, "digits": "x"}, {**AP, "total_n": 60}, {**AP, "power": None},
    {**AP, "mode": None}, {**AP, "mode": "sensitivity"},
    {**PH, "f": -0.1}, {**PH, "total_n": 3}, {**PH, "total_n": 1},
    {**PH, "power": 0.9}, {**PH, "total_n": None}, {**PH, "groups": 0},
    {**PH, "alpha": 2},
]


def _attr(obj, snake, camel):
    """mcp 1.x uses camelCase result fields, mcp 2.x snake_case."""
    return getattr(obj, snake) if hasattr(obj, snake) else getattr(obj, camel)


def _id(i, case):
    return f"{i:02d}-" + ",".join(f"{k}={v}" for k, v in case.items() if k != "mode")[:60]


def cli_argv(case):
    argv = [FLAG_ALIASES["test"][0], TEST_NAME]
    for name, value in case.items():
        if value is not None:
            argv += [FLAG_ALIASES[name][0], str(value)]
    return argv


def cli_object(case):
    code, out, err = run_cli(cli_argv(case))
    assert code in (0, 2), out
    return code, out.strip(), err.strip()


async def _call_all(cases):
    params = StdioServerParameters(command=sys.executable,
                                   args=["-m", "gpower_clone.mcp_server"])
    out = []
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            assert [t.name for t in tools.tools] == ["anova_oneway"]
            for case in cases:
                # the tool's parameter is named n_total (task requirement)
                args = {("n_total" if k == "total_n" else k): v for k, v in case.items()}
                res = await session.call_tool("anova_oneway", args)
                out.append(res)
    return out


@pytest.fixture(scope="module")
def both():
    with ThreadPoolExecutor(max_workers=6) as pool:
        cli = list(pool.map(cli_object, CASES))
    mcp_results = asyncio.run(_call_all(CASES))
    return cli, mcp_results


def test_at_least_30_cases_mixed():
    assert len(CASES) >= 30
    assert any(c.get("power") == 0.03 for c in CASES)


def test_R14_warning_reaches_mcp_client(both):
    """Eval S08: the 'not a multiple' warning must be visible to the agent."""
    cli, results = both
    i = next(j for j, c in enumerate(CASES) if c.get("total_n") == 61)
    structured = _attr(results[i], "structured_content", "structuredContent")
    assert structured["warnings"] == [
        "The total sample size (61) is not a multiple of the number of groups (3). "
        "The analysis was based on the average group size."]


@pytest.mark.parametrize("i", range(len(CASES)), ids=[_id(i, c) for i, c in enumerate(CASES)])
def test_mcp_equals_cli(both, i):
    cli, results = both
    code, cli_text, cli_err = cli[i]
    res = results[i]
    assert not _attr(res, "is_error", "isError"), res.content
    cli_obj = json.loads(cli_text)
    if cli_err:  # CLI warning on stderr == MCP "warnings" field (last)
        cli_obj["warnings"] = cli_err.splitlines()
    structured = _attr(res, "structured_content", "structuredContent")
    assert structured == cli_obj, (CASES[i], structured, cli_obj)
    assert list(structured) == list(cli_obj)            # same field order
    text_obj = json.loads(res.content[0].text)
    assert text_obj == cli_obj
    assert ("error" in cli_obj) == (code == 2)
