# eopowers Domain-Configurable Plugin — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rename bloxpowers → eopowers, extract all construction-specific logic into a domain config layer with presets and custom domain support during init.

**Architecture:** All construction-specific data (CPV codes, keywords, metrics, regex patterns, pricing structure, suppliers) moves from hardcoded skill prompts into a `domain.md` config file. The plugin ships with a `domains/construction.md` preset. During `/init`, users pick a preset or build a custom domain interactively. All skills read `./eopowers/domain.md` at runtime.

**Tech Stack:** Claude Code plugin (SKILL.md prompts, YAML frontmatter), Markdown config files, Bash hooks

**Spec:** `docs/2026-04-09-eopowers-domain-config-design.md`

---

### Task 1: Rename bloxpowers → eopowers (manifests, metadata, package.json)

**Files:**
- Modify: `.claude-plugin/plugin.json`
- Modify: `.claude-plugin/marketplace.json`
- Modify: `package.json`
- Modify: `CHANGELOG.md`
- Modify: `README.md`

- [ ] **Step 1: Update `.claude-plugin/plugin.json`**

Replace all occurrences of `bloxpowers` with `eopowers`:
```json
{
  "name": "eopowers",
  "description": "Инструменти за автоматизирано участие в обществени поръчки (ЕОП) — сканиране, анализ, ценообразуване и генериране на оферти",
  "version": "1.0.0",
  "author": {
    "name": "Blox Engineering",
    "email": "info@blox.bg"
  },
  "homepage": "https://github.com/Lutherwaves/eopowers",
  "repository": "https://github.com/Lutherwaves/eopowers",
  "license": "MIT",
  "keywords": ["eop", "procurement", "offers", "construction", "bulgaria", "обществени-поръчки"]
}
```

- [ ] **Step 2: Update `.claude-plugin/marketplace.json`**

```json
{
  "name": "eopowers",
  "owner": {
    "name": "Blox Engineering"
  },
  "plugins": [
    {
      "name": "eopowers",
      "source": "./",
      "description": "Инструменти за автоматизирано участие в обществени поръчки (ЕОП)",
      "version": "1.0.0"
    }
  ]
}
```

- [ ] **Step 3: Update `package.json`**

```json
{
  "name": "eopowers",
  "version": "1.0.0",
  "type": "module",
  "description": "Claude Code plugin for Bulgarian public procurement (eop.bg)",
  "license": "MIT",
  "repository": {
    "type": "git",
    "url": "https://github.com/Lutherwaves/eopowers"
  }
}
```

- [ ] **Step 4: Update `CHANGELOG.md`**

Add a new section at the top:
```markdown
## 1.0.0 (2026-04-09)

- Renamed plugin: bloxpowers → eopowers
- Domain-configurable: construction-specific logic extracted into domain.md config
- New: domains/construction.md preset (ships with plugin)
- New: /init Step 0 — domain selection (preset or custom)
- All skills now read from ./eopowers/domain.md instead of hardcoded values
- Migration support for existing ./bloxpowers/ users
```

- [ ] **Step 5: Update `README.md`**

Replace all occurrences of `bloxpowers` with `eopowers` and `Lutherwaves/bloxpowers` with `Lutherwaves/eopowers`. Update install commands:
```bash
/plugin marketplace add Lutherwaves/eopowers
/plugin install eopowers@eopowers
```

Add a "Domain Configuration" section after "What It Does":
```markdown
## Domain Configuration

eopowers ships with a construction domain preset but supports any procurement domain.
During `/init`, choose a preset or build a custom domain configuration.

Presets available:
- **Construction** — СМР, thermal insulation, energy efficiency, facades, renovation

Want to add a domain preset? See `domains/README.md` and submit a PR.
```

- [ ] **Step 6: Update `.github/workflows/release.yml`**

No changes needed — the CI reads version from JSON files dynamically, no hardcoded plugin name.

- [ ] **Step 7: Commit**

```bash
git add .claude-plugin/plugin.json .claude-plugin/marketplace.json package.json CHANGELOG.md README.md
git commit -m "feat: rename bloxpowers → eopowers, bump to v1.0.0"
```

