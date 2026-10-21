# SPEC / CONTRACT soruları ve verilen kararlar

Her madde: belirsizlik → seçim → gerekçe.

1. **`Please note:` öneki (R-14, oracle `gp_mesaj`).** SPEC uyarı metnini önek olmadan
   verir; oracle'daki `gp_mesaj` `Please note:` ile başlıyor. → Motor uyarıyı önek olmadan
   üretir (SPEC metni); diferansiyel testte iki taraftan da `Please note:` öneki ve satır
   sonları atılıp boşluklar normalize edilerek karşılaştırılır. Gerekçe: SPEC "başlığı
   `Please note` olan kutu" der; yani önek başlıktır, gövde değil.

2. **Hata metninin satır sonları (R-13).** SPEC iki satırlı yazar. → Motor tek satır, boşlukla
   birleşik yazar (`... greater than the number of groups (3).`). Gerekçe: CONTRACT JSON
   hatasının tek satırda olması gerekir; test satır sonlarını boşluk sayar.

3. **`--test` bayrağı zorunlu mu? (CONTRACT §1).** Komut biçiminde var ama parametre
   tablosunda yok. → İsteğe bağlı; verilirse `anova-oneway` olmalı, yoksa hata (çıkış 2).
   Gerekçe: gizli vektörlerin bayrağı atlaması riskine karşı hoşgörülü, yanlış testi ise reddet.

4. **`--digits` sınırları (CONTRACT §3).** Aralık belirtilmemiş. → 0–15 tamsayı; dışı veya
   tamsayı olmayan değer geçersiz girdi (çıkış 2). `digits=0`'da ondalıklı alanlar tamsayı olarak
   yazılır. Gerekçe: `round()` makul sınırı; 15 çift duyarlığın anlamlı basamağıdır.

5. **JSON'da `n_per_group` ve ondalıklı alanlar.** CONTRACT "tam sayı ya da sayı" der. →
   Bölünüyorsa tamsayı (84), değilse `digits`'e yuvarlanmış (20.3333). `ncp` gibi alanlar
   tamsayı değerde bile ondalıklı yazılır (ör. `150.0`); örnekteki `15.75` ile uyumlu.

6. **Doğrulama sırası ile CLI kontrolleri (R-08 vs CONTRACT §3).** SPEC yalnız sayısal sırayı
   tanımlar. → Önce bayrak ayrıştırma (bilinmeyen / yinelenen / değersiz), sonra mod,
   modda kullanılmayan bayrak, eksik zorunlu parametre, `--digits`, en son SPEC sırası
   (k → f → α → …). Gerekçe: CONTRACT bunları "geçersiz girdi" sayar ama G*Power karşılığı yok.

7. **Sayısal olmayan girdi (R-17).** → `Input error (illegal character?)` (SPEC'teki G*Power
   metni). `nan`, `inf`, boş dize, bool, virgüllü ondalık (`1,5`) de bu kapsamda. Bu kontrol
   ilgili alanın sırası geldiğinde yapılır (örn. k önce).

8. **R-16 sayısal hata çıkış kodu.** `G*Power was not able to compute...` hatası SPEC'te
   "çıktı yok" der, çıkış kodu söylemez. → Geçersiz girdi gibi `{"error":...}` ve çıkış 2.
   Gerekçe: CONTRACT'ta çıkış 1 yalnızca beklenmeyen iç hata içindir.

9. **Brent durma koşulu (R-04).** SciPy `brentq` mutlak `xtol` ister ve `rtol ≥ 4·eps` şartı var.
   → `xtol=1e-300`, `rtol=4·2⁻⁵²` (SciPy'nin alt sınırı; SPEC'in 2⁻⁵³'üne en yakın izinli
   değer), `maxiter=300`, yakınsamazsa son tahmin. Kökün yalnızca sonradan yukarı yuvarlanması
   önemli olduğundan N etkilenmez (sınır durumları R-18 / §5 bilinmeyenleri).

10. **R-04 aralık kurma döngüsü ve taşma.** İterasyon sınırı yok, ama `1,6·N` sonsuza taşarsa
    sonsuz döngü olur. → Sonsuza varınca (veya güç `nan` olunca) R-16 sayısal hata mesajı.

11. **R-18 / V52 ve benzerleri.** Doğru hesap yapılır; V52 `xfail(strict=True)`. "df2 ~10⁸ üstü
    benzer vektörler" SPEC'te adlandırılmadığı için ayrıca işaretlenmedi; bozuk çıkarlarsa
    gerçek uyuşmazlık sayılır (kararı insan versin). Ölçümümüz (f=0,0001, α=0,05, k=3): motor
    N=963 468 891 verir (güç 0,80000000053 ≥ 0,80); bir önceki 3 katı 963 468 888'in gücü
    0,79999999992 < 0,80. SPEC §5'in anıp G*Power değeri saydığı N=963 468 906 (oracle dosyasını görmedim) bizim değerimizden 15 büyük olurdu;
    §5'in "tam güç(963468906) ≥ 0,80 ise G*Power N doğrudur" dalı burada geçerli değildir,
    çünkü minimum N 963 468 891'dir.

12. **`mcp` paketi sürümü.** Görev `FastMCP` der; kurulan `mcp` 2.x'te sınıf `MCPServer`
    adını aldı (`mcp.server.fastmcp` yok). → `mcp_server.py` önce `FastMCP`'i, olmazsa
    `MCPServer`'ı içe aktarır (aynı dekoratör API'si). Testler istemci alan adı farkına
    (`isError` / `is_error`) dayanıklıdır. SPEC/CONTRACT konusu değil, ortam kararı.

13. **MCP uyarıları.** CLI uyarıyı stderr'e yazar; MCP aracının döndürdüğü nesne CLI
    stdout'u ile alan alan aynı olmak zorunda olduğundan uyarı nesneye eklenmez, sunucunun
    stderr'ine yazılır.
