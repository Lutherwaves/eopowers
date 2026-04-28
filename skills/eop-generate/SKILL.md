---
name: eop-generate
description: Генерира офертен документ — попълва шаблона на поръчката с фирмени данни и ценообразуване. Използва се след ценообразуване с eop-price.
argument-hint: [offer-id]
allowed-tools: Read, Write, Glob, Grep, Bash(python *), Bash(libreoffice *)
---

## Зареждане на контекст

Преди да започнеш, прочети задължително с Read tool:
1. `./eopowers/offers/$ARGUMENTS/analysis.md` — ако не съществува: "Няма анализ — стартирайте /eop-analyze $ARGUMENTS"
2. `./eopowers/offers/$ARGUMENTS/pricing.md` — ако не съществува: "Няма ценообразуване — стартирайте /eop-price $ARGUMENTS"
3. `./eopowers/company-profile.md` — ако не съществува: "Няма фирмен профил — стартирайте /init"
4. `./eopowers/domain.md` — ако не съществува: "Стартирайте /init първо"

# Генериране на оферта за поръчка $ARGUMENTS

## Чеклист

- [ ] Зареждане на шаблон от документацията
- [ ] Попълване на фирмени данни (хедър)
- [ ] Попълване на изисквания (лява/дясна колона)
- [ ] Попълване на ценово предложение
- [ ] КСС фаза A — mapping plan (matched/ambiguous/unmapped)
- [ ] КСС фаза B — резолюция на ambiguous/unmapped редове
- [ ] КСС фаза C — запис + проверка срещу прогнозна стойност
- [ ] Добавяне на подпис и печат блок
- [ ] Запис на offer-draft.docx и kss-filled.xlsx
- [ ] Включване на price-analyses.xlsx (ако е наличен)

---

## 1. Зареждане на шаблон

Прочети `analysis.md` и намери идентифицираните шаблони (DOCX и XLSX). Файловете се намират в:

```
./eopowers/offers/$ARGUMENTS/attachments/
```

**ВАЖНО:** Използвай `os.walk()` вместо glob за намиране на файлове — Windows ZIP архиви могат да създадат директории с `\` в името на Linux:

```python
python3 -c "
import os
attachments = './eopowers/offers/$ARGUMENTS/attachments'
templates = []
for root, dirs, files in os.walk(attachments):
    for f in files:
        if f.endswith(('.docx', '.xlsx', '.xls')):
            templates.append(os.path.join(root, f))
for t in templates:
    print(t)
"
```

Ако в анализа няма идентифициран шаблон, покажи списъка с намерени DOCX/XLSX файлове и помоли потребителя да избере.

---

## 2. Попълване на DOCX шаблон

Генерирай Python скрипт, базиран на конкретната структура на намерения шаблон.

**Стратегия за попълване (fuzzy matching):**

1. **Dot-field pass:** Намери клетки, съдържащи 3+ последователни точки (`...`). Това са полета за попълване. Съпостави по label-а в съседната клетка или по prefix текста в същата клетка.

2. **Empty-field pass:** Намери клетки, които са празни или съдържат само whitespace. Съпостави по header/label клетката в същия ред или колона.

3. **Label matching:** Нормализирай текста преди сравнение:
   ```python
   import re
   def normalize(text):
       return re.sub(r'\s+', ' ', str(text or '')).strip().lower()
   
   def fuzzy_match(label, target):
       return normalize(target) in normalize(label) or normalize(label) in normalize(target)
   ```

Пример за попълване:

```python
python3 << 'PYTHON_SCRIPT'
from docx import Document
import re

def normalize(text):
    return re.sub(r'\s+', ' ', str(text or '')).strip().lower()

def is_fill_field(text):
    """Check if cell contains dots (fill-in field) or is empty"""
    return bool(re.search(r'\.{3,}', str(text or ''))) or not str(text or '').strip()

doc = Document('path/to/template.docx')

# Данни за попълване (от company-profile.md и pricing.md)
fill_data = {
    'участник': 'ТЕКОМ ООД',
    'еик': '833035116',
    # ... всички полета
}

for table in doc.tables:
    for row in table.rows:
        cells = row.cells
        for i, cell in enumerate(cells):
            if is_fill_field(cell.text):
                # Търси label в съседна клетка (вляво) или в хедъра
                label = ''
                if i > 0:
                    label = cells[i-1].text
                elif len(cells) >= 2:
                    label = cells[0].text
                
                # Fuzzy match с данните за попълване
                for key, value in fill_data.items():
                    if normalize(key) in normalize(label):
                        cell.text = str(value)
                        break

doc.save('path/to/offer-draft.docx')
PYTHON_SCRIPT
```

Реалният скрипт трябва да се адаптира към конкретната структура на шаблона.

---

## 3. Попълване на фирмени данни

Вмъкни в хедъра/първата секция на документа:

| Поле | Стойност |
|------|---------|
| Наименование на участника | [от company-profile.md] |
| ЕИК | [от профила] |
| ДДС номер | [от профила] |
| Адрес | [от профила] |
| Управител | [от профила] |
| ISO сертификати | [от профила] |

---

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

---

## 5. Подпис и печат блок

Добави в края на DOCX документа:

```
Дата: [текуща дата]
Управител: [име от профила]
Подпис: _______________
Печат:
```

---

## 6. Изходни файлове

Запази готовите документи:

- `./eopowers/offers/$ARGUMENTS/offer-draft.docx`
- `./eopowers/offers/$ARGUMENTS/kss-filled.xlsx` (ако има КСС)
- `./eopowers/offers/$ARGUMENTS/price-analyses.xlsx` (ако е генериран от /eop-price — проверете дали файлът съществува)

---

Офертните документи са генерирани. Използвайте `/eop-review $ARGUMENTS` за финален преглед.