---

### Task 2: Create construction domain preset

**Files:**
- Create: `domains/construction.md`
- Create: `domains/README.md`

- [ ] **Step 1: Create `domains/construction.md`**

Extract all construction-specific data from the current `eop-scan/SKILL.md` (lines 219-253: CPV tables, keyword tables, negative keywords), the metric regex patterns (lines 161-163), file priority (lines 121-126), feasibility threshold (line 217), and from `eop-price/pricing-guide.md` (daily rates, suppliers, overhead). Write as a complete domain config:

```markdown
# Домейн: Строителство

## Търсене (eop-scan)

### Ключова дума за филтър
СМР

### Положителни ключови думи

| Категория | CPV кодове | Ключови думи |
|-----------|-----------|--------------|
| Топлоизолация | 45321000 | топлоизолац, EPS, XPS, минерална вата, термоизолац |
| Енергийна ефективност | 45453000, 45421000 | енергийна ефективност, НПВУ, ЕСКБ, ЕСМ, енергоспестяващ, енергийно обновяване, дограма, осветление |
| Ново строителство | 45210000, 45211000 | ново строителство, изграждане, жилищн |
| Ремонт/реконструкция | 45454000, 45453100 | ремонт, реконструкция, преустройство, обновяване |
| Фасади и мазилки | 45443000, 45410000 | фасад, мазилк, облицовк, бояджийск |
| Проектиране | 71220000, 71320000 | проектиране, архитектур, инженерн |
| СМР (общо) | 45000000 | СМР, строително-монтажни |
| Довършителни работи | 45400000 | довършителн |

### Отрицателни ключови думи

| Изключена категория | Ключови думи |
|---------------------|-------------|
| Пътно строителство | пътно, пътен, асфалт, настилка на път, пътна |
| Мостове и тунели | мост, тунел, виадукт, надлез, подлез |
| Озеленяване | озеленяване, паркоустройство, залесяване, тревн |
| Електроинсталации | електроинсталац, електромонтаж, кабелн, трафопост |
| Канализация | канализац, пречиствателн, ВиК мрежа |

### Приоритет при множество категории
ЕЕ > Топлоизолация > Ново строителство > Ремонт/реконструкция > Фасади и мазилки > Проектиране > СМР (общо) > Довършителни работи

### Бележки за категоризация
- ЕЕ винаги печели ако присъстват ключови думи за енергийна ефективност (НПВУ, ЕСКБ, ЕСМ, енергийно обновяване, енергоспестяващи)
- "Обновяване" в контекста на ЕЕ НЕ е Ремонт
- Проверката за отрицателни ключови думи е САМО по заглавие и CPV код — не по тялото на документите

## Метрики

### Основна метрика
- Име: Застроена площ
- Кратко име: ЗП
- Единица: м²
- Regex: `(?:Застроена площ|ЗП)\s*[^\d]{0,20}([\d][\d\s,.]*\d)\s*(?:кв\.?\s*м|m2|м)`
- Минимална стойност: 10

### Допълнителна метрика
- Име: Разгъната застроена площ
- Кратко име: РЗП
- Единица: м²
- Regex: `(?:Разгъната застроена площ|Разгъната площ|РЗП)[^\d]{0,20}([\d][\d\s,.]*\d)\s*(?:кв\.?\s*м|m2|м)`
- Минимална стойност: 10

### Праг за рентабилност
- Стойност: 100
- Единица: EUR/м²
- Формула: прогнозна стойност / РЗП
- Под прага: ⚠️ потенциално нерентабилна

### Приоритет на файлове за метрики
1. `.docx` файлове с "задание" в името (технически задания)
2. `.docx` файлове с "серт" или "енерг" в името (енергийни сертификати)
3. `.docx` файлове с "техн" в името (без "спецификац")
4. Файлове с "обява" или "обявление" в името
5. Всички останали `.docx` файлове
6. PDF fallback — `.pdf` файлове (последен приоритет)

## Ценообразуване

### Разходни категории
- Труд (дневни ставки по квалификация)
- Материали (с надценка 10-20%, 5-10% при големи количества)
- Допълнителни (транспорт, механизация, застраховки)
- Overhead: 10-15% от директните разходи

### Дневни ставки (регион Стара Загора, 2024-2026)
| Квалификация | Дневна ставка (лв.) | Забележка |
|-------------|---------------------|-----------|
| Общ строителен работник | 80–120 | Неквалифициран труд |
| Квалифициран работник (зидар, мазач, арматурист) | 120–180 | С професионален опит |
| Специалист (електротехник, ВиК, заварчик) | 150–200 | Със сертификат |
| Инженер / технически ръководител | 200–300 | Висше образование, опит |

### Ценови ориентир
- Целете 70–85% от прогнозната стойност
- Не слагайте под себестойност + 5%
- Ако критерият "цена" тежи >50% — ценете по-агресивно (70–75%)
- Ако "техническо предложение" тежи повече — инвестирайте в качеството, ценете умерено (80–85%)

### Типични доставчици
- Bagira — строителни материали, инструменти
- HomeMax — довършителни материали, бои, лепила
- Praktis — широк асортимент строителни материали
- Praktiker — инструменти, крепежни елементи

## Фирмен профил (допълнителни полета)

### Специфични полета за домейна
- Оборудване и ресурси
- Собствен склад (да/не, местоположение)
- Превозни средства (описание)
- Служители (брой)
```

