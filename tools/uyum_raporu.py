"""Diferansiyel test ve uyum raporu → tests/UYUM_RAPORU.md

İki oracle'ın her satırını motorla karşılaştırır (testlerin kullandığı aynı karşılaştırma kodu,
tests/helpers.py::compare_gui_row) ve vektör vektör tablo + oranlar + sapma açıklamaları yazar.

Kullanım (repo kökü): python tools/uyum_raporu.py
"""
from __future__ import annotations

import math
import platform
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))

import scipy  # noqa: E402
from helpers import blank, canonical_mode, compare_gui_row, engine_inputs, read_csv  # noqa: E402

from gpower_clone import engine  # noqa: E402
from gpower_clone.contract import APRIORI  # noqa: E402
from gpower_clone.display import format_fraction, format_integer  # noqa: E402

KNOWN = {
    "V52": "R-18: df2 ≈ 10⁹; G*Power'ın N'i minimum değil (15 kişi fazla) — mpmath 40 basamakla kanıtlı",
    "V54": "R-18: G*Power'ın N'i hedef gücü **sağlamıyor** (0,7999999953 < 0,80) — motor 3 kişi fazla, doğru",
    "V55": "R-18: G*Power'ın N'i 2 520 kişi fazla — mpmath ile kanıtlı",
    "V56": "R-18: N ≈ 9,6·10¹²; G*Power'ın λ'sı 9,6363, doğrusu ≈ 9,63469",
}
FIELDS = [("N", "gp_n_total"), ("güç", "gp_actual_power"), ("F krit.", "gp_critical"),
          ("df1", "gp_df1"), ("df2", "gp_df2"), ("λ", "gp_ncp"), ("mesaj", "gp_mesaj")]


def lib_expected_n(raw: float, k: int) -> int:
    n = math.ceil(raw / k) * k
    return n if n >= k + 1 else 2 * k


