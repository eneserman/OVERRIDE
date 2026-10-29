# Adjudication Proposal Comparison — Burak (A) vs Enes (B)
# Mechanical comparison of the two human proposals. NO label suggestions here;
# only what each proposed and where they differ. Final decisions belong to the
# two reviewers. Frozen agreement scores are unaffected by any of this.

Tarih: 2026-10-29 · Kural sürümü: her iki teklif de **v0.2.3** (G1'de tam mutabakat)
Durum: TASLAK — iki hakem de onaylayınca ortak karar olur.

## Sonuç özeti

- **Tam mutabakat: 9 madde** → T5, T6, P1, P2, P3, P5, P6, P8, P10 (+P9 span'leri büyük ölçüde aynı)
- **Farklı karar: 6 madde** → T1, T2, T3, T4, P4, P7
- **Farkların kökü: 2 kural sorunu** (C1-a bütün-parça kuralı, "around" konumu) + 2 tekil sorun (P4 artikel, P7 kabul edilmiş etiketin kaldırılması)

## 1. Mutabık olunan maddeler (ikisi de aynı)

| # | ID | Karar | Sonuç (her iki teklifte aynı) |
|---|---|---|---|
| T5 | SGD-148b0aee03a8931e50 | B | +`NEW_VALUE "an appointment" [15-29]` (B'nin dosyası esas) |
| T6 | SGD-9c4e5c1ad86443d8f3 | B | `NEW_VALUE "a dentist appointment" [34-55]` + `REFERENCE "the same day" [59-71]` (A'daki KEPT_VALUE değil) |
| P1 | SGD-1bff672afd614f473b | B | etiket yok (soru hedefi, C4) |
| P2 | SGD-3268166bbb220be170 | B | "exciting and interesting" yok (C2) |
| P3 | SGD-500c5b88b32a42951f | A | `REFERENCE "that date" [109-118]` — "on" dışında |
| P5 | SGD-71a78f8aba48043609 | A | `NEW_VALUE "a salon" [16-23]` |
| P6 | sgd_43f2a82f62150cff9090 | A | `NEW_VALUE "a games event" [46-59]` |
| P8 | sgd_a5d726d0e27a59f5082a | B | etiket yok (C2) |
| P10 | sgd_cb84c0478ba3127132d5 | ÖZEL | yalnız `NEW_VALUE "a restaurant" [71-83]`; "there"/"near there" yok (C3) |

**P9 (sgd_a7f975950eb100c6ad18):** İkisi de "that"i kaldırıyor, ikisi de `a garden` tutuyor → span'ler mutabık. **Tek açık alt madde: transition op** (Burak'ın dosyasında UPDATE, teklifinde ADD) — Enes transition'a değinmemiş.

## 2. Farklı olan maddeler (6)

| # | ID | Burak (A) | Enes (B) | Kök neden |
|---|---|---|---|---|
| **T1** | SGD-835ec70f9e0a905054 | **A**: `NEW_VALUE "a table for three" [68-85]` (tek span) | **B**: `"a table" [68-75]` + `"three" [80-85]` (iki span) | **C1-a**: bütün mü parçalı mı |
| **T2** | SGD-4dfe44204b3234df58 | **B**: `"around 8 in the night" [61-82]` ("around" içinde) | **A**: `"8 in the night" [68-82]` ("around" dışında) | **"around" konumu** |
| **T3** | SGD-c5bd6a91af5fa668c3 | **A**: `"a table for four" [54-70]` tek span | **B**: `"a table"` + `"four"` parçalı | **C1-a** |
| **T4** | SGD-32ffc7799423754ec9 | **A**: `"tickets for four people" [50-73]` tek span | **ÖZEL**: `"tickets" [50-57]` + `"four people" [62-73]` (not: B'nin kendi dosyasında "tickets" hiç yoktu) | **C1-a** |
| **P4** | SGD-50c2d5c01ea6273bc9 | **ÖZEL**: `"a small rental car" [14-32]` (artikel dahil) | **A**: `"small rental car" [16-32]` (artikel hariç) | **Artikel** — bkz. aşağıdaki tutarlılık uyarısı |
| **P7** | sgd_667a77ce3c34f0be8dfc | **ÖZEL**: tamamen boş — kabul edilmiş `REFERENCE "it" [5-7]` de kaldırılsın (**RULE_REVISION**, C3) | **B**: yalnız `REFERENCE "it" [5-7]` kalır | **Kabul edilmiş etiketin kaderi** |

## 3. Karara bağlanması gereken KURAL sorunları

### K1 — C1-a: "for/of/with + sayı" bütün mü, parçalı mı? (T1, T3, T4)
- **Burak:** `a table for three` → **tek span** (nedir + kaç kişi tek grup değer)
- **Enes:** `a table` + `three` → **iki ayrı span** (aradaki edat hiçbir span'e girmez)
- Etki sadece 3 madde değil: Enes'in kendi listesine göre **test-363'te** ("a table for one", "a table of one") ve **239'luk sette** ("a hotel with 3 rooms") de bu kural uygulanacak → **tek karar, çok dosya etkiliyor.**

### K2 — "around/about" span'in içinde mi dışında mı? (T2)
- **Burak:** içinde (`around 8 in the night`)
- **Enes:** dışında (`8 in the night`)

### K3 — Tutarlılık uyarısı: "in" kurala giriyor ama örneklerde girmiyor
Her iki teklifte de G2, yer/zaman edatlarını (`on, from, until, at, in`) span **dışı** sayıyor — ama **T2'de ikiniz de** `8 in the night` span'ini "in" ile birlikte tutuyoruz (Burak [61-82], Enes [68-82]). Kural metni ile örnek kararı örtüşmüyor; **kural metni neye göre düzeltilecek, siz karar verin.**

### K4 — Enes'in açık sorusu: "at least 4.2" / "at least three stars"
`at` edat olarak listede; ama "at least" bir eşik ifadesi. Bu test maddeleri **63'lük test çalışma kâğıdında** — orada karara bağlanacak. Henüz karar yok.

### K5 — P4: kendi kuralınızla seçiminiz örtüşmüyor mu?
Her iki teklifte de G2 "artikel span'e dahil" diyor. Burak ÖZEL'de `a small rental car [14-32]` (dahil), Enes ise **A'yı** seçiyor; A'nın span'ı `[16-32]` = `small rental car` **artikelsiz**. İkisi aynı anda doğru olamaz — P4'te Enes'in G2 ile kendi kararı arasında bir karar gerekiyor.

### K6 — C3'ün kabul edilmiş etiketlere uygulaması (tutarlılık sorusu)
- **P7'de** Burak, ikinizin de kabul ettiği `REFERENCE "it"`'i C3 gereği kaldırmayı öneriyor (RULE_REVISION).
- **P3'te** ikinizin de kabul ettiği `REFERENCE "there" [100-105]` var ("Can you see what's happening **there**?") — aynı C3 deseni burada da geçerli mi? İkisi de tartışmamış. **Tutarlılık için karar gerekmiyor mu?**
- **P10**'da aynı desen zaten kaldırıldı ("there"/"near there" yok) → P3 ile P10'un aynı kurala aynı tepkiyi vermesi beklenir.

## 4. İdari maddeler

| Madde | Durum |
|---|---|
| **Test çalışma kâğıdı "henüz yok" notu** | **VAR:** `data\annotations\d3_test_adjudication\TEST363_ADJUDICATION_WORKSHEET.md` (63 madde, ikiniz de doldurun) |
| **DOGRULAMA_BURAK_onaylar_ENES_179.md** | Burak'ın **evet/hayır** cevabı bekleniyor (179 kaydın hepsi incelendi mi?) |
| **v0.2.3 kural metni** | Repo rehberi hâlâ **v0.2.2**'de (C1-C3). Siz C4, C6, R1-R5 gibi kurallarla çalıştınız → **o kural metinlerini bana gönderin**, rehberi v0.2.3 olarak change-log'lu şekilde güncelleyeyim (etkilenen örnek ID'leriyle, protokol gereği) |
| **Frozen skorlar** | Pilot `5e409339…`, test `36509d5f…` — bu kararlardan **etkilenmez**; sadece gold değişir |

## 5. Sıradaki adım
1. İkiniz **K1-K6** ve **6 farklı madde** üzerinde anlaşın (tek mesaj: "T1: Burak, T2: Enes, ..." formatı).
2. Kararları verdiğinde ben: guideline v0.2.3'ü repo'ya yazarım → **train gold** üretirim → **D5 eğitimi** başlar.
3. Test gold'u (63 karar + K4) ayrıca mühürlü üretilir.