- [ ] **Step 2: Create `domains/README.md`**

```markdown
# Domain Presets

Domain presets define how eopowers searches, categorizes, prices, and evaluates tenders for a specific industry.

## Available Presets

| File | Domain | Description |
|------|--------|-------------|
| `construction.md` | Строителство | СМР, thermal insulation, energy efficiency, facades, renovation |

## Creating a Custom Preset

Copy `construction.md` as a template and modify each section:

1. **Търсене** — search keyword, positive/negative CPV codes and keywords, category priority
2. **Метрики** — what to extract from tender documents (regex patterns), feasibility thresholds
3. **Ценообразуване** — cost categories, daily rates, pricing strategy, suppliers
4. **Фирмен профил** — extra fields for company-profile.md specific to your domain

All text should be in Bulgarian (user-facing output is in Bulgarian).

## Contributing

Submit a PR with your `domains/<domain-name>.md` file. It will appear automatically in the `/init` domain selection menu.
```

- [ ] **Step 3: Commit**

```bash
git add domains/construction.md domains/README.md
git commit -m "feat: add construction domain preset and domain README"
```

---

### Task 3: Update init skill — add domain selection (Step 0)

**Files:**
- Modify: `skills/init/SKILL.md`

- [ ] **Step 1: Update frontmatter description**

Change description from construction-specific to generic:
```yaml
---
name: init
description: Първоначална настройка — избор на домейн и фирмен профил. Използва се еднократно при първо стартиране.
allowed-tools: Read, Grep, Glob, WebFetch, WebSearch, Write, Bash(mkdir *)
---
```

- [ ] **Step 2: Update checklist**

Replace the current checklist (lines 9-15) with:
```markdown
- [ ] Избор на домейн (preset или персонализиран)
- [ ] Генериране на domain.md
- [ ] Въвеждане на URL на фирмен уебсайт
- [ ] Сканиране на уебсайта за информация
- [ ] Въвеждане на регистрационни данни
- [ ] Зареждане на локален HTML експорт (по избор)
- [ ] Генериране на company-profile.md
- [ ] Потвърждение от потребителя
```

- [ ] **Step 3: Add Step 0 — Domain selection before Step 1**

Insert after the checklist, before current "Стъпка 1":

```markdown
### Стъпка 0 — Избор на домейн

**Миграция:** Ако съществува `./bloxpowers/company-profile.md` но НЕ съществува `./eopowers/`:
> "Открих съществуващ профил в ./bloxpowers/. Искате ли да мигрирам данните към ./eopowers/? (да/не)"
Ако "да" — копирай `company-profile.md` и `offers/` в `./eopowers/`, генерирай `domain.md` с preset "Строителство", и премини към Стъпка 6 (потвърждение).

**Ако `./eopowers/domain.md` вече съществува** — пропусни тази стъпка и премини към Стъпка 1.

Прочети наличните домейн preset-и от директорията `domains/` в plugin-а (всеки `.md` файл без `README.md`). За всеки файл, извлечи заглавието от първия ред (напр. `# Домейн: Строителство` → "Строителство").

