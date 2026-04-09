# eopowers — Domain-Configurable EOP Plugin

**Date:** 2026-04-09
**Status:** Approved
**Repo:** Lutherwaves/eopowers (renamed from Lutherwaves/bloxpowers)

## Summary

Rename the plugin from bloxpowers to eopowers, and extract all construction-specific logic into a domain configuration layer. The plugin ships with a construction preset but supports any procurement domain via configurable keywords, CPV codes, metrics, pricing structure, and profile fields. Domain selection happens during the `/init` onboarding flow.

## Problem

The plugin hardcodes construction-specific data across 4 skills:
- `eop-scan`: CPV codes (45xxx), keywords (СМР, топлоизолация), area extraction regex (ЗП/РЗП), EUR/m² threshold
- `eop-price`: construction trades (зидар, мазач), Stara Zagora suppliers (Bagira, HomeMax), КСС references
- `pricing-guide.md`: daily rates, material markups, supplier list — entirely construction
- `init`: profile template assumes equipment/vehicles/construction ISO certs

This makes the plugin unusable for IT services, medical supplies, consulting, or any non-construction domain.

## Design

### 1. Rename: bloxpowers → eopowers

All references change:

| What | Old | New |
|------|-----|-----|
| Repo | `Lutherwaves/bloxpowers` | `Lutherwaves/eopowers` |
| Plugin name | `bloxpowers` | `eopowers` |
| Working dir | `./bloxpowers/` | `./eopowers/` |
| Skill prefix | `bloxpowers:*` | `eopowers:*` |
| Plugin manifests | `name: "bloxpowers"` | `name: "eopowers"` |

### 2. Domain Config File

Generated during init, lives at `./eopowers/domain.md`. All skills read from this path.

#### Structure

```markdown
# Домейн: [name]

## Търсене (eop-scan)

### Ключова дума за филтър
[primary search keyword for eop.bg]

### Положителни ключови думи
| Категория | CPV кодове | Ключови думи |
|-----------|-----------|--------------|
| [cat1] | [codes] | [keywords] |

### Отрицателни ключови думи
| Категория | Ключови думи |
|-----------|--------------|
| [cat1] | [keywords] |

### Приоритет при множество категории
[ordered list: cat1 > cat2 > cat3 > останалите]

## Метрики

### Основна метрика
- Име: [human-readable name]
- Кратко име: [abbreviation for table headers]
- Единица: [unit]
- Regex: [extraction pattern]
- Минимална стойност: [sanity floor]

### Допълнителна метрика (optional, repeatable)
- Име: [name]
- Кратко име: [abbr]
- Единица: [unit]
- Regex: [pattern]
- Минимална стойност: [floor]

### Праг за рентабилност
- Стойност: [number]
- Единица: [e.g. EUR/м²]
- Формула: [e.g. прогнозна стойност / РЗП]
- Под прага: [warning text]

### Приоритет на файлове за метрики
[ordered list of file name patterns and extensions to search]

## Ценообразуване

### Разходни категории
[list of cost categories with descriptions]

### Ценови ориентир
[strategy text]

### Типични доставчици
[supplier list with specialties]

## Фирмен профил (допълнителни полета)

### Специфични полета за домейна
[list of extra fields for company-profile.md]
```

#### Construction Preset Example

The construction preset (`domains/construction.md`) contains:
- Search keyword: "СМР"
- 8 positive categories with CPV codes (Топлоизолация 45321000, ЕЕ 45453000, etc.)
- 5 negative categories (пътно, мостове, озеленяване, електроинсталации, канализация)
- Priority: ЕЕ > Топлоизолация > Ново строителство > Ремонт > останалите
- Metrics: ЗП (м²) and РЗП (м²) with regex patterns
- Feasibility threshold: 100 EUR/м² on РЗП
- File priority: задание > сертификат/енергийен > техн > обяв > all .docx > PDF fallback
- Pricing: Труд + Материали + Допълнителни, 10-15% overhead, 70-85% target
- Suppliers: Bagira, HomeMax, Praktis, Praktiker
- Profile fields: Оборудване, Склад, Превозни средства, Служители

### 3. Preset Directory

```
eopowers/
  domains/
    construction.md    # Full construction domain config (extracted from current hardcoded data)
    README.md          # Brief guide: "How to create a custom domain preset"
```

Init reads `domains/*.md` to build the selection menu dynamically. Adding a new preset = adding a file. Contributors can submit domain presets via PR.

### 4. Init Flow Changes

Current flow:
1. Website URL → 2. Scrape → 3. Registration data → 4. Optional HTML import → 5. Generate profile → 6. Confirm

New flow — **Step 0 inserted before Step 1:**

```
Стъпка 0 — Избор на домейн

> Какъв е основният ви бизнес домейн?
> 
> 1. 🏗️ Строителство (СМР, ремонт, ЕЕ, фасади)
> 2. 🔧 Персонализиран домейн
>
> (Въведете номер)
```

**Option 1 (preset):** Read the corresponding `domains/<preset>.md` from the plugin directory, copy to `./eopowers/domain.md`. Ask: "Искате ли да промените нещо в домейн конфигурацията?" If yes, walk through sections. If no, proceed to Step 1.

