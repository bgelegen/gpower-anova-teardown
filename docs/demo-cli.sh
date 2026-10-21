#!/usr/bin/env bash
cd /home/claude/gpower-anova-teardown
source /home/claude/venv-gp/bin/activate
export PS1=""
P=$'\e[1;32mbatuhan@yzm301\e[0m:\e[1;34m~/gpower-anova-teardown\e[0m$ '
say() { printf '\e[1;33m# %s\e[0m\n' "$1"; sleep 1.2; }
run() {
  printf '%s' "$P"; sleep 0.4
  local s="$1" i
  for ((i=0;i<${#s};i++)); do printf '%s' "${s:i:1}"; sleep 0.022; done
  printf '\n'; sleep 0.3
  eval "$1"
  sleep "${2:-2.2}"
}
clear
say "YZM301 Teardown Sprint · İz 3 · F testi, tek yönlü ANOVA (üç tedavi kolu)"
say "G*Power 3.1.9.7 davranışının temiz oda yeniden yazımı · Batuhan Gelegen"
run "gpower-clone --test anova-oneway --mode a-priori --f 0.25 --alpha 0.05 --power 0.95 --groups 3"
say "N = 252: 251 değil, 3'ün katına yukarı yuvarlanır (kılavuzda yok, REA ile bulundu)"
run "gpower-clone --test anova-oneway --mode a-priori --f 0.25 --alpha 0.05 --power 0.95 --groups 2"
say "k = 2 → hocanın t2-indep referansı: N = 210, güç 0.9501"
run "gpower-clone --test anova-oneway --mode a-priori --f 0.25 --alpha 0.05 --power 0.95 --groups 3 --digits 7"
say "7 hane = G*Power penceresiyle birebir (oracle V05)"
run "gpower-clone --test anova-oneway --mode post-hoc --f 0.25 --alpha 0.05 --n-total 61 --groups 3"
say "Post hoc: N grup sayısına bölünmüyor → G*Power'ın uyarısı stderr'e, çıkış 0"
run "gpower-clone --test anova-oneway --mode a-priori --f 0.25 --alpha 0.05 --power 0.03 --groups 3; echo \"exit=\$?\""
say "Geçersiz girdi → {\"error\": ...}, sıfırdan farklı çıkış kodu"
run "python -m pytest -q -p no:cacheprovider tests/test_oracle_gui.py tests/test_oracle_library.py tests/test_r18_high_precision.py 2>&1 | tail -1" 1.5
say "63 G*Power GUI vektörü + 1485 statsmodels vektörü: N birebir (4 bilinen sapmada motor doğru)"
sleep 2
