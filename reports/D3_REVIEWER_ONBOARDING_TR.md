# D3 Reviewer Onboarding Rehberi (TR) — 2026-10-28

**Kimler için:** projede insan anotatör olarak görev alacak **iki kişi** + koordinatör.  
**Durum:** teknik hazırlık tamamlandı; gold **0**. Sizin etiketleriniz olmadan gold oluşmayacak — bu bilinçli bir kural.

---

## 1. Ne yapıyoruz, ne yapmıyoruz?

- Çok turlu diyaloglarda (İngilizce) son kullanıcı cümlesindeki **düzeltme ipuçlarını** ve **değerleri** etiketliyorsunuz: hangi kelime/kelime grubu bir güncellemeyi, korumayı, iptali veya geri getirmeyi ifade ediyor; hangi kelimeler yeni/eski/değişmez/değinilen değer.
- **Yapmıyorsunuz:** genel NER (yer/kişi adı değil!), diyalog durumu tahmini, model eğitimi. Sadece insan yargısı.
- **Garanti:** hiçbir yapay zekâ etiketi size "cevap anahtarı" olarak verilmeyecek; sizin kararlarınız bağımsız saklanacak.

## 2. Dosyalar (hepsi sizin makinenizde, `data/annotations/` altında)

| Paket | İçerik | Ne zaman |
|---|---|---|
| `d3_calibration_v0.1/calibration_sample.jsonl` | 10 örneklik **alıştırma** seti (train bölümü) | **ÖNCE** — birlikte tartışılır |
| `d3_merged_traindev_v0.1/reviewer_A_BLIND.jsonl` (veya B) | **457 ana örnek** (train/dev) | Kalibrasyondan sonra |
| `d3_test_packets_v0.1/reviewer_A_BLIND.jsonl` (veya B) | **363 TEST örneği** — mühürlü | **EN SON** (aşağıdaki kuralla) |

⚠️ `PRIVATE_mining_manifest.jsonl`, `PRIVATE_sampling_manifest.jsonl` ve `data/ai_suggestions/` dosyalarına **bakmayınız** — örnekleme ipuçları ve AI taslakları içerir, sizi yanıltır.

## 3. Çalışma sırası ve bağımsızlık kuralları

1. **Kalibrasyon (birlikte):** 10 örneği önce **ayrı ayrı** doldurun, sonra bir araya gelip tartışın. Amaç: özellikle **DP-1 (ret ≠ iptal)** ve **DP-2 (konu dönüşü ≠ değer geri yükleme)** kurallarını netleştirmek. Cevap anahtarı niteliğindeki açıklamalar `reports/D3_CALIBRATION_PROTOCOL.md`'de; bunlar **eğitim malzemesidir, gold değildir**.
2. **Ana paket (ayrı ayrı):** birbirinizin dosyasını açmayın, örnekleri tartışmayın. Emin olmadığınız yeri `UNCERTAIN:` ile not edin; atlamayın.
3. **Test paketi (en son, mühürlü):** train/dev bittikten ve model seçim protokolü kilitlendikten sonra doldurulur. Test içeriğini **hiçbir yerde** (model geliştirme, prompt ayarı, hata analizi) kullanmak yasaktır; test etiketleri final değerlendirmeye kadar açılmaz.
4. **Aynı örnekleri** (bir diyalogun farklı turları paketler arasında bulunabilir) doğal karşılayın; ikisi de etiketlenir, aynı parsiyonda kalır.

## 4. Etiketleme kuralları — hızlı öz

- **Span:** `[start, end)` — Python karakter ofseti, `utterance[start:end]` yazdığınız `text` ile **birebir** aynı olmalı.
- **CUE katmanı** (minimal ifade): `UPDATE_CUE` (actually/instead/change…), `KEEP_CUE` (keep/the same…), `CANCEL_CUE` (gerçek iptal!), `RESTORE_CUE` (gerçek değer geri yükleme!).
- **VALUE katmanı** (tam değer): `NEW_VALUE`, `OLD_VALUE` (sadece kullanıcı **söylüyorsa**), `KEPT_VALUE`, `REFERENCE`.
- **DP-1:** "Not now." / "No, thanks." = teklif reddi → **etiket yok**. İptal = önceki talimatı geri çekme ("cancel the booking"). 3. şahıs iptali ("çocuklarım iptal etti, 2 kişi olsun") → iptal cue DEĞİL, sadece yeni değer.
- **DP-2:** "Back to the bus tickets" = konu/görev dönüşü → **RESTORE yok**. Restore = eski bir **slot değeri** geri isteniyor ("the earlier flight was better").
- **ADD vs UPDATE:** ilk kez söylenen bilgi = ADD/NEW_VALUE; önceki değeri değiştiren = UPDATE (+ varsa OLD_VALUE).
- **Aynı katmanda çakışma yok** (farklı katmanlar çakışabilir). İlişki/işlem katmanı (`transitions`) ayrıdır.
- Her kayıt için `difficulty` (L1–L5) + gerekirse `uncertainty_notes` (`UNCERTAIN:` ile başlar).

Ayrıntı: `13_ANNOTATION_GUIDELINES.md` (R1–R12 tablosu + DP-1/DP-2).

## 5. Aracı kullanımı (önerilen)

```
python scripts/annotation_entry_helper.py --packet data/annotations/d3_merged_traindev_v0.1/reviewer_A_BLIND.jsonl --reviewer-id reviewer_A_ISIM --out data/annotations/d3_merged_traindev_v0.1/reviewer_A_filled.jsonl
```

- İfadeyi **yazarsınız**, araç ofseti hesaplar/doğrular; menü: `V` değer, `C` cue, `T` işlem, `D` zorluk, `N` not, `K` "baktım-etiketlenecek yok", `S` kaydet.
- Her örnek anında kaydedilir; `--resume` kaldığınız yerden devam ettirir. Elle JSONL düzenleme de mümkündür (ofset kurallarına uyun).
- **Süre:** ana paket ≈ 10–14 saat (457 örnek), test ≈ 8–10 saat, kalibrasyon ≈ 1 saat. Birkaç oturuma bölünebilir.

## 6. Bittikten sonra (koordinatör çalıştırır)

```
python scripts/normalize_review_packet.py --input .../reviewer_X_filled.jsonl --reviewer-id reviewer_X_ISIM --out .../reviewer_X_canonical.jsonl
python scripts/annotation_agreement.py --a .../reviewer_A_canonical.jsonl --b .../reviewer_B_canonical.jsonl --out reports/D3_AGREEMENT.json
```

Sonra **adjudication** (anlaşmazlıkların insan kararıyla çözülmesi) → `scripts/build_adjudicated_gold.py` → gold doğrulama. Komutların tamamı ve protokol: `reports/D3_GOLD_CREATION_PROTOCOL.md`.

## 7. Sık sorulacak sorular

- **"Emin değilim, ne yapayım?"** → En iyi kararınızı yazın + `UNCERTAIN: <neden>`. Emin olmamak veridir; uydurmamak esastır.
- **"AI taslaklarına bakıp kontrol edebilir miyim?"** → **Hayır.** Bağımsızlık bozulur.
- **"Örnek anlamsız görünüyor"** → Olabilir; paket bilinçli olarak zor/yanıltıcı örnekler içerir. `K` ile "etiketlenecek yok" diyebilirsiniz; bu da geçerli bir karardır.
- **"Neden 3 kişi değil?"** → İki bağımsız insan + hakem, projenin kendi kalite standardımız (kursun doğrulanmış zorunluluğu değil). Standardı koruyoruz çünkü katkının kalbi veri kalitesi.