Покажи менюто:

> Какъв е основният ви бизнес домейн?
>
> 1. 🏗️ Строителство (СМР, ремонт, ЕЕ, фасади)
> [... допълнителни preset-и, ако има ...]
> N. 🔧 Персонализиран домейн
>
> (Въведете номер)

**Ако потребителят избере preset:**
1. Прочети съответния `domains/<preset>.md` от plugin директорията.
2. Запиши като `./eopowers/domain.md`.
3. Попитай: "Искате ли да промените нещо в домейн конфигурацията? (да/не)"
4. Ако "да" — покажи секция по секция и приеми промени.
5. Ако "не" — премини към Стъпка 1.

**Ако потребителят избере "Персонализиран домейн":**
1. "Опишете с 1-2 изречения основната дейност на фирмата."
2. На базата на описанието, предложи CPV кодове и ключови думи. Попитай: "Тези CPV кодове и ключови думи изглеждат ли коректно? Искате ли да добавите или премахнете?"
3. "Какви категории поръчки да изключим автоматично?" → построй таблица с отрицателни ключови думи.
4. "Какви метрики са важни при оценка на поръчка? (напр. площ на сграда, брой служители, часове работа)" → дефинирай метрики с regex patterns (предложи на базата на описания домейн).
5. "Какъв е прагът за рентабилност?" → задай стойност и формула.
6. "Какви са основните разходни категории?" → дефинирай структура.
7. "Кои са типичните доставчици във вашия бранш?" → списък.
8. "Какви допълнителни полета трябва да има фирменият профил?" → списък.
9. Генерирай `./eopowers/domain.md` по структурата от preset шаблона. Покажи за потвърждение.
```

- [ ] **Step 4: Update all path references**

Replace all `./bloxpowers/` with `./eopowers/` in the entire file:
- Line 65: `mkdir -p ./eopowers`
- Line 68: `./eopowers/company-profile.md`

- [ ] **Step 5: Make Step 5 (profile template) dynamic**

Replace the hardcoded profile template (lines 82-123). Keep the generic sections (Идентификация, Управители, Сертификати, Услуги, Референтни проекти, Контакти) and replace the hardcoded "Оборудване и ресурси" section with:

```markdown
## Допълнителни полета (от domain.md)

Прочети секция "Фирмен профил → Специфични полета за домейна" от `./eopowers/domain.md`.
За всяко поле, добави ред в шаблона с формат:
- [Име на полето]: [стойност от потребителя]

Попитай потребителя за всяко от тези полета.
```

- [ ] **Step 6: Commit**

```bash
git add skills/init/SKILL.md
git commit -m "feat(init): add domain selection step, dynamic profile template"
```

---

### Task 4: Update eop-scan — read from domain.md instead of hardcoded data

**Files:**
- Modify: `skills/eop-scan/SKILL.md`

This is the largest task. The scan algorithm (navigate → filter → extract → categorize → enrich → rank) stays the same. We replace hardcoded data with domain.md reads.

- [ ] **Step 1: Update frontmatter**

```yaml
---
name: eop-scan
description: Сканира eop.bg за отворени обществени поръчки, категоризира и приоритизира по ROI. Използва се при търсене на нови поръчки за участие.
allowed-tools: Read, Write, Glob, Bash(mkdir *), Bash(python *), Agent, mcp__plugin_playwright_playwright__*
---
```

Note: removed "строителни" from description — now generic.

- [ ] **Step 2: Add domain.md loading instruction**

Insert immediately after the checklist (after line 21), before "## Инструкции за сканиране":

```markdown
## Зареждане на домейн конфигурация

Прочети `./eopowers/domain.md` с Read tool. Ако файлът не съществува — съобщи: "Няма домейн конфигурация. Стартирайте /init първо." и спри.

