# /eop-generate KSS safety — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the silent single-pass KSS fill in `/eop-generate` with a three-phase flow (plan → resolve → write+cap-check) so unmapped rows and over-prognoza totals halt instead of producing invalid offers.

**Architecture:** `skills/eop-generate/SKILL.md` is a markdown spec executed by Claude inline — there is no compiled code and no automated test harness. The implementation is a rewrite of one section of that markdown, with embedded Python snippets Claude runs at execution time. Verification is manual reproduction on a real eop.bg order.

**Tech Stack:** Markdown (Claude Code skill), Python 3 (openpyxl) embedded as heredoc snippets. No new dependencies.

**Spec:** `docs/2026-04-28-eop-generate-kss-safety-design.md`
**Issue:** [#5](https://github.com/Lutherwaves/eopowers/issues/5)

---

## Files

- **Modify:** `skills/eop-generate/SKILL.md` — rewrite § "4. Попълване на КСС" (lines ~143–179). No other files touched.
- **Modify (in same edit):** Section "## Чеклист" near top — replace the single "Попълване на КСС (ако има)" bullet with three sub-bullets reflecting the new phases.

No new files. No tests file (skill is markdown).

---

### Task 1: Rewrite § "Попълване на КСС" with three-phase flow

**Files:**
- Modify: `skills/eop-generate/SKILL.md` (replace lines 143–179, the entire § 4 block ending before `## 5. Подпис и печат блок`)

- [ ] **Step 1: Read current section to confirm exact line range**

Run: `sed -n '143,179p' skills/eop-generate/SKILL.md`
Expected: shows the `## 4. Попълване на КСС (ако има XLSX)` heading down through the closing `Ако няма КСС/XLSX файл, пропусни тази стъпка.` line.

- [ ] **Step 2: Replace § 4 with the new three-phase block**

Use the Edit tool. `old_string` is the entire current § 4 block beginning at `## 4. Попълване на КСС (ако има XLSX)` and ending at `Ако няма КСС/XLSX файл, пропусни тази стъпка.`. `new_string` is:

````markdown
## 4. Попълване на КСС (ако има XLSX)

Ако няма XLSX файл в шаблоните, пропусни тази стъпка.

`/eop-generate` е **рендерер, не калкулатор**. Не взимай ценови решения тук — върни към `/eop-price` ако нещо не пасва.

Изпълни КСС попълването в три фази. Не записвай `kss-filled.xlsx` преди фаза C да премине.

### Фаза A — Изграждане на mapping plan (без записи)

Прочети КСС в паметта. За всеки ред с описание + количество класифицирай в една от три категории срещу `pricing.md`:

- **matched** — точно един `pricing.md` запис се нормализира в описанието (или обратно, substring containment след `normalize`).
- **ambiguous** — два или повече `pricing.md` записа пасват.
- **unmapped** — никой запис не пасва.

```python
python3 << 'PYTHON_SCRIPT'
from openpyxl import load_workbook
import re, json

def normalize(text):
    return re.sub(r'\s+', ' ', str(text or '')).strip().lower()

wb = load_workbook('path/to/kss-template.xlsx')
ws = wb.active

# pricing_items: списък с {'description': str, 'unit_price': float} от pricing.md
plan = []  # [{'row': int, 'desc': str, 'qty': float, 'status': str, 'matches': [...]}]
for row in range(2, ws.max_row + 1):
    desc = ws.cell(row=row, column=2).value
    qty = ws.cell(row=row, column=4).value
    if not (desc and qty):
        continue
    nd = normalize(desc)
    matches = [p for p in pricing_items
               if normalize(p['description']) in nd or nd in normalize(p['description'])]
    if len(matches) == 1:
        status = 'matched'
    elif len(matches) > 1:
        status = 'ambiguous'
    else:
        status = 'unmapped'
    plan.append({'row': row, 'desc': str(desc)[:60], 'qty': qty, 'status': status, 'matches': matches})

print(json.dumps(plan, ensure_ascii=False, indent=2, default=str))
PYTHON_SCRIPT
```

### Фаза B — Резолюция на ambiguous + unmapped

Ако `plan` съдържа ambiguous или unmapped редове, **спри преди запис**. Покажи структурирана таблица със само тези редове (не всичките):

```
Row | Description (60 chars)                                     | Qty | Status     | Suggestions
----|------------------------------------------------------------|-----|------------|----------------------------------
 14 | Разкачане и закачане на инсталации                         |   2 | unmapped   | (нито една)
 27 | Кабел СВТ 3х2.5                                            |  60 | ambiguous  | "Кабел СВТ 3x2.5 м" / "...мм²"
```

За **всеки** такъв ред питай потребителя точно един от:

1. **Дай ед. цена + кратка обосновка** — записва се нов ред в `pricing.md` (description = текстът от КСС, unit_price = въведената цена) и planът се обновява до `matched`.
2. **Избери една от предложените позиции** (само за ambiguous) — planът се обновява до `matched` с този pricing item.
3. **Маркирай като неприложима** — редът ще остане празен; добави в края на офертата (мотивационно писмо) бележка: `"Ред [N] '[описание]' не подлежи на остойностяване — позицията не е част от обхвата."`

Не предлагай default стойност (1.00 EUR или каквото и да е). Не приемай Enter без избор.

След цикъла, ако някой ред все още е ambiguous/unmapped → не продължавай към фаза C.

### Фаза C — Запис + проверка на тавана

Изчисли общата сума и сравни с прогнозната стойност от `analysis.md`.

```python
python3 << 'PYTHON_SCRIPT'
total = 0.0
for entry in plan:
    if entry['status'] == 'matched':
        price = entry['matches'][0]['unit_price']
        ws.cell(row=entry['row'], column=5).value = price
        ws.cell(row=entry['row'], column=6).value = float(entry['qty']) * price
        total += float(entry['qty']) * price
    # 'non-applicable' редове остават празни

# Прочети прогнозна стойност от analysis.md (поле "Прогнозна стойност")
prognoza = 12345.67  # parse from analysis.md

if total > prognoza:
    overage = total - prognoza
    pct = overage / prognoza * 100
    print(f"⚠️ КСС total {total:.2f} лв. надвишава прогнозна стойност {prognoza:.2f} лв. с {overage:.2f} лв. ({pct:.2f}%)")
    print(f"Файлът kss-filled.xlsx НЕ е записан.")
    print(f"Изпълни /eop-price <id> с целеви таван {prognoza:.2f} и стартирай /eop-generate отново.")
    raise SystemExit(2)

wb.save('path/to/kss-filled.xlsx')
print(f"✓ КСС записан. Total: {total:.2f} лв. (под прогнозна {prognoza:.2f}).")
PYTHON_SCRIPT
```

Ако скриптът излезе с код 2, **не записвай** `kss-filled.xlsx` и не продължавай към следващата стъпка от чеклиста.
````

- [ ] **Step 3: Update the top-level checklist (lines ~20–28)**

Use the Edit tool. Replace the single line:

```
- [ ] Попълване на КСС (ако има)
```

with:

```
- [ ] КСС фаза A — mapping plan (matched/ambiguous/unmapped)
- [ ] КСС фаза B — резолюция на ambiguous/unmapped редове
- [ ] КСС фаза C — запис + проверка срещу прогнозна стойност
```

- [ ] **Step 4: Sanity-check the file**

Run: `wc -l skills/eop-generate/SKILL.md && grep -n "Фаза [ABC]" skills/eop-generate/SKILL.md`
Expected: file is longer than the original 206 lines, three "Фаза" headings appear in order.

- [ ] **Step 5: Commit**

```bash
git add skills/eop-generate/SKILL.md
git commit -m "$(cat <<'EOF'
fix(eop-generate): three-phase KSS fill with halt on unmapped + over-prognoza

Closes #5.

- Phase A: build mapping plan in memory (matched/ambiguous/unmapped)
- Phase B: halt and require explicit per-row resolution; no 1.00 EUR default
- Phase C: refuse to write kss-filled.xlsx if total > прогнозна
EOF
)"
```

---

### Task 2: Manual verification on a real order

The skill executes inside Claude Code on the user's machine; there is no automated harness. Verify by reproducing the original failure.

**Files:** none (verification only).

- [ ] **Step 1: Pick a real order with a known multi-row КСС**

Use the order that surfaced #5 (the ~80-row КСС with administrative rows). Ensure `eopowers/offers/<id>/analysis.md` and `pricing.md` already exist; if not run `/eop-analyze <id>` and `/eop-price <id>` first.

- [ ] **Step 2: Run /eop-generate <id> and confirm Phase A output**

Expected: a JSON-shaped plan is printed showing each КСС row with `status` ∈ {matched, ambiguous, unmapped}. The administrative rows that previously shipped at 0.00 must appear with `status: unmapped`.

- [ ] **Step 3: Confirm Phase B halts and prompts**

Expected: the skill stops before writing `kss-filled.xlsx`, prints the unmapped/ambiguous table, and asks per-row for resolution. Confirm pressing Enter without an explicit choice does **not** advance.

- [ ] **Step 4: Resolve all rows, confirm Phase C writes**

Resolve each row (price / pick / mark non-applicable). Expected: `kss-filled.xlsx` is written, total ≤ прогнозна, "✓ КСС записан" line printed.

- [ ] **Step 5: Force the over-prognoza branch**

Edit one resolved unit price upward so total exceeds прогнозна by ~5 лв. Re-run. Expected: skill prints the warning, exits without writing `kss-filled.xlsx`, instructs to re-run `/eop-price`.

- [ ] **Step 6: Record results in PR description**

Capture (redacted) console output for steps 2, 3, 5 and paste into the PR body under "How was this tested?". No client-identifying data.

---

### Task 3: Open PR closing #5

**Files:** none (PR metadata only).

- [ ] **Step 1: Push branch**

Branch name: `fix/eop-generate-kss-safety`.

```bash
git checkout -b fix/eop-generate-kss-safety
git push -u origin fix/eop-generate-kss-safety
```

- [ ] **Step 2: Create PR**

```bash
gh pr create --title "fix(eop-generate): three-phase KSS fill (closes #5)" --body "$(cat <<'EOF'
## Summary
- Replaces silent single-pass КСС fill with three phases: mapping plan, resolve, write+cap-check
- Halts on unmapped/ambiguous rows instead of shipping 0.00 or guessing 1.00 EUR
- Refuses to write `kss-filled.xlsx` if total > прогнозна — bounces back to `/eop-price`

Closes #5. Spec: `docs/2026-04-28-eop-generate-kss-safety-design.md`.

## Type of change
- [x] Bug fix

## Areas touched
generate

## How was this tested?
Manual reproduction on the original ~80-row КСС that triggered #5. See Task 2 of the implementation plan; redacted console output below.

[paste redacted output from Task 2 here]

## Checklist
- [x] Linked to issue #5
- [x] Skill docs updated (SKILL.md is the doc)
- [x] Tested end-to-end on at least one real order
- [x] No client-identifying data in commits or screenshots

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

- [ ] **Step 3: Confirm PR passes the ruleset**

The `Protect main` ruleset requires 1 approving review. Self-review/admin-merge is acceptable per project owner discretion.

---

## Notes

- The skill's КСС column indices (description=2, qty=4, price=5, total=6) are unchanged — they reflect the typical Bulgarian КСС layout used in `/eop-analyze` output. If a future КСС has different columns, that's a separate issue.
- `pricing.md` parsing for new entries written in Phase B is whatever shape `/eop-price` already produces; this plan assumes append-compatible markdown and does not change the schema.
