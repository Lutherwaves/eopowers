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
4. `./eopowers/domain.md` — за домейн-специфична информация (по избор)

# Генериране на оферта за поръчка $ARGUMENTS

## Чеклист

- [ ] Зареждане на шаблон от документацията
- [ ] Попълване на фирмени данни (хедър)
- [ ] Попълване на изисквания (лява/дясна колона)
- [ ] Попълване на ценово предложение
- [ ] Попълване на КСС (ако има)
- [ ] Добавяне на подпис и печат блок
- [ ] Запис на offer-draft.docx и kss-filled.xlsx

---

## 1. Зареждане на шаблон

Прочети `analysis.md` и намери идентифицираните шаблони (DOCX и XLSX). Файловете се намират в:

```
./eopowers/offers/$ARGUMENTS/attachments/
```

Ако в анализа няма идентифициран шаблон, изброй всички DOCX/XLSX файлове в папката и помоли потребителя да избере.

---

## 2. Попълване на DOCX шаблон

Генерирай Python скрипт, базиран на конкретната структура на намерения шаблон. По-долу е опростен пример — реалният скрипт трябва да се адаптира към таблиците и секциите на конкретния документ:

```python
python3 << 'PYTHON_SCRIPT'
from docx import Document
import sys

doc = Document('path/to/template.docx')

# За всяка таблица в документа
for table in doc.tables:
    for row in table.rows:
        cells = row.cells
        # Ако редът е двуколонен с изискване вляво
        # Попълни дясната колона с нашия отговор
        if len(cells) >= 2:
            requirement = cells[0].text.strip()
            if requirement and not cells[1].text.strip():
                # Съпостави с изискванията от analysis.md
                cells[1].text = "[отговор базиран на фирмен профил и ценообразуване]"

doc.save('path/to/offer-draft.docx')
PYTHON_SCRIPT
```

Реалният скрипт трябва да:
- Съпостави изискванията от `analysis.md` с конкретните клетки
- Попълни отговорите използвайки данните от `company-profile.md`
- Включи конкретни компетенции, сертификати и референции
- Обработи различни структури на таблици (не само 2-колонни)

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

for row in range(2, ws.max_row + 1):  # Пропусни хедъра
    description = ws.cell(row=row, column=2).value
    quantity = ws.cell(row=row, column=4).value
    if description and quantity:
        # Съпостави с позициите от pricing.md
        unit_price = ...  # от pricing.md
        ws.cell(row=row, column=5).value = unit_price
        ws.cell(row=row, column=6).value = float(quantity) * unit_price

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

---

Офертните документи са генерирани. Използвайте `/eop-review $ARGUMENTS` за финален преглед.
