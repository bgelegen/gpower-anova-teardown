# Oturum 1 · Söküm — ilk prompt

> Bu dosya, Oturum 1'in ilk mesajının **birebir** kopyasıdır. `Oturum1-ac.bat`
> Claude Code'u repo klasöründe yeni bir oturumla açar ve aşağıdaki iki çizgi
> arasındaki metni ilk mesaj olarak verir.

---

Sen bir temiz oda tersine mühendislik çalışmasının **inceleme (söküm)** tarafısın.
Ders: YZM301 Yazılım Gerçekleme ve Test, Teardown Sprint. Hedef yazılım ücretsiz,
akademik bir araçtır ve incelemesi ders kapsamında verilmiştir.

**Hedef:** G*Power 3.1.9.7 (Windows), yalnızca şu hesap:
*F tests → ANOVA: Fixed effects, omnibus, one-way*, a priori ve post hoc modları.

- Binary: `C:\Users\batuh\YZM301-araclar\gpower\acilmis\GPower_3.1.9.7_143\GPowerNT.exe`
- SHA-256: `c63e6a133eb6372932f810c08cc33dc35a06d1ddb658f897bd6c34a754efc812`
  — işe başlamadan önce hash'i doğrula; farklıysa dur ve bana söyle.
- Araçlar: REA MCP araçları ve Ghidra sağlayıcısı. Başka araç indirme veya kurma.

**Senin üreteceğin dosyalar yalnızca ikisi:** `SPEC.md` ve `LEDGER.md`
(şablonları repoda). `src/` ve `tests/` klasörlerine **dokunma**, kod yazma.

### Kurallar

1. **Decompile kodu hiçbir repo dosyasına girmez.** Ghidra projesini ve ham
   çıktıları repo DIŞINDA tut: `C:\Users\batuh\YZM301-araclar\ghidra-proje\`.
   LEDGER'da yalnızca fonksiyon adı/adresi + davranışın bir cümlelik tarifi olur.
2. **SPEC.md yalnızca gözlenebilir davranışı anlatır.** Yeniden yazım oturumu
   yalnızca SPEC.md'yi görecek; içinde kod, adres veya fonksiyon gövdesi olmasın.
   Formüller matematik olarak yazılabilir.
3. **Her iddiayı etiketle:**
   - `[DOK]` kılavuzda/makalede yazıyor (sayfa ver),
   - `[REA]` binary'de gördün ve kılavuzda yok (iz ver),
   - `[AJAN]` çıkarım, kod izi yok → “diferansiyel testle sınanmalı” yaz.
   Emin değilsen `[AJAN]` de; `[REA]` etiketini kanıtsız kullanma.
4. Her SPEC kuralı (`R-xx`) en az bir LEDGER satırına (`L-xx`) ve bir oracle
   vektörüne (`oracle/gpower_gui_vectors.csv`, `V-xx`) bağlanır.
5. Beklenen sayısal değerleri sen üretme; onları G*Power GUI'si (oracle) verir.

### Cevaplanacak sorular (puan kılavuzda OLMAYAN davranışlardan gelir)

1. λ, df1, df2 ve kritik F nasıl kuruluyor? (kılavuzla tutarlı mı)
2. A priori modda N nasıl aranıyor: başlangıç değeri, adım, **durma koşulu**,
   en fazla iterasyon, yakınsamazsa ne oluyor?
3. **N yuvarlama:** hangi yönde, neye göre? Tam sayıya mı, grup sayısının
   katına mı? Grup başına dağılım nasıl?
4. Minimum N / alt sınır var mı? (çok büyük f)
5. Çok küçük f'de (0,01–0,05) tavan, taşma veya zaman aşımı var mı?
6. Gösterim hassasiyeti: her çıktı alanı kaç ondalıkla, yuvarlama mı kesme mi?
7. **Geçersiz girdiler:** f ≤ 0, α ∉ (0,1), güç ∉ (0,1), güç ≤ α, k < 2,
   post hoc'ta N ≤ k — her biri için davranış ve mesaj metni.
8. Post hoc'ta N grup sayısına bölünmüyorsa ne oluyor?

### Çalışma biçimi

- Önce kısa bir plan yaz, sonra onay beklemeden başla.
- Her bulguyu bulduğun anda LEDGER.md'ye ekle; sonda topluca yazma.
- Oturum sonunda SPEC.md'nin “Bilinmeyenler” tablosunu doldur ve hangi oracle
  vektörlerinin önce G*Power'da girilmesi gerektiğini listele.

---