Извлечи от файла:
- **Ключова дума за филтър** (секция "Търсене → Ключова дума за филтър")
- **Положителни ключови думи** (секция "Търсене → Положителни ключови думи" — таблица с категории, CPV кодове, ключови думи)
- **Отрицателни ключови думи** (секция "Търсене → Отрицателни ключови думи" — таблица)
- **Приоритет при множество категории** (секция "Търсене → Приоритет при множество категории")
- **Бележки за категоризация** (секция "Търсене → Бележки за категоризация", ако съществува)
- **Метрики** (секция "Метрики" — всички дефинирани метрики с име, кратко име, единица, regex, минимална стойност)
- **Праг за рентабилност** (секция "Метрики → Праг за рентабилност")
- **Приоритет на файлове за метрики** (секция "Метрики → Приоритет на файлове за метрики")

Използвай тези данни навсякъде по-долу вместо хардкоднати стойности.
```

- [ ] **Step 3: Make Step 2 (search filter) dynamic**

Replace the hardcoded "СМР" in Step 2 (line 34) with:

```markdown
### Стъпка 2: Филтри за търсене

1. Натисни бутон **"Търсене"** за да отвориш панела с филтри.
2. В полето **"Ключова дума"** (textbox "Въведете дума/израз") въведи **ключовата дума от domain.md** и натисни бутон **"Добави"**.
3. Натисни бутон **"Приложи"** за да филтрираш резултатите.
4. Филтърът **"отворени за участие"** е приложен по подразбиране — не го променяй.
```

- [ ] **Step 4: Replace hardcoded categorization section**

Remove the entire "## Категоризация по CPV кодове" section (lines 219-241) and the "## Отрицателни ключови думи" section (lines 243-253). Replace with:

```markdown
## Категоризация

Използвай таблиците от domain.md (заредени в началото).

Алгоритъм:
1. Извлечи заглавието на поръчката.
2. Провери дали ОСНОВНИЯТ обхват (заглавие + CPV код) съвпада с **отрицателни ключови думи** от domain.md → **изключи** от резултатите. Логирай: "⛔ Изключена: [title] (причина: [matched keyword])".
3. Провери CPV кода — ако съвпада с **положителни ключови думи** таблицата от domain.md, задай категория.
4. Ако CPV не е наличен — търси положителни ключови думи в наименованието.
5. **Приоритет при множество категории:** Ако съвпада с повече от една, приложи приоритета от domain.md. Спазвай бележките за категоризация (ако има).
6. Ако няма съвпадение с нито една категория — маркирай като "Некатегоризирана".
```

- [ ] **Step 5: Replace hardcoded metric extraction**

Replace "#### Извличане на ЗП и РЗП" section (lines 118-217) with a dynamic version. Keep the Python script structure but make it read patterns from domain.md:

```markdown
#### Извличане на метрики от документи

Приоритет на файлове: спазвай реда от секция "Приоритет на файлове за метрики" в domain.md.

За всяка метрика дефинирана в domain.md, използвай нейния regex pattern за извличане.

