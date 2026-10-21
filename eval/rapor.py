"""Yönergenin istediği ajan raporu (kayıtlardan; ajanı yeniden çalıştırmaz):
- her soru için beklenen test ailesi ve DOĞRU SEÇİM oranı,
- MCP ve GUI (ekran görüntüsü) yollarının token, süre ve doğruluk değerleri.

Kullanım: python eval/rapor.py   →  eval/KARSILASTIRMA.md
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

EVAL = Path(__file__).resolve().parent
sys.path.insert(0, str(EVAL))
from agent_eval import load, numbers, summarize  # noqa: E402

RUNS = [("v3 (son sürüm)", EVAL), ("v3 tekrar", EVAL / "v3-tekrar")]


def sp(n, d=0):
    return f"{n:,.{d}f}".replace(",", " ")


def duration(events):
    for e in events:
        if e.get("type") == "result":
            return (e.get("duration_ms") or 0) / 1000
    return None


def gui_correct(q, final):
    """GUI kolu G*Power'ın 7 basamaklı değerini okur; beklenen değer 4 basamaklı.
    Bu yüzden yanıttaki bir sayı, beklenenin basamak sayısına yuvarlandığında eşitse doğru sayılır."""
    ok = q["dogru"]
    if "error" in ok:
        return bool(re.search(r"en az|2 grup|iki grup|at least 2", final, re.I))
    got = [float(x) for x in numbers(final)]
    for k, want in ok.items():
        if k == "uyari":
            if not re.search(r"kat[ıi]|multiple|ortalama|average|b[öo]l[üu]nm", final, re.I):
                return False
            continue
        dec = len(f"{float(want):g}".split(".")[1]) if "." in f"{float(want):g}" else 0
        if not any(round(g, dec) == float(want) for g in got):
            return False
    return True


def main():
    qs = json.loads((EVAL / "questions.json").read_text(encoding="utf-8"))
    out = ["# Ajan değerlendirmesi — yönerge raporu", "",
           "Yönergenin AI ajanı maddesi için: her sorunun **beklenen test ailesi**, ajanın **doğru seçim** "
           "oranı ve aynı soruların **MCP** ve **GUI (ekran görüntüsü)** yollarından token, süre ve doğruluk "
           "değerleri. Değerler Claude Code kayıtlarından (`usage`, `duration_ms`) okunur; `python eval/rapor.py` "
           "ile yeniden üretilir.", ""]
    for name, base in RUNS:
        logs = base / "logs"
        rows, tot = [], dict(sec=0, mcp=0, gui=0, gui_n=0, mt=0, gt=0, ms=0.0, gs=0.0, n=0)
        for q in qs:
            ev = load(logs / f"{q['id']}-mcp.jsonl")
            s = summarize(ev)
            res = json.loads((base / "results.json").read_text(encoding="utf-8"))
            r = next(x for x in res if x["id"] == q["id"])
            called = bool(s["calls"])
            secim = (called if q["aile"] == "anova-oneway" else
                     (not called and bool(re.search(r"destekle|kapsam|yaln[ıi]zca", s["final"], re.I))))
            mcp_ok = r["degerlendirme"]["gecti"]
            md = duration(ev)
            tot["sec"] += secim; tot["mcp"] += mcp_ok
            g = "—"; gt = gs = None
            gpath = logs / f"{q['id']}-gui.jsonl"
            if gpath.exists():
                gev = load(gpath); gsum = summarize(gev)
                gok = gui_correct(q, gsum["final"]); gt = gsum["tokens_in"] + gsum["tokens_out"]; gs = duration(gev)
                g = "✅" if gok else "❌"
                tot["gui"] += gok; tot["gui_n"] += 1
                tot["mt"] += s["tokens_in"] + s["tokens_out"]; tot["gt"] += gt
                tot["ms"] += md or 0; tot["gs"] += gs or 0; tot["n"] += 1
            rows.append(f"| {q['id']} | `{q['aile']}` | {'✅' if secim else '❌'} | {'✅' if mcp_ok else '❌'} | "
                        f"{sp(s['tokens_in'] + s['tokens_out'])} | {md:.1f} sn | {g} | "
                        f"{(sp(gt) if gt else '—')} | {(f'{gs:.1f} sn' if gs else '—')} |")
        n = len(qs)
        out += [f"## {name}", "",
                "| Soru | Beklenen aile | Doğru seçim | MCP doğru | MCP token | MCP süre | GUI doğru | GUI token | GUI süre |",
                "|------|---------------|:-----------:|:---------:|----------:|---------:|:---------:|----------:|---------:|",
                *rows, "",
                f"- **Doğru seçim oranı: {tot['sec']}/{n}** (9 tek yönlü ANOVA sorusunda aracı çağırdı, ki-kare sorusunu "
                "çağırmadan reddetti).",
                f"- **Doğruluk:** MCP {tot['mcp']}/{n} · GUI (ekran görüntüsü) {tot['gui']}/{tot['gui_n']}.",
                f"- **Karşılaştırılabilir {tot['n']} soruda ortalama:** MCP {sp(tot['mt'] / tot['n'])} token, "
                f"{tot['ms'] / tot['n']:.1f} sn · GUI {sp(tot['gt'] / tot['n'])} token, {tot['gs'] / tot['n']:.1f} sn.",
                ""]
    out += ["## Yorum", "",
            "- **Seçim:** ajan iki koşuda da 10/10 doğru aileyi seçti; kapsam dışı ki-kare sorusunda aracı hiç "
            "çağırmadan \"bu araç yalnızca tek yönlü ANOVA'yı destekliyor\" dedi.",
            "- **Doğruluk:** MCP yolunda tek hata (v3 tekrar S09) ajanın \"tek kollu\" soruda grup sayısını kendisi "
            "2 varsaymasıdır (H-08). GUI yolundaki hata S01: grup başı n G*Power ekranında yazmıyor; ajan bunu "
            "dürüstçe söyledi ama soruyu tam yanıtlayamadı. MCP çıktısında bu alan yapısal JSON'da hazır gelir.",
            "- **Token ve süre:** bu tabloda GUI kolu ~500 token ve ~1,5 sn daha ucuz görünüyor, çünkü ona **hazır** "
            "bir G*Power ekran görüntüsü verildi. O görüntüyü üretmek (G*Power'ı açıp alanları doldurmak, ekran "
            "görüntüsü almak) dahil değildir; bu bedel `OZET.md`'de ayrıca hesaplandı (vektör başına ~3 araç "
            "çağrısı ve ~1 500 görüntü token'ı). MCP kolunun fazladan token'ı araç şemasının bağlamda durmasından "
            "gelir ve sabittir.",
            "- **Değerlendirme notu:** G*Power ekranı 7 basamak (0,3744311), beklenen değer 4 basamak (0,3744) "
            "verir; GUI yanıtı beklenen basamağa yuvarlanarak karşılaştırılır.", ""]
    (EVAL / "KARSILASTIRMA.md").write_text("\n".join(out), encoding="utf-8")
    print("\n".join(out[:40]))


if __name__ == "__main__":
    main()
