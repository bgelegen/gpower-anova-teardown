# Oturum 1 · Söküm — devam mesajı

> Aynı söküm oturumuna (`claude --continue`) verilen ikinci mesajın birebir
> kopyası. `Oturum1-devam.bat` ile başsız (`-p`) çalıştırıldı; araç çağrıları ve
> token kullanımı repo dışındaki `loglar\` klasörüne kaydedildi.

---

Oracle'daki 52 vektörün tamamı G*Power 3.1.9.7 penceresinden dolduruldu:
oracle/gpower_gui_vectors.csv (gp_* sütunları ve gp_mesaj) ve her satırın
ekran görüntüsü oracle/screenshots/Vxx.png. Ayrıca resmî kılavuz şurada:
C:\Users\batuh\YZM301-araclar\gpower\GPowerManual.pdf (repo dışında; repoya kopyalama).

Bu turda yalnızca LEDGER.md ve SPEC.md dosyalarını güncelle. Kod yazma; src/ ve
tests/ klasörlerine dokunma. Decompile kodunu yine hiçbir repo dosyasına koyma.

1. Her [AJAN] satırını oracle ile karşılaştır.
   - Oracle doğruluyorsa satırı silme; Kanıt sütununa ilgili Vxx değerini ekle,
     etiketi [AJAN+ORACLE] yap.
   - Oracle yanlışlıyorsa satırı silme; iddianın üstünü çiz (~~ ~~), altına
     doğrusunu yaz ve satırın sonuna YANILGI yaz. Yanılgıları LEDGER'ın sonuna
     Oracle ile çelişen iddialar başlıklı ayrı bir tabloya da koy: önceki iddia,
     oracle'da görülen, hangi vektör, nasıl fark edildi.
2. Oracle'ın ortaya çıkardığı ve SPEC'te henüz olmayan üç davranışı binary'de
   ara; bulursan [REA] satırı ekle, bulamazsan [ORACLE] diye yaz:
   a) Kesirli grup sayısı: V45 (2.5 → 3 grup gibi davrandı), V46 (2.4 → 2).
      Grup alanı nasıl okunup tam sayıya çevriliyor?
   b) Gösterim: λ ve kritik F 100'ü geçince ondalıklar atılıyor (V23 λ=150,
      V39 kritik F=199.5, V47 λ=15000, V48 λ=156.06). R-15 ile tutarlı mı?
   c) Çok küçük etki V52 (f = 0.0001, güç 0.80, k = 3): G*Power N = 963468906
      ve gerçekleşen güç 0.7999999 gösteriyor; yani hedefin altında kalıyor.
      Hedefi sağlayan en küçük 3'ün katı daha küçük olmalı. Sebebi kök bulucu mu,
      F dağılımı kodunun büyük df2'deki hassasiyeti mi? Kanıtla ya da
      bilinmeyen olarak yaz.
3. Kılavuzdan [DOK] satırları ekle: λ = f²N, df1 = k − 1, df2 = N − k, kritik F
   ve güç tanımları, Cohen f eşikleri (0.10/0.25/0.40), kılavuzdaki ANOVA
   örneği. Her biri için sayfa numarası ver. Kılavuzda yazanları [REA]
   puanından çıkar (puan yalnızca kılavuzda olmayan davranışa verilir).
4. SPEC.md'yi buna göre güncelle: kurallar, Gherkin senaryoları, Bilinmeyenler
   ve Öncelikli vektörler bölümü. Kesirli grup sayısı ve V52 davranışı için
   birer kural ya da bilinmeyen satırı olsun. SPEC yeniden yazım oturumunun
   gördüğü TEK belge; içinde adres, fonksiyon adı veya kod olmasın.
5. Bitince kısa bir özet yaz: kaç [AJAN] doğrulandı, kaç tanesi yanlışlandı,
   kaç yeni [REA] satırı eklendi.

---
