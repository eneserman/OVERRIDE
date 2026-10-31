# JEV-alternative comparison: Laya zero-shot (protocol, written before any run)

**Status:** protocol committed before the first Laya prediction; results are appended in §5 after the runs.

## 1. Why

The course allows JEV and JEV alternatives (Laya, OpenAI Decisions, AnyJev) as "new" methods. These are *decision
models*: they read a text and answer typed questions (choice, score, yes/no) with probabilities, without generating text.
The question here: **can a general decision model, without any training on our labels, do revision-role span labeling?**
We use **Laya** (`convaiinnovations/laya`, ModernBERT-large 421M, and `laya-multilingual`, mmBERT-base 322M; Apache-2.0,
package `laya==0.4.19`) because its weights are open and run locally; Jev itself is a hosted, paid API.

## 2. Adapting a decision model to token labeling

Laya has no token head, so each word of the current user turn becomes one decision (`scripts/jev_alt_laya.py`):

- **State:** the last 4 earlier turns (`SPEAKER: utterance`) + the current turn with the target word marked `<<word>>`.
- **Question**, two fixed variants:
  - `choice`: one question "What role does the marked word play?", options UPDATE_CUE / NEW_VALUE / REFERENCE / none,
    each with a one-line description.
  - `noul`: three yes/no questions (one per label); the word takes the label with the highest probability if it is
    above 0.5, otherwise none.
- **Words → spans:** consecutive words with the same label form one span; punctuation-only words are always outside.
- Only the three claimed labels (SCOPE-001) are asked; the scorer is the unchanged strict exact-span evaluator.

Four variants = {choice, noul} × {english, multilingual}. Prompts and rules are fixed in the script before any run and
are not edited after seeing a score.

## 3. Selection without the test

Laya never sees our labels, so the **857 train-side gold records** (gold v1.3) are an unbiased place to choose the
variant: all four are scored there with `evaluate_spans.py`, and the variant with the highest S (mean of VALUE and CUE
micro-F1) is selected. The same records give the comparison with our models' pooled out-of-fold CV scores
(`D5V2_RESULTS.md`), an apples-to-apples benchmark that needs no test access.

## 4. Test access (DEV-003)

The selected variant is then run once on the 363 locked test rows and scored with `evaluate_frozen_test.py
--accept-consensus-reference`. This is a second test access, recorded as DEV-003 and in `TEST_ACCESS_LOG.md` before it
happens. It adds one comparison row; it cannot change the frozen model, its reported numbers (S 0.768) or any choice made
before, and nothing is tuned on it.

## 5. Results

(appended after the runs)
