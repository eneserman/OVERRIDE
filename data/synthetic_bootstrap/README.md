# SYNTHETIC bootstrapping only

Each example has `source.dataset=SYNTHETIC_COMPOSITION`, `annotation.status=SYNTHETIC_PROGRAMMATIC`, `annotation.is_gold=false`, a recipe and template family. Character span offsets are generated compositionally and tested. The dataset does not consist of actual SGD utterances. The synthetic challenge partition is a within-generator diagnostic only; **never report it as a real SGD benchmark or as final academic test**.

Regenerate: `python scripts/build_synthetic_bootstrap.py --out data/synthetic_bootstrap --seed 20261028`.
