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
- [ ] Попълване на КСС (ако има)
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

Ако в шаблоните има XLSX файл (КСС), генерирай скрипт базиран на конкретната му структура. Типична структура на КСС: №, Описание, Ед. мярка, Количество, Ед. цена, Обща стойност:

```python
python3 << 'PYTHON_SCRIPT'
from openpyxl import load_workbook

wb = load_workbook('path/to/kss-template.xlsx')
ws = wb.active

# Намери колоните за единична цена и обща стойност
# Попълни от pricing.md

import re

def normalize(text):
    return re.sub(r'\s+', ' ', str(text or '')).strip().lower()

# За съпоставяне на описания от KSS с pricing.md:
# Използвай substring containment след нормализация
for row in range(2, ws.max_row + 1):
    description = ws.cell(row=row, column=2).value
    quantity = ws.cell(row=row, column=4).value
    if description and quantity:
        norm_desc = normalize(description)
        for pricing_item in pricing_items:
            if normalize(pricing_item['description']) in norm_desc or norm_desc in normalize(pricing_item['description']):
                ws.cell(row=row, column=5).value = pricing_item['unit_price']
                ws.cell(row=row, column=6).value = float(quantity) * pricing_item['unit_price']
                break

wb.save('path/to/kss-filled.xlsx')
PYTHON_SCRIPT
```

Ако няма КСС/XLSX файл, пропусни тази стъпка.

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
