"""stdio MCP server: one tool, no computation of its own."""
from __future__ import annotations

from typing import Any, Optional, Union

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:  # mcp >= 2 renamed FastMCP to MCPServer (same API)
    from mcp.server.mcpserver import MCPServer as FastMCP

from .cli import evaluate

mcp = FastMCP("gpower-clone")

Number = Union[float, int, str]


@mcp.tool()
def anova_oneway(
    mode: Optional[str] = None,
    f: Optional[Number] = None,
    alpha: Optional[Number] = None,
    power: Optional[Number] = None,
    groups: Optional[Number] = None,
    n_total: Optional[Number] = None,
    digits: Optional[Number] = None,
) -> dict[str, Any]:
    """One-way ANOVA (F test, fixed effects, omnibus) power analysis.

    mode: "a-priori" (needs f, alpha, power, groups) or "post-hoc"
    (needs f, alpha, n_total, groups). digits: decimals (default 4).
    Send every number as a JSON number with a decimal POINT (f=0.25, not "0,25");
    like G*Power, the tool rejects a decimal comma with "Input error (illegal character?)".
    Returns the same JSON object as the gpower-clone CLI, or {"error": ...}.
    If the CLI would print a warning to stderr (e.g. the total sample size is
    not a multiple of the number of groups), the warning lines are returned
    in an extra trailing "warnings" field so that the calling agent sees them.
    """
    payload, warnings, _code = evaluate({
        "mode": mode, "f": f, "alpha": alpha, "power": power,
        "groups": groups, "total_n": n_total, "digits": digits,
    })
    if warnings:
        # stderr of an MCP stdio server never reaches the agent (see eval S08)
        payload = {**payload, "warnings": list(warnings)}
    return payload


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
