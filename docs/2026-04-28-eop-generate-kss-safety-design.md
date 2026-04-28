# /eop-generate KSS safety — design

**Issue:** [#5 — KSS auto-fill fails silently when KSS has more rows than pricing.md](https://github.com/Lutherwaves/eopowers/issues/5)
**Skill touched:** `skills/eop-generate/SKILL.md`
**Date:** 2026-04-28

## Problem

`/eop-generate` writes the КСС Excel template by fuzzy-matching row descriptions to entries in `pricing.md`. Two failure modes are silent and can disqualify the offer:

1. **Unmapped rows.** КСС templates routinely contain rows with no counterpart in `pricing.md` (administrative items, protocols, нашите номинални позиции). The current loop skips them — they ship at 0.00 — and the offer is rejected as incomplete.
2. **Over-prognoza totals.** Nothing checks the filled total against the прогнозна стойност from `analysis.md`. Totals above prognoza are an automatic disqualification.

## Guiding principle

`/eop-generate` is a **renderer, not a pricer.** Anything that would have generation make a pricing decision must instead halt and bounce back to `/eop-price`.

## Counter-proposal (vs. the four fixes in #5)

| #5 proposed              | This design                                                                                          |
|--------------------------|------------------------------------------------------------------------------------------------------|
| 1. Pre-fill row dump     | Build mapping plan in memory; surface only **unmapped + ambiguous matches** as a decision table.    |
| 2. Default unmapped to 1.00 EUR | **Halt on unmapped.** Per-row explicit resolution (price / map to existing item / mark N/A). No defaults. |
| 3. Auto-reduce highest line to fit prognoza | **Hard stop.** Report overage; refuse to write `kss-filled.xlsx`; instruct user to re-run `/eop-price` with corrected ceiling. |
| 4. Flatten ZIP files     | **Drop.** `os.walk()` already handles nested paths. Flattening mutates user files for no real bug.   |

## Flow change in `skills/eop-generate/SKILL.md` § "Попълване на КСС"

Replace the single-pass fill loop with three phases:

### Phase A — Build mapping plan (in memory, no writes)

For every row with description + quantity, classify:

- **matched** — exactly one pricing item normalises into the description (or vice-versa).
- **ambiguous** — multiple pricing items match. Surface for user pick.
- **unmapped** — no pricing item matches.

### Phase B — Resolve before write

If any rows are `ambiguous` or `unmapped`, **stop before writing**. Show a structured table:

```
Row | Description (truncated)         | Qty | Status     | Suggestions
----|---------------------------------|-----|------------|-----------------------------
 14 | Разкачане и закачане ...        |   2 | unmapped   | (none)
 27 | Кабел СВТ 3х2.5                 |  60 | ambiguous  | "Кабел СВТ 3x2.5 м" / "...мм²"
```

For each row, ask the user one of:

- supply a unit price (and a one-line rationale that gets written to `pricing.md` as a new entry)
- pick one of the suggested pricing items (resolves ambiguous)
- mark non-applicable — row is left blank and noted in offer cover letter as "не подлежи на остойностяване"

The skill writes resolutions back to `pricing.md` so the next run is clean.

### Phase C — Write + total-cap check

After all rows resolved, compute total. Read `прогнозна стойност` from `analysis.md`.

- `total ≤ prognoza` → write `kss-filled.xlsx`, done.
- `total > prognoza` → **do not write the file.** Print:

  ```
  ⚠️ КСС total {total:.2f} лв. exceeds прогнозна стойност {prognoza:.2f} лв. by {overage:.2f} лв. ({pct:.2f}%)
  Re-run /eop-price <id> with target ceiling {prognoza:.2f} and regenerate.
  ```

  Exit non-zero so it's obvious in CI/scripts.

## Out of scope

- Pricing-strategy logic (live in `/eop-price`).
- ZIP path flattening (#5 fix 4).
- Auto-creating `pricing.md` entries for unmapped rows without user input.

## Test plan

Manual on one real ~80-row КСС that previously triggered the bug:

1. КСС with 3 unmapped rows → skill halts, table shown, user resolves, file written.
2. КСС that fits prognoza → no halt, file written.
3. КСС that exceeds prognoza by 5 лв → skill refuses to write, instructs re-run of `/eop-price`.
4. КСС fully matched, total OK → no behavioural change vs today.

No automated tests — skill is markdown executed by Claude; behaviour is verified by reproducing on a real order.

## Files changed

- `skills/eop-generate/SKILL.md` — rewrite § "Попълване на КСС" (≈ lines 143–179) with the three-phase flow.

No new files. No new dependencies.
