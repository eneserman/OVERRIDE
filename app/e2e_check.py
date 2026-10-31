#!/usr/bin/env python3
"""End-to-end check of the demo site in a real browser (Playwright, Chromium).

  python app/e2e_check.py --url http://localhost:8000

Drives every page and control like a user (analyze, tabs, history switch, examples, dataset filters, model info,
language, theme, mobile layout) and fails on wrong results, broken controls, page overflow or any console error.
"""
from __future__ import annotations

import argparse
import sys

from playwright.sync_api import sync_playwright

RESULTS: list[tuple[bool, str]] = []


def check(ok: bool, what: str) -> None:
    RESULTS.append((bool(ok), what))
    print(("PASS  " if ok else "FAIL  ") + what, flush=True)


def no_overflow(page) -> bool:
    return page.evaluate("document.documentElement.scrollWidth <= document.documentElement.clientWidth + 1")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://localhost:8000")
    args = ap.parse_args()
    errors: list[str] = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1600, "height": 900})
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.goto(f"{args.url}/?lang=en&theme=light")
        page.wait_for_function("document.getElementById('st-dev').textContent !== '—'", timeout=60000)

        # start state
        check(page.is_visible("#ph"), "guide is shown before the first analysis")
        check(page.locator(".turn").count() == 2, "starts with two empty turns")
        check("Not read" in page.inner_text("#ctxnote"), "context note says history is off")

        # analyze with typed input
        turns = page.locator(".turn input")
        turns.nth(0).fill("Book a table for Friday at 6.")
        turns.nth(1).fill("Booked: Friday, 6 pm, Dolce.")
        page.fill("#utt", "Actually, make it 7 pm at the same place.")
        page.click("#go")
        page.wait_for_function("document.querySelectorAll('.rc.in').length > 0", timeout=60000)
        spans = page.evaluate("last.spans.map(s => [s.label, s.text])")
        check(["NEW_VALUE", "7 pm"] in spans, f"finds NEW_VALUE '7 pm' ({spans})")
        check(["REFERENCE", "the same place"] in spans, "finds REFERENCE 'the same place'")
        check(any(l == "UPDATE_CUE" for l, _ in spans), "finds an UPDATE_CUE")
        check(page.locator(".chip.lit").count() >= 3, "highlighted chips are drawn")
        check(page.locator(".rc").count() == 3, "three explanation cards")
        check(page.locator("#links path").count() >= 6, "arrows are drawn")
        check(not page.is_visible("#ph"), "guide hides after analysis")
        check(page.evaluate("last.history_mode") == "no", "history off uses the selected model")

        # token table
        page.click("#seg-a button[data-stage=table]")
        n_words = page.evaluate("last.words.length")
        check(page.locator("#tbody tr").count() == n_words, f"token table has one row per word ({n_words})")
        check(page.evaluate("[...document.querySelectorAll('#tbody tr td:nth-child(6)')].every(td => /^[01]\\.\\d\\d$/.test(td.textContent))"), "seed columns are numbers")
        check(page.evaluate("document.getElementById('an').classList.contains('wide')"), "table view uses the full width")

        # spans
        page.click("#seg-a button[data-stage=spans]")
        check(page.locator(".span-card").count() == len(spans), "one card per span")
        page.locator(".span-card").nth(1).click()
        check(page.locator(".span-card.sel").count() == 1 and page.locator(".seedbars i").count() == 3, "span details show three seed bars")
        page.click("#totable")
        check(page.is_visible("#st-table"), "'Show in token table' switches to the table")
        page.click("#seg-a button[data-stage=visual]")

        # history switch
        page.click("#hist")
        check("reads these turns" in page.inner_text("#ctxnote"), "context note changes when history is on")
        page.click("#go")
        page.wait_for_function("!busy && last.history_mode === 'tail60'", timeout=60000)
        check(True, "history on uses the tail60 model")
        page.click("#hist")

        # validation and keyboard
        page.fill("#utt", "")
        page.click("#go")
        check(page.inner_text("#err").strip() != "", "empty message shows an error")
        page.fill("#utt", "Sorry, change that to 2 tickets.")
        page.press("#utt", "Enter")
        page.wait_for_function("!busy && last.utt === 'Sorry, change that to 2 tickets.'", timeout=60000)
        check(True, "Enter key runs the analysis")
        status = page.evaluate("fetch('api/analyze', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({utterance:'  '})}).then(r => r.status)")
        check(status == 400, "server rejects an empty message (400)")

        # a long message still fits on one line
        page.fill("#utt", "Actually, could you please change the reservation to next Saturday at half past seven in the evening for six people at the same Italian place we talked about?")
        page.click("#go")
        page.wait_for_function("!busy && last.utt.startsWith('Actually, could')", timeout=60000)
        check(page.evaluate("(() => { const r = document.getElementById('chips'); return r.scrollWidth <= r.clientWidth + 1; })()"), "long message fits the stage")

        # no-revision example from the row
        page.locator("#ex-row .ex").nth(2).click()
        page.click("#go")
        page.wait_for_function("!busy && last.utt.startsWith('No thanks')", timeout=60000)
        check(page.evaluate("last.spans.length") == 0 and page.inner_text("#verdict").strip() != "", "'No change' shows no spans and a verdict")

        # turn controls
        page.click("#addturn")
        check(page.locator(".turn").count() == 3, "add turn")
        page.locator(".turn .who").last.click()
        check(page.locator(".turn .who").last.inner_text() in ("USER", "SYSTEM"), "speaker switch")
        page.locator(".turn").last.hover()
        page.locator(".turn .x").last.click()
        check(page.locator(".turn").count() == 2, "remove turn")
        page.click("#clear")
        check(page.locator(".turn").count() == 2 and page.input_value("#utt") == "", "clear resets the form")

        # examples page
        page.click("nav button[data-view=examples]")
        check(page.locator("#ex-body tr").count() == 8, "eight examples listed")
        page.click("#runall")
        page.wait_for_function("Object.keys(exResults).length === 8 && !document.getElementById('runall').disabled", timeout=120000)
        check(page.locator("#ex-body mark").count() > 10, "run all highlights the messages")
        check(page.inner_text("#ex-r").strip() != "—", "roles summary is filled")
        page.locator("#ex-body [data-ex='3']").click()
        page.wait_for_function("!busy && last.utt.startsWith('Is there an SUV')", timeout=60000)
        check(page.is_visible("#v-analyze"), "example opens and runs in the analyzer")

        # dataset page
        page.click("nav button[data-view=data]")
        page.wait_for_function("DS.rows && DS.rows.length > 0", timeout=60000)
        check(page.inner_text("#ds-turns") == "1,220", "dataset: 1,220 human-labeled turns")
        check(page.inner_text("#ds-labels") == "34,522", "dataset: 34,522 word labels")
        page.click("#ds-part button[data-part=test]")
        check(page.inner_text("#ds-count").startswith("363"), "dataset: test filter shows 363")
        page.click("#ds-part button[data-part=synthetic]")
        check(page.inner_text("#ds-count").startswith("1,000"), "dataset: synthetic filter shows 1,000")
        page.click("#ds-part button[data-part=human]")
        page.fill("#ds-q", "instead")
        n = int(page.inner_text("#ds-count").split()[0].replace(",", ""))
        check(0 < n < 1220, f"dataset: search narrows the list ({n})")
        page.fill("#ds-q", "")
        page.locator(".lchip[data-l=NONE]").click()
        check(page.evaluate("[...document.querySelectorAll('#ds-list .rec')].every(r => !r.querySelector('mark'))"), "dataset: 'no span' filter shows unlabeled turns")
        page.locator(".lchip[data-l='']").click()
        page.click("#ds-next")
        check(page.inner_text("#ds-page").startswith("2"), "dataset: next page")
        page.click("#ds-prev")
        page.select_option("#ds-dom", "Flights")
        check(page.evaluate("[...document.querySelectorAll('#ds-list .rec .dom')].every(d => d.textContent === 'Flights')"), "dataset: domain filter")
        page.locator("#ds-list [data-id]").first.click()
        page.wait_for_function("!busy && last && document.getElementById('v-analyze').classList.contains('on')", timeout=60000)
        check(True, "dataset record opens in the analyzer")

        # model info
        page.click("nav button[data-view=model]")
        check(page.locator("#rolechart .col").count() == 5 and page.locator("#confhist i").count() == 20, "model info charts render")
        page.click("#seg-m button[data-mtab=bench]")
        check(page.locator("#benchbody tr").count() == 7, "benchmark lists seven systems")
        check("0.768" in page.inner_text("#benchbody"), "benchmark shows the selected model's 0.768")

        # about, language, theme
        page.click("nav button[data-view=about]")
        check("Team" in page.inner_text("#v-about"), "about page")
        page.click(".lang button[data-lang=tr]")
        check(page.inner_text("nav button[data-view=analyze]") == "Analiz", "Turkish interface")
        page.click("nav button[data-view=analyze]")
        check("Değişiklik" in page.inner_text("#rcards") or page.inner_text("#worktitle") == "Modelin anlayışı", "Turkish analyzer texts")
        page.click(".lang button[data-lang=en]")
        before = page.evaluate("document.documentElement.dataset.theme")
        page.click("#theme")
        page.wait_for_timeout(2200)
        after = page.evaluate("document.documentElement.dataset.theme")
        check(before != after and page.evaluate("document.getElementById('tiles').hidden"), f"theme switch with tile animation ({before} -> {after})")

        # layouts
        for view in ("analyze", "examples", "data", "model", "about"):
            page.click(f"nav button[data-view={view}]")
            check(no_overflow(page), f"desktop: no horizontal overflow on {view}")
        page.set_viewport_size({"width": 375, "height": 812})
        for view in ("analyze", "examples", "data", "model", "about"):
            page.evaluate(f"show('{view}')")
            page.wait_for_timeout(200)
            check(no_overflow(page), f"phone: no horizontal overflow on {view}")
        errors = [e for e in errors if "400 (Bad Request)" not in e]  # the deliberate empty-message request above
        check(not errors, f"no console or page errors ({errors[:3]})")
        browser.close()
    failed = [w for ok, w in RESULTS if not ok]
    print(f"\n{len(RESULTS) - len(failed)} / {len(RESULTS)} checks passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
