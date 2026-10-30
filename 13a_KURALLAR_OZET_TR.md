# Etiketleme kuralları — kısa Türkçe özet (guideline v0.2.3)

Bu sayfa `13_ANNOTATION_GUIDELINES.md` (v0.2.3) ve `reports/D3_ADJUDICATION_DECISIONS_FINAL.md` içindeki kuralların
özetidir; yeni kural eklemez. Çelişki olursa asıl kılavuz geçerlidir. Örnekler kılavuzdan alınmıştır,
etiketleme paketlerindeki cümlelerden değil.

## A. Çalışma kuralları

1. **Programı kullan:** bat dosyasına çift tıkla. Etiketi ve ifadeyi sen yazarsın, offset'i program hesaplar ve
   doğrular. JSON'u elle düzenleme. Kapatıp açınca kaldığın yerden devam eder.
2. **Bağımsız çalış:** diğer kişiyle kayıtları konuşma; onun dosyasına, gold dosyalarına ve `PRIVATE_*` dosyalarına bakma.
3. **AI sadece çeviri için.** AI'a etiket, offset ya da yorum yaptırma.
4. **İlk teslim puanlanır.** Dosyayı gönderdikten sonra düzeltme yapma; düzeltmeler karar sayfasında yapılır.
5. **Emin değilsen:** en iyi tahminini işaretle, not alanına `UNCERTAIN:` ile başlayan kısa bir sebep yaz. Atlama.
6. Sadece **şu anki kullanıcı cümlesindeki** ifadeleri işaretle. Önceki turlar sadece bağlam içindir.

## B. Etiketler

| Katman | Etiket | Basitçe | Kılavuzdan örnek |
|---|---|---|---|
| VALUE | `NEW_VALUE` | Kullanıcının verdiği somut değer | "Paris", "twelve in the afternoon", "San Jose" |
| VALUE | `REFERENCE` | Önceden geçen **belirli** bir değere/seçeneğe gönderme | "Book **the second option** we discussed." |
| VALUE | `KEPT_VALUE` | Açıkça korunan değer | "keep **Friday**", "Yes, I like **the same**." |
| VALUE | `OLD_VALUE` | Kullanıcının bu cümlede **söylediği** eski değer | "Paris instead of **Berlin**" |
| CUE | `UPDATE_CUE` | Açık değişiklik kelimesi | "**Actually**", "**instead of**", "**change**", "**make it**" |
| CUE | `CANCEL_CUE` | Daha önce verilen talimatı geri çekme | "**Cancel** the hotel booking." |
| CUE | `KEEP_CUE` | Açık koruma kelimesi | "**keep** Friday" |
| CUE | `RESTORE_CUE` | Önceki bir **değere** geri dönme | "**Go back to** the earlier flight." |

Aynı katmanda span'lar çakışamaz; farklı katmanlarda çakışabilir. Kayıtların yaklaşık üçte biri boştur; hiçbir şey
yoksa boş bırakmak doğru cevaptır.

## C. Sınır kuralları (C1-r, F1, F2)

- Artikel ve iyelik **içeride**: `a salon`, `a small rental car`, `a games event`.
- Baştaki edatlar **dışarıda**: `on that date` → `that date` (`on`, `from`, `until`, `at`).
- Yaklaşık ifadeler **dışarıda**: `around 8 in the night` → `8 in the night` (`around`, `about`).
- İçteki bağlayıcılar **içeride**: `8 in the night`, `10th of March`.
- Miktar **ayrılır**: `a table for three` → `a table` + `three`; `tickets for four people` → `tickets` + `four people`;
  `a hotel with 3 rooms` → `a hotel` + `3 rooms`.
- Eşik **içeride**: `at least 4.2`.
- Cue'lar en kısa tam ifade: "change", "Actually", "the same".

## D. Değer mi? (C2, C4, R11)

- Sadece **somut/belirlenebilir** değer. "some other places", "something exciting and interesting" → span yok.
- **Sorulan şey işaretlenmez**: "What's the genre?" → yok; "Does it have 1 stop?" → `1 stop` yok.
- İlk kez verilen bilgi `NEW_VALUE`, cue yok: "I would like for it to be in San Jose."

