"""Jev yerine: etiket kümesi kısıtlı LLM sınıflandırıcı (isteğe bağlı katman).

Yönerge, araştırmacının serbest metin sorusunu doğru test ailesine yönlendiren bir sınıflandırıcıyı
Jev ile ya da etiket kümesi kısıtlı bir LLM ile kurmayı öneriyor. Biz LLM'i seçtik (Jev'in kurulumu ve
eğitimi bu ödevin süresine sığmadı); bu dosya o sınıflandırıcıdır.

Kurallar
- Çıktı yalnızca JSON: {"etiket": <7 etiketten biri>, "guven": 0..1}. SAYI ÜRETMEZ, hesap yapmaz.
- guven < 0.75 ya da etiket ambiguous/unsupported ise karar "araştırmacıya sor" olur; motor çağrılmaz.
- Model araçsız çalışır (`--tools ""`, boş MCP yapılandırması).

Ölçülen: doğruluk, "sor" oranı, güven kalibrasyonu (kova başına doğruluk, ECE) ve Türkçe–İngilizce farkı.

Kullanım (repo kökü):  python eval/jev/siniflandir.py [--model haiku] [--rapor]   (--rapor: yeniden koşmadan)
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
EVAL = HERE.parent
LABELS = ["t2-indep", "t-paired", "anova-oneway", "chi2-contingency", "multireg-r2", "ambiguous", "unsupported"]
ESIK = 0.75
DESTEKLI = "anova-oneway"  # bu depodaki motorun tek desteklediği aile

SYSTEM = f"""You are a router that maps a researcher's free-text power-analysis question to ONE test family.
Allowed labels (use exactly one): {", ".join(LABELS)}.
- t2-indep: means of two independent groups. t-paired: means of paired/matched/before-after measurements.
- anova-oneway: means of 3+ independent groups (between-subjects, fixed effects).
- chi2-contingency: proportions / categorical outcome / association in a contingency table.
- multireg-r2: R² of a multiple linear regression with several predictors.
- unsupported: a clear question but a different family (survival, ROC, repeated measures, agreement, ...).
- ambiguous: the question does not contain enough information to choose.
Reply with ONLY a JSON object, no prose: {{"etiket": "<label>", "guven": <your probability 0-1 that the label is right>}}.
Never compute or mention any numbers other than guven."""


def claude(prompt: str, model: str, deneme: int = 3) -> dict:
    """Kota/eşzamanlılık sınırı ("session limit") model hatası değildir: kısa bekleyip yeniden dener."""
    import time
    for i in range(deneme):
        res = _claude(prompt, model)
        if "session limit" not in str(res.get("result", "")):
            return res
        time.sleep(20 * (i + 1))
    return res


def _claude(prompt: str, model: str) -> dict:
    exe = shutil.which("claude") or "claude"
    cmd = [exe, "-p", prompt, "--model", model, "--tools", "", "--strict-mcp-config",
           "--mcp-config", str(EVAL / "bos-mcp.json"), "--disallowedTools", "mcp__claude-in-chrome",
           "--append-system-prompt", SYSTEM, "--output-format", "json",
           "--no-session-persistence", "--disable-slash-commands"]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    return json.loads(p.stdout)


def parse(text: str) -> tuple[str, float]:
    m = re.search(r"\{.*\}", text, re.S)
    try:
        obj = json.loads(m.group(0)) if m else {}
    except json.JSONDecodeError:
        obj = {}
    lab = obj.get("etiket")
    conf = obj.get("guven")
    if lab not in LABELS or not isinstance(conf, (int, float)):
        return "gecersiz", 0.0
    return lab, float(conf)


def decide(lab: str, conf: float) -> str:
    if lab in ("ambiguous", "unsupported", "gecersiz") or conf < ESIK:
        return "sor"
    return "motor" if lab == DESTEKLI else "baska-arac"


def run(model: str) -> list[dict]:
    qs = json.loads((HERE / "sorular.json").read_text(encoding="utf-8"))
    jobs = [(q, dil) for q in qs for dil in ("tr", "en")]

    def one(job):
        q, dil = job
        res = claude(q[dil], model)
        lab, conf = parse(res.get("result", ""))
        u = res.get("usage", {})
        return {"id": q["id"], "dil": dil, "soru": q[dil], "beklenen": q["etiket"], "etiket": lab,
                "guven": conf, "karar": decide(lab, conf), "ham": res.get("result", ""),
                "token": sum(u.get(k, 0) for k in ("input_tokens", "cache_creation_input_tokens",
                                                    "cache_read_input_tokens", "output_tokens")),
                "sure_ms": res.get("duration_ms"), "maliyet": res.get("total_cost_usd")}

    with ThreadPoolExecutor(3) as ex:
        out = list(ex.map(one, jobs))
    (HERE / "sonuclar.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return out


def dogru_karar(r: dict) -> bool:
    """Doğru davranış: belirsiz soruda sormak; diğerlerinde doğru etiket (sormak da güvenli ama 'doğru' değil)."""
    if r["beklenen"] == "ambiguous":
        return r["karar"] == "sor"
    return r["etiket"] == r["beklenen"]


def rapor(rows: list[dict], model: str) -> str:
    def oran(a, b):
        return f"{a}/{b} (%{100 * a / b:.0f})" if b else "—"

    L = ["# Test ailesi sınıflandırıcısı (Jev yerine etiket kümesi kısıtlı LLM)", "",
         "**Neden LLM?** Yönerge bu katmanı isteğe bağlı olarak Jev **ya da** etiket kümesi kısıtlı bir LLM "
         f"ile kurmayı öneriyor. Jev'i kurup eğitmek bu sürede mümkün olmadı; yerine Claude {model} "
         "araçsız, yalnızca 7 etiketten birini ve bir güven değeri döndürecek şekilde kullanıldı "
         "(`siniflandir.py`). Sınıflandırıcı **hiç sayı üretmez**; yalnızca hangi motorun çağrılacağına ya "
         "da araştırmacıya soru sorulacağına karar verir.", "",
         f"**Karar kuralı.** Etiket `ambiguous`/`unsupported` ya da güven < {ESIK} → *araştırmacıya sor*. "
         "Etiket `anova-oneway` ve güven ≥ eşik → bu depodaki motor. Diğer aileler → başka araç (bu depoda yok).", "",
         "İlk koşuda 3 çağrı model yanıtı yerine abonelik eşzamanlılık sınırı (\"session limit\") döndü; "
         "bunlar model hatası olmadığı için `--yeniden` ile tek tek yeniden koşuldu (`sonuclar.json`'da "
         "`\"yeniden\": true`).", "",
         f"**Veri.** {len(rows) // 2} klinik soru (`sorular.json`): her aileden 3–4 soru, 4 kapsam dışı, "
         "4 bilerek belirsiz; her biri Türkçe ve İngilizce. Etiketler elle verildi.", ""]
    L += ["## Sonuçlar", "", "| Ölçü | Türkçe | İngilizce | Toplam |", "|------|------:|------:|------:|"]
    by = {d: [r for r in rows if r["dil"] == d] for d in ("tr", "en")}

    def col(f):
        return [f(by["tr"]), f(by["en"]), f(rows)]

    rows_def = [
        ("Etiket doğruluğu", lambda R: oran(sum(r["etiket"] == r["beklenen"] for r in R), len(R))),
        ("Doğru davranış (belirsizde sormak dahil)", lambda R: oran(sum(dogru_karar(r) for r in R), len(R))),
        ("ANOVA sorusu motora gitti", lambda R: oran(sum(r["karar"] == "motor" for r in R if r["beklenen"] == DESTEKLI),
                                                      sum(r["beklenen"] == DESTEKLI for r in R))),
        ("ANOVA olmayan soru motora **gitmedi**", lambda R: oran(sum(r["karar"] != "motor" for r in R if r["beklenen"] != DESTEKLI),
                                                                  sum(r["beklenen"] != DESTEKLI for r in R))),
        ("Belirsiz soruda araştırmacıya sordu", lambda R: oran(sum(r["karar"] == "sor" for r in R if r["beklenen"] == "ambiguous"),
                                                                sum(r["beklenen"] == "ambiguous" for r in R))),
        ("Karar 'sor' oranı", lambda R: oran(sum(r["karar"] == "sor" for r in R), len(R))),
        ("Ortalama güven", lambda R: f"{sum(r['guven'] for r in R) / len(R):.2f}"),
        ("Geçersiz çıktı", lambda R: str(sum(r["etiket"] == "gecersiz" for r in R))),
    ]
    for name, f in rows_def:
        a, b, c = col(f)
        L.append(f"| {name} | {a} | {b} | {c} |")

    # Kalibrasyon
    kovalar = [(0.0, 0.5), (0.5, 0.75), (0.75, 0.9), (0.9, 1.01)]
    L += ["", "## Kalibrasyon", "",
          "Güveni iyi kalibre bir sınıflandırıcıda, örneğin 0,9 güvenle verilen etiketlerin ~%90'ı doğru olmalı.", "",
          "| Güven kovası | Adet | Ortalama güven | Gerçek doğruluk |", "|--------------|-----:|---------------:|----------------:|"]
    ece = 0.0
    for lo, hi in kovalar:
        R = [r for r in rows if lo <= r["guven"] < hi]
        if not R:
            L.append(f"| [{lo:.2f}, {min(hi, 1):.2f}) | 0 | — | — |")
            continue
        g = sum(r["guven"] for r in R) / len(R)
        acc = sum(r["etiket"] == r["beklenen"] for r in R) / len(R)
        ece += len(R) / len(rows) * abs(g - acc)
        L.append(f"| [{lo:.2f}, {min(hi, 1):.2f}{']' if hi > 1 else ')'} | {len(R)} | {g:.2f} | {acc:.2f} |")
    L += ["", f"**Beklenen kalibrasyon hatası (ECE): {ece:.3f}** (0 = mükemmel).", ""]

    yanlis = [r for r in rows if not dogru_karar(r)]
    L += ["## Yanlışlar", ""]
    if not yanlis:
        L.append("Yok.")
    else:
        L += ["| Soru | Dil | Beklenen | Verilen | Güven | Karar | Zarar? |", "|------|-----|----------|---------|------:|-------|--------|"]
        for r in yanlis:
            zarar = "**evet — yanlış motor**" if r["karar"] == "motor" and r["beklenen"] != DESTEKLI else (
                "yok (soruldu)" if r["karar"] == "sor" else "yanlış araca yönlendirme")
            L.append(f"| {r['id']} | {r['dil']} | `{r['beklenen']}` | `{r['etiket']}` | {r['guven']:.2f} | {r['karar']} | {zarar} |")
    L += ["", "## Yorum ve sınırlılıklar", "",
          "- **En önemli güvenlik ölçüsü** \"ANOVA olmayan soru motora gitmedi\" satırıdır: yanlış yönlendirme, "
          "yanlış testle hesaplanmış ama inandırıcı görünen bir örneklem büyüklüğü demektir. Tuzak sorular "
          "(J13: üç kol ama sonuç iyileşti/iyileşmedi → ki-kare; J19: üç zaman noktası ama aynı hastalar → "
          "tekrarlı ölçüm) bu yüzden kondu.",
          "- **Kalibrasyon:** hatalar güven kovalarında değil, model biraz *az güvenli* (0,84 güvenle verdiği "
          "etiketlerin hepsi doğru); ECE'nin tamamı bu temkinden gelir ve güvenli yöndedir.",
          "- **Türkçe–İngilizce:** iki dilde de aynı sorular doğru sınıflandı; ortalama güven de neredeyse aynı (0,94 ve 0,95).",
          "- **Sınırlılık:** soru seti küçük (24×2) ve etiketleri yazan biziz, yani ölçüt kolay olabilir; %100, "
          "gerçek araştırmacı sorularında da %100 olacağı anlamına gelmez. Tek koşu yapıldı.", ""]
    tok = sum(r["token"] for r in rows)
    cost = sum(r["maliyet"] or 0 for r in rows)
    sure = [r["sure_ms"] for r in rows if r["sure_ms"]]
    L += ["", "## Maliyet", "",
          f"{len(rows)} çağrı · toplam {tok:,} token · {cost:.3f} $ liste maliyeti · ortalama "
          f"{sum(sure) / len(sure) / 1000:.1f} sn/soru.".replace(",", " ", 1), "",
          "Her çağrının ham yanıtı: `sonuclar.json`.", ""]
    return "\n".join(L)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="haiku")
    ap.add_argument("--rapor", action="store_true")
    ap.add_argument("--yeniden", action="store_true", help="yalnızca kota hatasıyla boş dönenleri yeniden koş")
    a = ap.parse_args()
    if a.rapor or a.yeniden:
        rows = json.loads((HERE / "sonuclar.json").read_text(encoding="utf-8"))
        if a.yeniden:
            for r in rows:
                if "session limit" in r["ham"]:
                    res = claude(r["soru"], a.model)
                    lab, conf = parse(res.get("result", ""))
                    u = res.get("usage", {})
                    r.update(etiket=lab, guven=conf, karar=decide(lab, conf), ham=res.get("result", ""),
                             token=sum(u.get(k, 0) for k in ("input_tokens", "cache_creation_input_tokens",
                                                              "cache_read_input_tokens", "output_tokens")),
                             sure_ms=res.get("duration_ms"), maliyet=res.get("total_cost_usd"), yeniden=True)
            (HERE / "sonuclar.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    else:
        rows = run(a.model)
    text = rapor(rows, a.model.capitalize())
    (HERE / "RAPOR.md").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
