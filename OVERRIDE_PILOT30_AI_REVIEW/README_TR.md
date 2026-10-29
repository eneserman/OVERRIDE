# OVERRIDE Pilot-30 — AI-assisted single review

Bu dosya **tek bir AI tarafından** mevcut mesaj ve geçmişi kontrol ederek hazırlanmış 30 örneklik anotasyon taslağıdır. İki bağımsız insan değerlendirmesi değildir; `human_gold=0` ve insan inter-annotator agreement hesaplanamaz.

- `PILOT30_AI_REVIEW_v021.jsonl`: Orijinal kayıtları korur; 30 örneğin tamamı `AI_DRAFT` statüsündedir. `human_verified=false`, `gold_eligible=false`.
- `PILOT30_DECISION_REVIEW.csv`: Her örneğin kararı, span ve kısa gerekçesi.
- `QA_SUMMARY.json`: Teknik doğrulama ve sınıf dağılımı.

**Kullanım sınırı:** Bu verileri `data/ai_suggestions/` gibi ayrı bir klasörde tutun. Gerçek insan anotasyonu, hakem kararı, kör değerlendirme, gold veri veya insan anlaşması skoru olarak raporlamayın. Kullanılacaksa çalışma yönteminde AI-assisted annotation olarak açıkça belirtin.

**Sınırlama:** DP-3, DP-4 ve DP-5 kararları konuşmada tarif edilen v0.2.1 rehber değişikliklerine göre yorumlandı. Agent'ın güncel dondurulmuş rehber dosyası bu turda paylaşılmadığından birebir metin karşılaştırması yapılmadı. `transitions` boş bırakıldı; doğrulanmamış durum geçişleri oluşturulmadı. `UNCERTAIN:` olan kayıtlar özellikle ayrıca incelenmelidir.
