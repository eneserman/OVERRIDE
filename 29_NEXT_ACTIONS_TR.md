# 29 — OVERRIDE v0.8: IDE'ye gönderim ve yapılacaklar

**Bu ZIP, akademik araştırma için geliştirme paketidir; bitmiş proje ya da kesin güvenilir gold veri değildir.**

### IDE'ye ilk komut
"Bu arşivi aç. Önce `27_V08_AGENT_RESEARCH_HANDOFF.md`, `28_V08_EVIDENCE_AUDIT.md`, `24_EXTERNAL_DATASET_RESEARCH.md`, `26_PROSPECTIVE_TEST_PREREGISTRATION.md`, `AGENT_MASTER_PROMPT.md` oku. İnternetten gerçek veri edinmeden gold/test sonucu uydurma; sentetik skorları gerçek performans olarak sunma. Aşamaları D0–D7 olarak kalite kapılarından geçirerek uygula. Her aşamanın commit'i, terminal çıktısı, dosya hash'i ve başarısızlık nedeni raporda olsun."

### Kaynaklar
- SGD: `git clone https://github.com/google-research-datasets/dstc8-schema-guided-dialogue.git data/upstream/sgd` → pin HEAD / hash
- `python scripts/inspect_upstream_provenance.py --sgd-root data/upstream/sgd --out reports/SGD_PROVENANCE.json`
- Microsoft Frames: resmî Microsoft Research sayfasından izin ve kullanım koşullarını kabul ederek **elle** edin. İngilizce kullanıcı mesajlarını `scripts/extract_frames_candidates.py` ile ANOTASYON ADAYI olarak çıkar; otomatik gold üretme.
- Önceden AI'nın gördüğü 100 SGD train örneğini hiçbir şekilde prospektif kör ana test olarak kullanma.

### Gerçek test protokolü
- Farklı resmî SGD dev/test diyaloglarından yeni ve daha önce görülmemiş adayları çıkar.
- `python scripts/lock_prospective_holdout.py --pool data/review/NEW_UNLABELED_TEST_POOL.jsonl --seen data/sgd_pilot/annotator_A_UNLABELED.jsonl --out data/prospective_holdout/sgd_raw_lock.json --source-commit-sha <ACTUAL_GIT_SHA> --license-status VERIFIED`
- Yukarıdaki `<ACTUAL_GIT_SHA>` metnini uydurma; `git rev-parse HEAD` çıktısını kullan.
- Örnekleme kurallarını sonradan metriğe göre değiştirme; test kümesinin gold etiketleri gerçek kişilerce bağımsız incelenmeli.
- Frames korpusu için `--source-release-id` ile resmî release kaydı kullan; git SHA uydurma.

### Eğitim ve bilimsel sonuç
- İlk rapordaki çalıştırılmış sentetik baseline gerçek akademik başarı değil. Model geliştirme D5'te gerçek kod, gerçek gold ve sabit seed gerektirir.
- Yalnızca doğrulanmış gerçek holdout üzerinde exact-span F1 ve per-class support ilan et. Gerçek model eğitiminden sonra kaydet, kodla tekrar üretilebilir olsun.
- Published SOM-DST / TripPy MultiWOZ JGA skorları OVERRIDE token span F1 ile doğrudan kıyaslanmaz.
- İnsan doğrulaması mümkün değilse projeyi dürüstçe **weakly supervised/AI-assisted exploratory research** olarak sınırlı sun; yüksek güvenilirlik iddiasını çıkar.
