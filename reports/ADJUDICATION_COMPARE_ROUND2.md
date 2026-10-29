# Adjudication Proposal Comparison — ROUND 2 (final proposals, both approved by their authors)
# Mechanical comparison only. No label suggestions. Final decision = joint session of the two reviewers.

Tarih: 2026-10-29 (Burak 19:05 sürümü · Enes onaylı sürüm) · Kural tabanı: v0.2.3 (G1'de mutabakat)

## 🔴 Başlık: İki tur arasında pozisyonlar yer değiştirmiş

| Konu | Burak 18:34 taslağı | **Burak 19:05 (şimdi)** | Enes önceki | **Enes şimdi** |
|---|---|---|---|---|
| **G2** | `for N`/`around` **içeri**, tek span | `for N` **bölünür**, `around` **dışarı** | `for N` bölünür, around dışarı | `for N`/`with N`/`around` **içeri**, tek span |
| T1 | A (tek) | **B (böl)** | B (böl) | **A (tek)** |
| T2 | B (around'lı) | **A (around'suz)** | A (around'suz) | **B (around'lı)** |
| T3 | A (tek) | **B (böl)** | B (böl) | **A (tek)** |
| T4 | A (tek) | **ÖZEL (böl)** | ÖZEL (böl) | **A (tek)** |
| P4 | ÖZEL artikelli | **A artikelsiz ⚠** | A artikelsiz | **ÖZEL artikelli** |
| P7 | ÖZEL (boş) | **B (it kalır)** | B (it kalır) | **ÖZEL (boş)** |
| P9 | child-friendly + a garden | **sadece a garden ⚠** | sadece a garden | **child-friendly + a garden** |

Her iki hakem de diğerinin önceki turdaki gerekçelerine bakıp konumunu değiştirmiş görünüyor.
Sonuç: **aynı maddelerde hâlâ ayrışıyorlar** — ama artık ayrışma yüzeyi çok net ve küçük.

## ✅ Bu turda KAZANILAN mutabakatlar

1. **K3 (geçen turdaki tutarsızlık) çözüldü:** Her iki teklifte de span'in **başındaki** edatlar (`on, from, until, at`) dışarıda; **değerin içindeki** edatlar (`in`, `of` — "8 in the night", "10th of March") içeride. → P3 `that date`, T2 `8 in the night` konularında mutabakat.
2. **G3/K6 — Enes kararını verdi:** Pilot 20 (`it`), Pilot 28 (`there` [100-105]), Pilot 29 (`there`) → **C3'e aykırı kabul edilmiş etiketler gold'dan kaldırılır** (RULE_REVISION). Burak'ın K6'sı hâlâ açık ama bu üç madde için Enes "evet" dedi.
3. **T5, T6, P1, P2, P3, P5, P6, P8, P10 + P9'un `a garden` kısmı** → iki teklif de aynı (toplam 9+ madde tam mutabık).

## ⚔️ KALAN FARKLAR — hepsi 3 kök soruna iniyor

### 🔴 F1 — `for N` / `with N` bütün mü bölünmüş mü? (T1, T2 hariç T3, T4 + dosyalar)
| | Burak | Enes |
|---|---|---|
| `a table for three` | `a table` + `three` (iki span) | tek span |
| `a table for four` | `a table` + `four` | tek span |
| `tickets for four people` | `tickets` + `four people` | tek span |
| `a hotel with 3 rooms` (457) | ? ("with N" netleştirilmeli diyor) | tek span |

### 🔴 F2 — `around` span'in içinde mi dışında mı? (T2)
| | Burak | Enes |
|---|---|---|
| `around 8 in the night` | `8 in the night` [68-82] | `around 8 in the night` [61-82] |

*(Bu iki karar test-363'ü de vuruyor: `around 9:30 in the morning`, `around five in the evening`, `a table for one/of one/for 3 people` ID'leri iki listenizde de var.)*

### 🟡 F3 — üç tekil teyit
| Madde | Burak | Enes | Not |
|---|---|---|---|
| **P4** | A = `small rental car` [16-32] (artikelsiz) ⚠ kendi G2'si "artikel dahil" diyor, teyit istiyor | ÖZEL = `a small rental car` [14-32] (artikelli) | Burak kendi teyidini bekletiyor — P5/P6'da artikel aldı |
| **P7** | B (`it` kalır) — K6'ya bıraktı | ÖZEL (boş; `it` G3 ile kalkar) | G3 "evet" diyen tek taraf Enes |
| **P9** | sadece `a garden` ⚠ `child-friendly` kalsın mı diye soruyor | `child-friendly` + `a garden` (anlaşmalı etiket korunur) | Burak teyit bekletiyor |

## 📌 İdari tekrarlar
- **Test çalışma kâğıdı yine "yok" denmiş** → **VAR:** `data\annotations\d3_test_adjudication\TEST363_ADJUDICATION_WORKSHEET.md` (63 madde). Yukarıdaki F1/F2'nin test ayağı orada karara bağlanacak.
- **Burak'ın "Etkilenen ID'ler" listesi** (test-363: 5 ID, 457: 3 madde) → G2 kararı kesinleşince gold üretiminde otomatik uygulanacak; ayrıca **guideline v0.2.3 change-log'una** girecek.
- **Enes'in "at least 4.2 / at least three stars" açık sorusu** hâlâ cevapsız (test worksheet K4'ünde).

## ⏭️ Birlikte çözülmesi gereken tek oturum (≈10 dk)
1. **F1:** `for N`/`with N` → **böl** mi **tek** mi? (T1, T3, T4 + 457'deki 2 madde + test-363'teki 3 ID)
2. **F2:** `around` → **içeri** mi **dışarı** mı? (T2 + test-363'teki 2 ID)
3. **F3:** P4 artikel (A mı ÖZEL mi) · P7 `it` (G3 evet mi) · P9 `child-friendly` (kalsın mı)

Bu 3 karar gelince: **guideline v0.2.3'ü rehberde change-log'la yayımlarım → 16+63 kararı gold üretimine geçiririm → train gold kapanır → D5 başlar.**