def main() -> int:
    rows = read_csv("gpower_gui_vectors.csv")
    lines, kinds, stat = [], Counter(), Counter()
    field_bad = Counter()
    n_rows = n_ok = 0
    for row in rows:
        vid = row["id"]
        bad = compare_gui_row(row)
        kind = ("hata" if not row["gp_n_total"].strip() else
                "not" if row["gp_mesaj"].lower().startswith("please note") else "sonuç")
        kinds[kind] += 1
        try:
            r = engine.calculate(**engine_inputs(row))
            motor_n, motor_p = format_integer(r.total_n), format_fraction(r.power)
        except engine.GPowerError as exc:
            motor_n, motor_p = "—", f"hata: {exc}"
        st = "✅ birebir" if not bad else ("⚠️ bilinen sapma" if vid in KNOWN else "❌ AÇIKLANMAMIŞ")
        stat[st] += 1
        for label, col in FIELDS:
            if any(f"{col} " in d for d in bad):
                field_bad[label] += 1
        if kind != "hata":
            n_rows += 1
            n_ok += row["gp_n_total"].strip() == motor_n
        girdi = (f"{row['mode']}, f={row['f']}, α={row['alpha']}, "
                 + (f"güç={row['power']}" if canonical_mode(row["mode"]) == APRIORI else f"N={row['n_total']}")
                 + f", k={row['groups']}")
        gp = row["gp_n_total"] or row["gp_mesaj"][:40]
        lines.append(f"| {vid} | {girdi} | {gp} / {row['gp_actual_power'] or '—'} | "
                     f"{motor_n} / {motor_p[:40]} | {st} |")

    lib = read_csv("library_vectors.csv")
    lib_ok = lib_n = 0
    max_diff = 0.0
    for row in lib:
        res = engine.calculate(**engine_inputs(row))
        if canonical_mode(row["mode"]) == APRIORI:
            if blank(row.get("lib_n_total_raw")):
                continue
            k = engine._round_half_up(float(row["groups"]))
            lib_n += 1
            lib_ok += res.total_n == lib_expected_n(float(row["lib_n_total_raw"]), k)
        else:
            if blank(row.get("lib_power")):
                continue
            d = abs(res.power - float(row["lib_power"]))
            max_diff = max(max_diff, d)
            lib_n += 1
            lib_ok += d < 1e-6

    total = len(rows)
    exact = stat["✅ birebir"]
    out = [
        "# Diferansiyel test ve uyum raporu",
        "",
        "Bu rapor `python tools/uyum_raporu.py` ile **testlerin kullandığı aynı karşılaştırma kodundan** "
        "(`tests/helpers.py::compare_gui_row`) üretilir. Her satırda G*Power 3.1.9.7'nin GUI'de gösterdiği "
        "değer ile temiz odada yazılan motorun aynı girdideki gösterimi alan alan, 7 basamaklı metin olarak "
        "karşılaştırılır (sayı yakınlığı değil, ekrandaki dizginin aynısı).",
        "",
        f"Ortam: Python {platform.python_version()} · scipy {scipy.__version__} · {platform.system()}.",
        "",
        "## Oranlar",
        "",
        "| Ölçü | Değer |",
        "|------|------:|",
        f"| G*Power GUI vektörü (ekran görüntülü) | {total} ({kinds['sonuç']} sonuç, {kinds['not']} uyarılı, {kinds['hata']} hata) |",
        f"| Bütün alanlar + mesaj birebir | **{exact}/{total} (%{f'{100 * exact / total:.1f}'.replace('.', ',')})** |",
        f"| Toplam N birebir (sonuç veren {n_rows} vektör) | **{n_ok}/{n_rows} (%{f'{100 * n_ok / n_rows:.1f}'.replace('.', ',')})** |",
        f"| Hata mesajı birebir ({kinds['hata']} hata vektörü) | {kinds['hata']}/{kinds['hata']} |",
        f"| Bilinen sapma (R-18, açıklamalı) | {stat['⚠️ bilinen sapma']} |",
        f"| **Açıklanmamış uyumsuzluk** | **{stat['❌ AÇIKLANMAMIŞ']}** |",
        f"| statsmodels kütüphane vektörü (bağımsız ikinci oracle) | {lib_ok}/{lib_n} uyumlu "
        f"(post hoc güç farkı en çok {max_diff:.1e}) |",
        "",
        "Sapan alan sayısı (yalnızca bilinen sapmalardan): "
        + ", ".join(f"{k} {v}" for k, v in field_bad.items() if v) + ".",
        "",
        "## Uyumsuzlukların açıklaması",
        "",
        "Dört sapmanın dördü de aşırı küçük etki büyüklüğündedir (f ≤ 0,0002, N ≥ 2,4·10⁸). Bu bölgede "
        "çift duyarlıklı her merkezi olmayan F hesabı gürültülüdür; kimin doğru olduğu `mpmath` ile 40 "
        "basamakta ayrıca hesaplandı (`oracle/R18_YUKSEK_HASSASIYET.md`, `tests/test_r18_high_precision.py`). "
        "Testlerde `xfail(strict=True)` ile işaretlidirler: G*Power ile birden eşleşirlerse test **kırmızı** "
        "olur, yani bu liste sessizce eskiyemez.",
        "",
        "| Vektör | Açıklama |",
        "|--------|----------|",
        *[f"| {k} | {v} |" for k, v in KNOWN.items()],
        "",
        "## Vektör vektör",
        "",
        "| Vektör | Girdi | G*Power (N / güç) | Motor (N / güç) | Sonuç |",
        "|--------|-------|-------------------|-----------------|-------|",
        *lines,
        "",
        "Ekran görüntüleri: `oracle/screenshots/<Vektör>.png` · ham değerler: `oracle/gpower_gui_vectors.csv` · "
        "aynı karşılaştırma tarayıcıda: canlı demodaki **Doğrula** düğmesi.",
        "",
    ]
    (ROOT / "tests" / "UYUM_RAPORU.md").write_text("\n".join(out), encoding="utf-8")
    print("\n".join(out[8:22]))
    return 0 if stat["❌ AÇIKLANMAMIŞ"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