```python
python -c "
import re, glob, subprocess, os

offer_id = '<offer-id>'
attachments_dir = f'./eopowers/offers/{offer_id}/attachments'

# File collection — .docx first, PDF fallback
all_files = glob.glob(f'{attachments_dir}/*.docx')
pdf_files = glob.glob(f'{attachments_dir}/*.pdf')

# File priority from domain.md — adapt this function per the loaded config
# The priority keywords come from domain.md section 'Приоритет на файлове за метрики'
def file_priority(f):
    name = os.path.basename(f).lower()
    # [Adapt priority keywords from domain.md]
    # Example for construction: задание=0, серт/енерг=1, техн=2, обяв=3, else=4
    return 4  # default

files = sorted(all_files, key=file_priority)
files.extend(sorted(pdf_files, key=file_priority))

# Metric patterns from domain.md
# [Insert patterns dict from domain.md metrics section]
# Example: patterns = {'zp': r'...', 'rzp': r'...'}
patterns = {}  # populated from domain.md

results = {}
for fpath in files:
    try:
        if fpath.endswith('.pdf'):
            try:
                import subprocess as sp
                r = sp.run(['pdftotext', '-l', '5', fpath, '-'], capture_output=True, text=True, timeout=15)
                text = r.stdout
            except FileNotFoundError:
                try:
                    import pdfplumber
                    with pdfplumber.open(fpath) as pdf:
                        text = '\n'.join(p.extract_text() or '' for p in pdf.pages[:5])
                except ImportError:
                    continue
        elif fpath.endswith('.docx'):
            from docx import Document
            doc = Document(fpath)
            text = '\n'.join(p.text for p in doc.paragraphs)
            for table in doc.tables:
                for row in table.rows:
                    text += '\n' + ' '.join(cell.text for cell in row.cells)
        else:
            with open(fpath, 'r', errors='ignore') as f:
                text = f.read()

        for key, pat in patterns.items():
            if key not in results:
                m = re.search(pat, text, re.IGNORECASE)
                if m:
                    val = m.group(1).replace(' ', '').replace(',', '.')
                    num = float(val)
                    min_val = 10  # [from domain.md metric min value]
                    if num >= min_val:
                        results[key] = num

        if len(results) == len(patterns):
            break
    except Exception:
        continue

for key, val in results.items():
    print(f'{key.upper()}={val}')
for key in patterns:
    if key not in results:
        print(f'{key.upper()}=—')
"
```

Изчисли рентабилност по формулата от domain.md (секция "Праг за рентабилност").
Ако стойността е под прага — маркирай с предупреждението от domain.md.
```

- [ ] **Step 6: Make results table dynamic**

Replace the hardcoded table (lines 273-283) with:

```markdown
## Представяне на резултати

Покажи резултатите като Markdown таблица, сортирана по ROI (низходящо).

Колоните се генерират динамично от domain.md:
- Фиксирани колони: #, Поръчка, Възложител, Стойност (EUR), Категория, ROI
- За всяка метрика в domain.md: добави колона "[Кратко име] ([Единица])"
- За всяка метрика с праг за рентабилност: добави колона "EUR/[Единица] [Кратко име]"

Пример (за строителство с ЗП и РЗП):
| # | Поръчка | Възложител | Стойност (EUR) | ЗП (м²) | РЗП (м²) | EUR/м² ЗП | EUR/м² РЗП | Категория | ROI |

- ⚠️ — стойност под прага от domain.md
- "—" — метриката не може да бъде извлечена от документите

Ако няма намерени резултати — съобщи: "Не бяха намерени отворени поръчки с текущите филтри."
```

- [ ] **Step 7: Update all path references**

Replace all `./bloxpowers/` with `./eopowers/` throughout the file:
- Line 83: `./eopowers/offers/<offer-id>/meta.md`
- Line 85: `mkdir -p ./eopowers/offers/<offer-id>/attachments`
- Lines 95-96: `./eopowers/offers/<offer-id>/attachments/`
- Lines 100-106: attachment paths
- Lines 111-113: `.doc` conversion paths
- Line 135: `attachments_dir`
- Line 289: `./eopowers/offers/scan-YYYY-MM-DD.md`
- Lines 295-296: scan summary references
- Lines 341-364: offer selection paths

- [ ] **Step 8: Update scan summary to use dynamic metric columns**

Replace the hardcoded scan summary template (lines 289-329) — the table headers should use metric names from domain.md instead of hardcoded "ЗП (м²) | РЗП (м²) | EUR/м² ЗП | EUR/м² РЗП":

```markdown
## Автоматичен запис на резултатите

[Same structure but with dynamic columns:]

## Обогатени поръчки (Phase 2 — с метрики)

| # | ID | Обект | Възложител | Стойност (EUR) | [metric columns from domain.md] | Категория |
```

- [ ] **Step 9: Update meta.md template**

Replace the hardcoded meta.md template (lines 347-362) with dynamic metric fields:

```markdown
# Поръчка <offer-id>

