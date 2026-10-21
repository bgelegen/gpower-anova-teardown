# Oturum 2 · Yeniden yazım — ilk prompt

> Bu oturum **SPEC.md ve CONTRACT.md dışında hiçbir davranış belgesi görmez.**
> `Oturum2-temiz-oda.bat`:
>
> 1. Repo dışında boş bir klasör açar: `C:\Users\batuh\YZM301-temiz-oda\`,
>    içine yalnızca `SPEC.md`, `CONTRACT.md` ve boş MCP yapılandırması
>    `bos-mcp.json` (`{"mcpServers":{}}`) kopyalanır.
> 2. Claude Code'u orada **REA olmadan** ve başsız çalıştırır:
>    `claude -p <aşağıdaki metin> --strict-mcp-config --mcp-config bos-mcp.json --model sonnet --permission-mode auto --disallowedTools WebFetch WebSearch`
>    (REA ve diğer tüm MCP sunucuları bu oturumda yüklenmez; web araçları kapalı.
>    Plan kotası için bu oturumda Sonnet kullanıldı.)
> 3. Bitince `src/`, `tests/` ve `pyproject.toml` repoya taşınır; araç çağrıları
>    ve token kullanımı repo dışındaki `loglar\oturum2.jsonl` dosyasındadır.

---

Bir istatistiksel güç analizi motoru yazacaksın. Bulunduğun klasörde yalnızca iki
belge var: SPEC.md (davranış) ve CONTRACT.md (komut satırı arayüzü). Tek kaynağın
bunlar. Bu klasörün dışındaki dosyalara bakma, internette arama yapma, hiçbir
yürütülebilir programı inceleme. İnternete yalnızca pip paket kurulumu için çık.

Ortam: Windows, Python 3.13 (py -3.13 ile çağrılır). Bu klasörde bir sanal ortam
kur: py -3.13 -m venv .venv ; sonra .venv\Scripts\python -m pip install scipy pytest mcp
ve paketi düzenlenebilir kur: .venv\Scripts\python -m pip install -e .

Yapılacaklar:

1. Paket düzeni (tek motor, ince adaptörler):
   - pyproject.toml: paket adı gpower-clone, Python >= 3.10, bağımlılık scipy;
     isteğe bağlı mcp; gpower-clone ve gpower-clone-mcp komutlarını kaydeden
     giriş noktaları.
   - src/gpower_clone/engine.py: saf hesap. Girdi doğrulama, a priori ve post hoc
     hesap SPEC'teki kurallarla. Tam hassasiyetli sonuç döndürür; G/Ç yapmaz.
     Hata durumunda SPEC'teki mesaj metniyle bir istisna sınıfı fırlatır; uyarıları
     sonuçla birlikte döndürür.
   - src/gpower_clone/contract.py: CONTRACT.md bölüm 5'teki üç tablo
     (FLAG_ALIASES, MODE_ALIASES, OUTPUT_FIELDS). Bayrak ve alan adları başka
     hiçbir dosyada sabit yazılmasın.
   - src/gpower_clone/cli.py: CONTRACT.md'ye birebir uyan komut satırı. Standart
     çıktıya tek satır JSON; geçersiz girdide error alanlı JSON ve çıkış kodu 2;
     uyarı stderr'e, çıkış kodu 0.
   - src/gpower_clone/mcp_server.py: mcp paketinin FastMCP sınıfıyla stdio MCP
     sunucusu. Tek araç: anova_oneway (parametreler: mode, f, alpha, power,
     groups, n_total, digits). Aracın döndürdüğü nesne CLI'nin yazdığı JSON
     nesnesiyle alan alan aynı olmalı; hata durumunda aynı error nesnesi.
     Sunucu hesap yapmaz, yalnızca motoru çağırır ve CLI ile aynı biçimlendirme
     fonksiyonunu kullanır.
   - src/gpower_clone/display.py: SPEC'teki G*Power gösterim kuralı (hangi
     değerin ekranda nasıl görüneceği). Diferansiyel testler bunu kullanır.

2. Testler (tests/, pytest):
   - SPEC'teki her kural (R-xx) için en az bir test; test adında kural kimliği
     geçsin: test_R05_... gibi. SPEC'teki her Gherkin senaryosu da bir test olsun.
   - tests/test_cli.py: CLI'yi alt süreç olarak çalıştırıp JSON biçimini, alan
     sırasını, çıkış kodlarını ve takma adları dener.
   - tests/test_mcp_equality.py: en az 30 girdi için (geçerli ve geçersiz) MCP
     aracının sonucu ile CLI çıktısı birebir aynı mı. MCP tarafını gerçek stdio
     istemcisiyle (mcp paketinin istemcisi) çağır.
   - tests/test_oracle_gui.py ve tests/test_oracle_library.py: diferansiyel test.
     Oracle dosyaları bu klasörde YOK; repoya taşınınca oracle/ klasöründe
     olacaklar. Yolu ortam değişkeni ORACLE_DIR'den, yoksa depo kökündeki
     oracle/ klasöründen al; dosya yoksa testleri atla (skip), başarısız sayma.
     Dosya biçimleri:
     a) oracle/gpower_gui_vectors.csv sütunları: id, mode (a-priori ya da
        post-hoc), f, alpha, power, groups, n_total, sinif, neden, gp_n_total,
        gp_actual_power, gp_critical, gp_df1, gp_df2, gp_ncp, gp_mesaj,
        ekran_goruntusu. gp_* değerleri G*Power penceresinde göründüğü gibi
        metindir. gp_n_total boş ve gp_mesaj doluysa G*Power hata vermiştir:
        motor da hata vermeli ve mesaj gp_mesaj ile aynı olmalı (satır sonları
        boşluk sayılır). gp_mesaj Please note: ile başlıyorsa bu bir uyarıdır:
        sonuç verilmeli ve uyarı metni aynı olmalı.
     b) oracle/library_vectors.csv sütunları: mode, f, alpha, power, groups,
        n_total, lib_n_total_raw, lib_power. Bu statsmodels kütüphanesinin
        çıktısıdır: a priori satırlarda lib_n_total_raw kesirli ham N'dir;
        post hoc satırlarda lib_power güçtür.
     Tolerans: N, n_per_group, df1, df2 birebir aynı. Diğer alanlar, motorun
     tam hassasiyetli değeri display.py ile G*Power biçimine çevrildiğinde metin
     olarak aynı olmalı. Kütüphane vektörlerinde: a priori için beklenen N, ham
     N'den SPEC'teki yuvarlama kuralıyla türetilir ve motorun N'i ile aynı olmalı;
     post hoc güç için mutlak fark 1e-6'dan küçük olmalı. Her uyuşmazlığı testin
     hata mesajında vektör kimliğiyle yaz.
     SPEC bir vektör için G*Power ile bilerek ayrıştığımızı söylüyorsa (bilinen
     sapma) o vektörü pytest.mark.xfail(strict=True) ile işaretle ve gerekçeyi
     yaz.
   - Tüm testleri çalıştır, geçir.

3. SPEC'te belirsiz ya da çelişkili bir yer görürsen tahmin etme: SPEC_SORULARI.md
   dosyasına yaz, makul ve SPEC ile çelişmeyen bir seçim yap, seçimini o dosyada
   gerekçelendir ve devam et.

4. Bitince kısa bir özet yaz: dosyalar, test sayısı, geçen/atlanan, SPEC_SORULARI
   sayısı.

Önce kısa bir plan yaz, sonra onay beklemeden başla.

---
