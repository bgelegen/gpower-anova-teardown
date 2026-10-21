"""AI ajanı değerlendirmesi: Türkçe klinik soru → MCP çağrısı → yanıt.

Ajan = Claude Code (başsız, `claude -p`). Tek aracı bu repodaki MCP sunucusudur
(`gpower-clone-mcp`); yerleşik araçların hepsi kapalıdır (`--tools ""`), yani
ajanın kod çalıştırıp kendi hesabını yapma imkânı yoktur.

Her soru iki kez sorulur:
  mcp : ajan anova_oneway aracını çağırır, sayıları araçtan alır.
  gui : aynı soru, G*Power penceresinin ekran görüntüsüyle (oracle/screenshots)
        yanıtlanır; ajan yalnızca Read aracıyla görüntüyü okuyabilir.
İki koşunun token kullanımı Claude Code'un kendi `usage` alanından okunur
(ölçüm; tahmin değil).

Çıktılar: eval/logs/<id>-<kol>.jsonl (araç çağrıları dahil tam akış),
          eval/results.json, eval/RESULTS.md

Kullanım (repo kökünde, Windows):
  <venv>\\Scripts\\python eval\\agent_eval.py [--model haiku] [--only S01,S04]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVAL = ROOT / "eval"
OUT = Path(os.environ["EVAL_OUT"]) if os.environ.get("EVAL_OUT") else EVAL  # sonuç klasörü
LOGS = OUT / "logs"
TOOL = "mcp__gpower__anova_oneway"
# Bazı ortamlar (ör. bulut çalışma alanı) --strict-mcp-config'e rağmen kendi MCP sunucularını
# ekler; ajanın bağlamında yalnızca anova_oneway kalsın diye bunlar açıkça yasaklanır.
EXTRA_DENY = ["--disallowedTools", "mcp__claude-in-chrome"]

SYSTEM = (
    "Sen klinik araştırmacılara örneklem büyüklüğü ve istatistiksel güç konusunda "
    "yardım eden bir asistansın. Hiçbir sayısal işlem yapma: hesaplama, yuvarlama, "
    "yüzdeye çevirme, bölme, tahmin yok. Her sayıyı anova_oneway aracından al ve "
    "aracın döndürdüğü değeri aynen, tüm basamaklarıyla yaz. 'Yaklaşık', yüzde (%) ya da "
    "kısaltılmış sayı (ör. 0,3744 yerine 0,37 veya %37) YAZMA; yorum cümlelerinde de yalnızca "
    "araçtan gelen sayıyı aynen kullan. Kullanıcının verdiği değerleri (grup sayısı "
    "2'den küçük olsa bile) olduğu gibi araca ver; geçerliliği araç denetler. "
    "Araç sonucunda warnings alanı varsa uyarıyı mutlaka Türkçe aktar; error alanı "
    "varsa hatayı Türkçe açıkla. Yalnızca tek yönlü ANOVA (F testi, sabit etkiler, "
    "omnibus) desteklenir; başka bir test sorulursa desteklenmediğini söyle ve aracı "
    "çağırma. Kısa ve Türkçe yanıt ver."
)
SYSTEM_GUI = (
    "Sen klinik araştırmacılara yardım eden bir asistansın. Hesap yapma; yalnızca "
    "verilen G*Power ekran görüntüsünde yazan değerleri oku ve aktar. Kısa ve "
    "Türkçe yanıt ver."
)


def claude_exe() -> str:
    exe = shutil.which("claude")
    if exe:
        return exe
    cand = Path(os.environ.get("USERPROFILE", "")) / ".local" / "bin" / "claude.exe"
    return str(cand)


def venv_scripts() -> Path:
    """Sanal ortam: GPOWER_VENV, yoksa %USERPROFILE%\\YZM301-araclar\\venv-gpower, yoksa .venv."""
    sub = "Scripts" if os.name == "nt" else "bin"
    cands = [os.environ.get("GPOWER_VENV", ""),
             str(Path(os.environ.get("USERPROFILE", "~")) / "YZM301-araclar" / "venv-gpower"),
             str(ROOT / ".venv")]
    for c in cands:
        if c and (Path(c) / sub).exists():
            return Path(c) / sub
    return Path(sys.executable).parent


def mcp_config() -> Path:
    scripts = venv_scripts()
    server = scripts / ("gpower-clone-mcp.exe" if os.name == "nt" else "gpower-clone-mcp")
    cfg = {"mcpServers": {"gpower": {"command": str(server), "args": []}}}
    path = EVAL / "agent-mcp.json"
    path.write_text(json.dumps(cfg, indent=1), encoding="utf-8")
    return path


def run(prompt: str, args: list[str], log: Path) -> list[dict]:
    cmd = [claude_exe(), "-p", prompt, *args, "--output-format", "stream-json",
           "--verbose", "--no-session-persistence", "--disable-slash-commands"]
    t0 = time.time()
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=600)
    log.write_text(proc.stdout + ("\n#STDERR\n" + proc.stderr if proc.stderr else ""),
                   encoding="utf-8")
    events = []
    for line in proc.stdout.splitlines():
        line = line.strip()
        if line.startswith("{"):
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    events.append({"type": "_wall", "seconds": round(time.time() - t0, 1)})
    return events


def load(log: Path) -> list[dict]:
    out = []
    for line in log.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("{"):
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return out


def summarize(events: list[dict]) -> dict:
    calls, results, texts = [], [], []
    usage, cost, turns = {}, None, None
    for e in events:
        if e.get("type") == "assistant":
            for c in e["message"].get("content", []):
                if c.get("type") == "tool_use":
                    calls.append({"name": c["name"], "input": c.get("input", {})})
                elif c.get("type") == "text":
                    texts.append(c["text"])
        elif e.get("type") == "user":
            for c in e["message"].get("content", []):
                if isinstance(c, dict) and c.get("type") == "tool_result":
                    content = c.get("content")
                    if isinstance(content, list):
                        content = "".join(x.get("text", "") for x in content if isinstance(x, dict))
                    results.append(str(content))
        elif e.get("type") == "result":
            usage = e.get("usage") or {}
            cost = e.get("total_cost_usd")
            turns = e.get("num_turns")
            if e.get("result"):
                texts.append(e["result"])
    final = texts[-1] if texts else ""
    tok_in = sum(usage.get(k, 0) or 0 for k in
                 ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"))
    return {"calls": calls, "results": results, "final": final, "turns": turns,
            "cost_usd": cost, "usage": usage, "tokens_in": tok_in,
            "tokens_out": usage.get("output_tokens", 0) or 0}


NUM = re.compile(r"(?<![\w.,])\d+(?:[.,]\d+)?")


def numbers(text: str) -> set[str]:
    out = set()
    for m in NUM.findall(text):
        v = m.replace(",", ".")
        try:
            f = float(v)
        except ValueError:
            continue
        out.add(f"{f:g}")
    return out


def grade(q: dict, s: dict) -> dict:
    calls = [c for c in s["calls"] if c["name"] == TOOL]
    exp, ok = q["beklenen"], q["dogru"]
    checks = {}
    if exp is None:
        checks["arac_cagrilmadi"] = not calls
        checks["desteklenmiyor_dedi"] = bool(re.search(r"destekle|kapsam|yaln[ıi]zca", s["final"], re.I))
    else:
        checks["arac_cagrildi"] = bool(calls)
        if calls:
            inp = calls[0]["input"]
            same = True
            for k, v in exp.items():
                got = inp.get(k)
                if k == "mode":
                    same &= str(got).replace("_", "-").lower() in (v, v.replace("-", ""))
                else:
                    try:
                        same &= abs(float(got) - float(v)) < 1e-9
                    except (TypeError, ValueError):
                        same = False
            checks["parametreler_dogru"] = same
        if ok.get("uyari"):
            checks["uyari_aktarildi"] = bool(re.search(r"kat[ıi]|multiple|ortalama|average|b[öo]l[üu]nm", s["final"], re.I))
        if "error" in ok:
            checks["hata_aktarildi"] = any(ok["error"] in r for r in s["results"]) and bool(
                re.search(r"grup|en az", s["final"], re.I))
        else:
            got = numbers(s["final"])
            for k, v in ok.items():
                if k == "uyari":
                    continue
                checks[f"yanitta_{k}"] = f"{float(v):g}" in got or f"{float(v) * 100:g}" in got
        # ajan hesap yapmadı mı: yanıttaki her sayı ya soruda ya araç çıktısında geçmeli
        allowed = numbers(q["soru"]) | set().union(*[numbers(r) for r in s["results"]] or [set()])
        allowed |= {f"{float(x) / 100:g}" for x in numbers(q["soru"]) if float(x) > 1}  # %95 -> 0.95
        allowed |= {f"{float(x) * 100:g}" for x in list(allowed) if float(x) < 1}  # yüzde yazımı
        allowed |= {f"{x:g}" for x in range(0, 11)}  # madde numaraları
        allowed |= {"80", "0.8", "90", "0.9"}  # alan sabiti: geleneksel güç eşikleri (hesap değil)
        extra = sorted(numbers(s["final"]) - allowed)
        checks["hesap_yapmadi"] = not extra
        if extra:
            checks["_kaynaksiz_sayilar"] = extra
    passed = all(v for k, v in checks.items() if not k.startswith("_"))
    return {"gecti": passed, "kontroller": checks}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="haiku")
    ap.add_argument("--only", default="")
    ap.add_argument("--skip-gui", action="store_true")
    ap.add_argument("--regrade", action="store_true",
                    help="ajanı çalıştırma; eval/logs içindeki kayıtları yeniden puanla")
    a = ap.parse_args()
    LOGS.mkdir(parents=True, exist_ok=True)
    qs = json.loads((EVAL / "questions.json").read_text(encoding="utf-8"))
    if a.only:
        keep = set(a.only.split(","))
        qs = [q for q in qs if q["id"] in keep]
    cfg = None if a.regrade else mcp_config()
    rows = []
    for q in qs:
        print(f"[{q['id']}] mcp ...", flush=True)
        ev = load(LOGS / f"{q['id']}-mcp.jsonl") if a.regrade else run(q["soru"], ["--model", a.model, "--strict-mcp-config", "--mcp-config", str(cfg),
                             "--tools", "", "--allowedTools", TOOL, *EXTRA_DENY,
                             "--append-system-prompt", SYSTEM], LOGS / f"{q['id']}-mcp.jsonl")
        s = summarize(ev)
        g = grade(q, s)
        row = {"id": q["id"], "soru": q["soru"], "oracle": q["oracle"], "mcp": s, "degerlendirme": g}
        if q["oracle"] and not a.skip_gui:
            shot = f"oracle/screenshots/{q['oracle']}.png"
            print(f"[{q['id']}] gui ...", flush=True)
            prompt = (q["soru"] + "\n\nYanıt için yalnızca şu G*Power ekran görüntüsünü kullan "
                      f"(Read aracıyla oku): {shot}")
            evg = load(LOGS / f"{q['id']}-gui.jsonl") if a.regrade else run(prompt, ["--model", a.model, "--strict-mcp-config", "--mcp-config",
                               str(EVAL / "bos-mcp.json"), "--tools", "Read", "--allowedTools", "Read", *EXTRA_DENY,
                               "--append-system-prompt", SYSTEM_GUI], LOGS / f"{q['id']}-gui.jsonl")
            row["gui"] = summarize(evg)
        rows.append(row)
        print(f"[{q['id']}] {'GEÇTİ' if g['gecti'] else 'KALDI'} {g['kontroller']}", flush=True)
    (OUT / "results.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    write_md(rows, a.model)
    return 0


def write_md(rows: list[dict], model: str) -> None:
    lines = ["# Ajan değerlendirmesi", "",
             f"Model: `{model}` (Claude Code başsız). Ajanın tek aracı `anova_oneway` MCP aracı; "
             "yerleşik araçlar kapalı (`--tools \"\"`). Token değerleri Claude Code'un `usage` "
             "alanından ölçüldü (girdi = input + cache_creation + cache_read).", "",
             "| Soru | Oracle | Sonuç | MCP çağrısı | MCP girdi tok. | MCP çıktı tok. | GUI girdi tok. | GUI çıktı tok. |",
             "|------|--------|-------|-------------|---------------:|---------------:|---------------:|---------------:|"]
    tot = {"mi": 0, "mo": 0, "gi": 0, "go": 0, "n": 0}
    for r in rows:
        m, g = r["mcp"], r.get("gui")
        call = json.dumps(m["calls"][0]["input"], ensure_ascii=False) if m["calls"] else "—"
        lines.append(f"| {r['id']} | {r['oracle'] or '—'} | {'✅' if r['degerlendirme']['gecti'] else '❌'} | "
                     f"`{call}` | {m['tokens_in']} | {m['tokens_out']} | "
                     f"{g['tokens_in'] if g else '—'} | {g['tokens_out'] if g else '—'} |")
        if g:
            tot["mi"] += m["tokens_in"]; tot["mo"] += m["tokens_out"]
            tot["gi"] += g["tokens_in"]; tot["go"] += g["tokens_out"]; tot["n"] += 1
    passed = sum(r["degerlendirme"]["gecti"] for r in rows)
    lines += ["", f"**Geçen: {passed}/{len(rows)}**", ""]
    if tot["n"]:
        lines += [f"Karşılaştırılabilir {tot['n']} soruda toplam: MCP {tot['mi']} girdi / {tot['mo']} çıktı token; "
                  f"GUI ekran görüntüsü {tot['gi']} girdi / {tot['go']} çıktı token.", ""]
    rel = LOGS.relative_to(ROOT).as_posix() if LOGS.is_relative_to(ROOT) else LOGS.as_posix()
    lines += [f"Her sorunun tam akışı (araç çağrısı, araç sonucu, yanıt): `{rel}/`.", "",
              "## Yanıtlar", ""]
    for r in rows:
        lines += [f"### {r['id']}", "", f"> {r['soru']}", "", r["mcp"]["final"].strip(), "",
                  f"Kontroller: `{json.dumps(r['degerlendirme']['kontroller'], ensure_ascii=False)}`", ""]
    (OUT / "RESULTS.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