- Наименование: [title]
- Възложител: [buyer]
- Прогнозна стойност: [value] EUR
- Краен срок: [deadline]
- Начин на възлагане: [procedure type]
- Категория: [category]
- ROI оценка: [score]
[За всяка метрика от domain.md:]
- [Име на метриката]: [value] [единица]
[За всяка метрика с праг:]
- EUR/[единица] ([кратко име]): [value]
- URL: https://app.eop.bg/today/<offer-id>
- Дата на сканиране: [current date]
```

- [ ] **Step 10: Update checklist at top**

Replace "Извличане на площ от документите" with "Извличане на метрики от документите":
```
- [ ] Извличане на метрики от документите
```

- [ ] **Step 11: Commit**

```bash
git add skills/eop-scan/SKILL.md
git commit -m "feat(eop-scan): read categories, metrics, thresholds from domain.md"
```

---

### Task 5: Update eop-price — read pricing config from domain.md

**Files:**
- Modify: `skills/eop-price/SKILL.md`

- [ ] **Step 1: Add domain.md loading**

Insert after the existing context loading section (line 12), before the checklist:

```markdown
3. `./eopowers/domain.md` — ако не съществува: "Стартирайте /init първо"

Използвай секция "Ценообразуване" от domain.md за:
- Разходни категории (адаптирай стъпки 3-5)
- Дневни ставки (ако са дефинирани)
- Ценови ориентир
- Типични доставчици (за market research)
```

- [ ] **Step 2: Make Steps 3-5 dynamic**

Replace Step 3 (Труд, line 56-63) — keep the structure but reference domain.md:

```markdown
### Стъпка 3: Разходи по категории

За всяка **разходна категория** дефинирана в domain.md (секция "Ценообразуване → Разходни категории"), попитай последователно за необходимите данни.