**Option 2 (custom):** Interactive session:
1. "Опишете с 1-2 изречения основната дейност на фирмата" → LLM generates initial CPV codes and keywords
2. "Какви CPV кодове таргетирате?" → confirm/edit generated list
3. "Какви категории поръчки са релевантни?" → build positive keyword table
4. "Какви категории да изключим?" → build negative keyword table
5. "Какви метрики са важни за оценка на поръчка?" → define metrics with regex patterns (LLM suggests based on domain)
6. "Какъв е прагът за рентабилност?" → set threshold
7. "Какви са основните разходни категории?" → define pricing structure
8. "Кои са типичните доставчици?" → supplier list
9. Generate `./eopowers/domain.md`, show for confirmation

As more presets ship, options auto-populate from `domains/` directory.

**Step 5 change:** Profile template dynamically includes domain-specific fields from `domain.md`'s "Фирмен профил" section instead of hardcoded construction fields (Оборудване, Превозни средства, etc.).

### 5. Skill Changes

#### eop-scan

**Remove:** All inline CPV code tables, keyword tables, category definitions, regex patterns, metric calculations, file priority lists, feasibility threshold.

**Replace with:** A single instruction block at the top of Phase 2 (enrichment):

> Прочети `./eopowers/domain.md`. Ако файлът не съществува — съобщи: "Стартирайте /init първо."
>
> Използвай секция "Търсене" за:
> - Ключова дума за филтър (Стъпка 2)
> - Положителни/отрицателни ключови думи (Стъпка 4 — категоризация)
> - Приоритет при множество категории
>
> Използвай секция "Метрики" за:
> - Regex patterns за извличане на стойности от документи (Стъпка 5)
> - Приоритет на файлове за парсване
> - Праг за рентабилност (⚠️ маркиране)
>
> Адаптирай колоните на резултатната таблица спрямо дефинираните метрики.

The scan algorithm (navigate → filter → extract → categorize → enrich → rank) stays identical. Only the parameters change.

The Python regex script becomes dynamic — reads patterns from domain.md instead of hardcoding them. The script structure stays the same.

#### eop-price

**Remove:** Hardcoded reference to construction pricing guide specifics.

**Replace with:**

> Прочети секция "Ценообразуване" от `./eopowers/domain.md` за разходни категории, ценови ориентири и доставчици. Адаптирай стъпки 3-5 спрямо дефинираните категории.

`pricing-guide.md` stays as a file but becomes the construction-specific detailed appendix. The domain config provides the structure; the pricing guide provides depth for construction users.

#### init

**Add:** Step 0 (domain selection) as described above. Make Step 5 (profile template) dynamic based on domain config's profile fields section.

#### start

**Add:** Read `./eopowers/domain.md` and show domain name in header:

> "BloxPowers — Домейн: Строителство" or "eopowers — Домейн: ИТ услуги"

#### eop-analyze, eop-generate, eop-review

**Minimal changes:** Add `Read ./eopowers/domain.md` to context loading. These skills are already mostly domain-agnostic. The only change is path references (`./bloxpowers/` → `./eopowers/`).

### 6. What Stays Hardcoded (Not Domain-Configurable)

These are EOP-platform-specific, not domain-specific:

- Portal navigation (eop.bg URLs, Angular SPA behavior, Playwright automation)
- Document pipeline (download, ZIP/RAR extraction, .doc→.docx conversion, PDF text extraction)
- ROI formula structure (V * Cm * Ct / D * Cp)
- Workflow pipeline order (scan → analyze → price → generate → review)
- File organization (`./eopowers/offers/<id>/`)
- Pagination, error handling, timeouts

### 7. Migration for Existing Users

Users who already have `./bloxpowers/` data:

Init detects `./bloxpowers/company-profile.md` exists but `./eopowers/` doesn't:

> "Открих съществуващ профил в ./bloxpowers/. Искате ли да мигрирам данните към ./eopowers/? (да/не)"

If yes: copy `company-profile.md` and `offers/` to `./eopowers/`, generate `domain.md` with construction preset (since existing users are construction). Leave old directory untouched.

### 8. File Structure After Implementation

```
eopowers/                           # Plugin root (git repo)
  .claude-plugin/
    plugin.json                     # name: "eopowers"
    marketplace.json                # name: "eopowers"
  domains/
    construction.md                 # Construction preset (extracted from current hardcoded data)
    README.md                       # "How to create a custom domain"
  skills/
    start/SKILL.md                  # Shows domain in header
    init/SKILL.md                   # Step 0: domain selection
    eop-scan/SKILL.md               # Reads domain.md for all parameters
    eop-analyze/SKILL.md            # Path rename only
    eop-price/SKILL.md              # Reads domain.md for pricing structure
    eop-price/pricing-guide.md      # Construction-specific appendix (unchanged)
    eop-generate/SKILL.md           # Path rename only
    eop-review/SKILL.md             # Path rename only
  agents/
    eop-offer-analyzer.md
    eop-market-researcher.md
  hooks/
    ...
```

User workspace after init:

```
./eopowers/
  domain.md                         # Active domain config
  company-profile.md                # Company profile
  offers/
    scan-2026-04-09.md
    575004/meta.md
    ...
```
