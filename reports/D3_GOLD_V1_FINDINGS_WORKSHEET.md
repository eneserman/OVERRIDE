# Gold v1 — Mekanik v0.2.3 Bulguları (ORTAK KARAR SAYFASI)

**Durum: KARAR BEKLİYOR (Burak + Enes, ortak).** Hazırlanma: 2026-10-30, koordinatör.
Kaynak: `train_dev_gold_v1.jsonl` üzerinde salt-okunur kural taraması (C1-r, F1, F2,
C3/G3, kenar boşluğu, noktalama, aynı metin–farklı etiket). 457 kayıtta yalnızca
aşağıdaki 4 span işaretlendi. **Tarama sadece aday gösterir, karar vermez.**
Koordinatör etiket önermiyor; her satırda yalnızca ilgili kuralın yazılı metni var.

Bu 4 kayıt kör denetim örnekleminden önceden çıkarıldı (`D3_GOLD_V1_AUDIT_PROTOCOL.md` §2).
Kararlar `D3_GOLD_V1_1_DECISIONS.md` dosyasına yazılır; gold v1 dosyası değiştirilmez.

---

### B1 — `SGD-7bb4b2f1283e503502` (Enes tek kişi, Burak doğruladı)
- **Cümle:** "I would need to get a hotel with 3 rooms when I get there."
- **Gold v1:** NEW_VALUE `a hotel with 3 rooms` [20-40]
- **İlgili kural (F1):** "`for/of/with + N` quantities are **split**: `a table` + `three`, `tickets` + `four people`, `a hotel` + `3 rooms`."
- **Karar:** ☐ olduğu gibi kalsın ☐ değiştir → yeni span(lar): ____________ ☐ not: ______

### B2 — `sgd_f90ea0abaea8773c2149` (Burak tek kişi, Enes doğruladı)
- **Önceki kullanıcı turu:** "We are a group of three"
- **Cümle:** "No, we are a group of 2 and i like a regular ride."
- **Gold v1:** NEW_VALUE `a group of 2` [11-23] · NEW_VALUE `a regular ride` [35-49]
- **İlgili kural (F1):** yukarıdaki `for/of/with + N` metni. (`a group of 2` kalıbı kural örneklerinde yok — kapsamda olup olmadığı sizin kararınız.)
- **Karar:** ☐ olduğu gibi kalsın ☐ değiştir → yeni span(lar): ____________ ☐ kuralın kapsamı netleştirilsin: ______

### B3 — `sgd_3324bf1e7d2ec8ca4acf` (Burak tek kişi, Enes doğruladı)
- **Önceki sistem turu:** "Yup, there is another bus that leaves at 7:40 am and it has 0 transfers. …"
- **Cümle:** "Do you have any other buses available on the same day?"
- **Gold v1:** KEPT_VALUE `the same day` [41-53]
- **İlgili kural (C6):** "a reference to a previously mentioned day/time is `REFERENCE`, not an update: `on the same day` in a non-revision sentence → `REFERENCE`."
- **Karar:** ☐ olduğu gibi kalsın ☐ değiştir → etiket: ____________ ☐ not: ______

### B4 — `SGD-90cfacf6a275f8d7f3` (Burak tek kişi, Enes doğruladı)
- **Önceki sistem turu:** "I'm sorry. I wasn't able to make a reservation. Is there any other places you'd want to try?"
- **Cümle:** "Let's try Jojo restaurant the same day at afternoon 1. Let's just make it for three people though."
- **Gold v1:** NEW_VALUE `Jojo restaurant` [10-25] · KEPT_VALUE `the same day` [26-38] · NEW_VALUE `afternoon 1` [42-53] · UPDATE_CUE `make it` [66-73] · NEW_VALUE `three people` [78-90]
- **İlgili kural:** C6 (yukarıda; "non-revision sentence" koşulu) ve R10 ("Explicit retention … → `KEPT_VALUE`"). Gold v1'deki diğer 3 `the same day` span'ı REFERENCE (T5, T6 kararları dahil).
- **Karar:** ☐ olduğu gibi kalsın ☐ değiştir → etiket: ____________ ☐ not: ______

---

**Etki notu (sayım, öneri değil):** gold v1'de toplam 4 KEPT_VALUE var; B3 ve B4 bunların 2'si.

**İmza (ortak):** reviewer_A_BURAK ________ · reviewer_B_ENES ________ · Tarih: ________