Ако domain.md дефинира **дневни ставки** — предложи ги като ориентир.
Ако domain.md дефинира **типични доставчици** — използвай ги за market research (dispatch `eop-market-researcher` субагент или WebSearch).
```

- [ ] **Step 3: Update supplier references in Step 4**

Replace hardcoded "Bagira, HomeMax, Praktis, Praktiker и други доставчици в Стара Загора" (line 73) with:

```markdown
- Търси в доставчиците от domain.md (секция "Ценообразуване → Типични доставчици") и други онлайн източници
```

- [ ] **Step 4: Update all path references**

Replace all `./bloxpowers/` with `./eopowers/` throughout the file.

- [ ] **Step 5: Commit**

```bash
git add skills/eop-price/SKILL.md
git commit -m "feat(eop-price): read pricing categories and suppliers from domain.md"
```

---

### Task 6: Update eop-analyze, eop-generate, eop-review — path rename

**Files:**
- Modify: `skills/eop-analyze/SKILL.md`
- Modify: `skills/eop-generate/SKILL.md`
- Modify: `skills/eop-review/SKILL.md`

- [ ] **Step 1: eop-analyze — replace paths**

Replace all `./bloxpowers/` with `./eopowers/` throughout the file:
- Line 12: `./eopowers/offers/$ARGUMENTS/meta.md`
- Line 31: `./eopowers/offers/$ARGUMENTS/attachments/`
- Line 36: `./eopowers/offers/$ARGUMENTS/attachments/`
- Line 39: `./eopowers/offers/$ARGUMENTS/attachments/*.zip`
- Line 92: `./eopowers/offers/$ARGUMENTS/analysis.md`

- [ ] **Step 2: eop-generate — replace paths**

Replace all `./bloxpowers/` with `./eopowers/` throughout the file:
- Lines 11-13: context loading paths
- Line 34: attachments path
- Lines 64, 98-99, 116, 139-140: output paths

Also add domain.md to context loading:
```markdown
4. `./eopowers/domain.md` — за домейн-специфична информация (по избор)
```

- [ ] **Step 3: eop-review — replace paths**

Replace all `./bloxpowers/` with `./eopowers/` throughout the file:
- Lines 11-12: context loading paths
- Lines 29, 98-99, 103, 105: file paths

- [ ] **Step 4: Commit**

```bash
git add skills/eop-analyze/SKILL.md skills/eop-generate/SKILL.md skills/eop-review/SKILL.md
git commit -m "refactor: rename bloxpowers → eopowers paths in analyze, generate, review"
```

---

### Task 7: Update start skill, agents, and hooks

**Files:**
- Modify: `skills/start/SKILL.md`
- Modify: `agents/eop-market-researcher.md`
- Modify: `hooks/session-start`
- Modify: `hooks/hooks.json`

- [ ] **Step 1: Update start skill**

Replace the description in frontmatter:
```yaml
description: Главно меню на eopowers — показва налични инструменти за обществени поръчки и други бизнес операции.
```

Add domain display after the prerequisites check (line 21). Insert before "## Налични инструменти":

```markdown
## Домейн

Прочети `./eopowers/domain.md` и покажи:

> **eopowers** — Домейн: [name from domain.md heading]

Ако domain.md не съществува:
> "Няма домейн конфигурация. Стартирайте `/init` за първоначална настройка."
```

Replace `./bloxpowers/` with `./eopowers/` throughout:
- Line 21: `./eopowers/company-profile.md`
- Lines 58-60: working directory references

Update the command table to remove "строителни" from eop-scan description:
```markdown
| `/eop-scan` | Сканиране на eop.bg за отворени обществени поръчки |
```

- [ ] **Step 2: Update eop-market-researcher agent**

Replace the hardcoded construction description with domain-aware instructions. Change the first paragraph (line 9):

```markdown
You research current prices for materials and services from suppliers.

## Input

You will receive:
- Item name (in Bulgarian)
- Required quantity
- Preferred suppliers (from domain.md, optional)
- Search region (optional)
```

Replace the hardcoded supplier list (line 23) with:
```markdown
   - Check suppliers from domain.md configuration (passed as input)
   - Also check: specialized suppliers, wholesale options
```

- [ ] **Step 3: Update session-start hook**

Replace `BloxPowers` with `eopowers` and remove "строителни" from the session context message:

```bash
session_context="<IMPORTANT>\neopowers е инсталиран.\n\nНалични инструменти за обществени поръчки:\n- /eop-scan — сканиране на eop.bg за отворени поръчки\n- /eop-analyze <id> — анализ на конкретна поръчка\n- /eop-price <id> — ценообразуване\n- /eop-generate <id> — генериране на оферта\n- /eop-review <id> — преглед и PDF конвертиране\n\nНастройка: /init | Меню: /start\n</IMPORTANT>"
```

- [ ] **Step 4: Commit**

```bash
git add skills/start/SKILL.md agents/eop-market-researcher.md hooks/session-start
git commit -m "refactor: update start, market-researcher, hooks for eopowers rename"
```

---

### Task 8: Rename GitHub repo and update remotes

- [ ] **Step 1: Rename repo on GitHub**

```bash
gh repo rename eopowers --repo Lutherwaves/bloxpowers --yes
```

- [ ] **Step 2: Update git remote**

```bash
git remote set-url origin git@github.com:Lutherwaves/eopowers.git
git remote set-url oss git@github.com:Lutherwaves/eopowers.git
```

- [ ] **Step 3: Push all commits**

```bash
git push origin main
```

- [ ] **Step 4: Verify CI runs**

```bash
gh run list --repo Lutherwaves/eopowers --limit 3
```

Verify the release workflow triggers and bumps version from 1.0.0 to 1.0.1.

---

### Task 9: Final verification

- [ ] **Step 1: Verify plugin installs from new repo**

User should run:
```
/plugin marketplace add Lutherwaves/eopowers
/plugin install eopowers@eopowers
/reload-plugins
```

Verify all 7 skills appear with `eopowers:` prefix.

- [ ] **Step 2: Verify domain.md is read correctly**

Run `/init` in a test workspace. Select construction preset. Verify `./eopowers/domain.md` is created with full construction config.

- [ ] **Step 3: Verify scan works with domain config**

Run `/eop-scan`. Verify it reads keywords and metrics from `./eopowers/domain.md` instead of hardcoded values. The behavior should be identical to before for construction domain.

- [ ] **Step 4: Commit any fixes**

```bash
git add -A && git commit -m "fix: post-rename verification fixes"
git push origin main
```