## E. REFERENCE (DP-3, C3, C6)

- Belirli bir önceki değer/seçenek olmalı. "I want to go back to **Dr. Hamblin Basil** again." ✅
- **Konuya dönüş değil**: "Back to booking tickets." ❌
- **Çıplak zamir/yer değil**: "it", "there" ❌
- Önceki gün/saate gönderme REFERENCE: revizyon olmayan cümlede "on **the same day**" → REFERENCE.

## F. UPDATE_CUE (DP-4, DP-5, R1, R2, R12)

- Sadece **açık bir değişiklik kelimesi** varsa: change, instead (of), make it, actually, I meant, on second thought…
- **Tek başına "No" cue değil**: "No, thanks", "No, that is all." → hiçbir şey.
- Değişiklik var ama kelime yoksa cue uydurma: "No, I forgot, my mother-in-law canceled, so I only need reservations
  for two." → sadece `two` NEW_VALUE.
- "Instead of the previous time, can you make it at 18:00?" → UPDATE_CUE (RESTORE değil).
- Önceki değer görünmüyorsa değişiklik varsayma: "Make it 2 people." → `2 people` NEW_VALUE, not: `UNCERTAIN:`.

## G. CANCEL_CUE (DP-1, R4, R5)

Sor: **kullanıcı daha önce verdiği bir talimatı geri mi çekiyor?**
- "Not now." / "No, not now. Thanks." / "Yes but not now" → teklifi reddetme/erteleme → **CANCEL yok**.
- "Cancel the hotel booking." / "Forget that, don't book it" → CANCEL_CUE (az görülür).
- "Can I get a refund if I decide to cancel?" → varsayım, hiçbir şey.
- "My kids cancelled, I only need 2" → başkasının iptali; söylenmişse `2` NEW_VALUE, CANCEL yok.

## H. RESTORE_CUE (DP-2, R7, R8)

Sor: **bir değer eskiye mi dönüyor, yoksa sadece eski konuya mı dönülüyor?**
- "Back to the bus tickets, I'll need 4 tickets." → konuya dönüş, **RESTORE yok**; `4 tickets` NEW_VALUE.
- "I need to head back to Chicago on the 9th" → yolculuk anlamı, RESTORE yok.
- "Go back to the earlier flight." / "Actually the first one was better." → RESTORE_CUE (çok az görülür).
- Nesne bir **görev** ise ("tickets", "reserving rooms") RESTORE değildir. Emin değilsen hiçbirini işaretleme, `UNCERTAIN:` yaz.

## I. KEEP_CUE / KEPT_VALUE (R9, R10)

- "keep looking", "keep searching" → aramaya devam, **KEEP yok**.
- "Yes, I like the same." → `the same` KEPT_VALUE, KEEP_CUE yok.
- "Actually Paris, but keep Friday." → `keep` KEEP_CUE + `Friday` KEPT_VALUE.
- "keep everything else" → `keep` KEEP_CUE, uydurma değer yok.

## J. OLD_VALUE

Sadece kullanıcı eski değeri **bu cümlede söylüyorsa**: "Actually, Paris instead of Berlin" → `Berlin` OLD_VALUE,
`Paris` NEW_VALUE, `instead of` UPDATE_CUE.

## K. Her cümle için 30 saniyelik kontrol

1. Somut değer var mı? → NEW_VALUE (C bölümündeki sınırlar).
2. Belirli bir önceki değere gönderme var mı (zamir değil, konu değil)? → REFERENCE.
3. Açık değişiklik kelimesi var mı ("No" tek başına sayılmaz)? → UPDATE_CUE.
4. Önceki talimat geri çekiliyor mu ("not now" sayılmaz)? → CANCEL_CUE.
5. Önceki değere dönülüyor mu (konuya dönüş sayılmaz)? → RESTORE_CUE.
6. Açık "keep/same" var mı ("keep looking" sayılmaz)? → KEEP_CUE / KEPT_VALUE.
7. Hiçbiri yoksa boş bırak.
