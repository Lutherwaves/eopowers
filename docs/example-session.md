# Example session — full pipeline on one tender

A realistic Claude Code session showing how the five `/eop-*` skills compose. Names and IDs are fabricated; output is elided with `...` where it would otherwise be repetitive.

This is meant for new users who installed the plugin and want to know "what does this actually look like end-to-end."

---

## 0. One-time setup

```
> /init
```

Claude reads your company website (or asks for one), pulls firm data into `company-profile.md`, then walks you through choosing a domain preset.

```
> What is your company website URL?
< https://example-company.bg

✓ Извлечени фирмени данни от example-company.bg:
  - Наименование: ПРИМЕР ЕООД
  - ЕИК: 200000000
  - ДДС: BG200000000
  - Адрес: гр. София, ул. ...
  - Управител: Иван Иванов

✓ Намерени ISO сертификати: ISO 9001, ISO 14001, ISO 45001

? Кой домейн преобладава в дейността ви?
  1. Construction (СМР, изолация, фасади, енергийна ефективност)
  2. Custom — конфигурирай ръчно
< 1

✓ Записани: company-profile.md, domain.md
```

You only do this once. After that:

---

## 1. Scan for open tenders

```
> /eop-scan
```

Claude opens eop.bg, runs your domain's keyword set, merges results, scores by relevance and ROI, writes `eopowers/scans/YYYY-MM-DD-scan.md`.

```
< Сканиране на eop.bg за ключови думи: ['СМР', 'топлоизолация', 'фасада', 'санирaне', ...]
  Намерени 47 уникални поръчки. Филтриране по прогнозна стойност > 10000 лв., краен срок > 5 дни...
  
| ID    | Възложител              | Прогноза   | Срок       | Score | Тип        |
|-------|-------------------------|------------|------------|-------|------------|
| 12847 | Община Кюстендил        | 145 000 лв | 2026-05-12 | 8.5   | санирaне   |
| 12903 | Община Враца            |  89 200 лв | 2026-05-08 | 7.2   | фасада     |
| ...   | ...                     |     ...    |    ...     |  ...  |    ...     |

✓ Записан: eopowers/scans/2026-04-28-scan.md
```

You pick one. Let's say `12847`.

---

## 2. Analyze the tender

```
> /eop-analyze 12847
```

Claude downloads all attachments (Решение, Обявление, Документация, КСС шаблон, Техническа спецификация, ...), extracts structured requirements, and writes `analysis.md`.

```
< Изтегляне на 8 документа от eop.bg (poръчка 12847)...
  Извличане на изисквания от ТС.docx (47 страници)...
  Разпознаване на КСС шаблон: kss-template.xlsx (82 реда)...
  
✓ Идентифицирани изисквания:
  - Прогнозна стойност: 145 000 лв. без ДДС
  - Срок за изпълнение: 90 календарни дни
  - Гаранция за изпълнение: 3% от стойността
  - Критерий: оптимално съотношение качество/цена (50/50)
  - Изискван опит: 2 обекта от подобен вид за последните 5 г.
  - ...

✓ Записан: eopowers/offers/12847/analysis.md
```

Read `analysis.md` and decide whether to bid. Assume yes.

---

## 3. Build pricing

```
> /eop-price 12847
```

Claude reads `analysis.md` + KSS template, runs market research per material, builds unit prices with П1–П5 breakdowns where required, sums against прогнозна стойност.

```
< Извличане на 82 позиции от КСС шаблона...
  Market research: керамзитобетонни блокчета 200мм, EPS 100мм, ...
  Изчисляване на единични цени с П1–П5 разбивка...
  
✓ Сума на офертата: 142 380 лв. (98.2% от прогнозната — в безопасния диапазон)

✓ Записани:
  - eopowers/offers/12847/pricing.md
  - eopowers/offers/12847/price-analyses.xlsx (П1–П5 единични анализи)
```

Review `pricing.md`. Adjust margins if needed and re-run.

---

## 4. Generate offer documents

```
> /eop-generate 12847
```

Now the КСС three-phase fill from issue #5 kicks in.

### Phase A — mapping plan

```
< Phase A: изграждане на mapping plan...
  
[
  {"row": 12, "desc": "Демонтаж на стара дограма", "qty": 24, "status": "matched", ...},
  {"row": 14, "desc": "Разкачане и закачане на инсталации", "qty": 2, "status": "unmapped"},
  {"row": 27, "desc": "Кабел СВТ 3х2.5", "qty": 60, "status": "ambiguous", "matches": [
      {"description": "Кабел СВТ 3x2.5 м"},
      {"description": "Кабел СВТ 3x2.5 мм²"}
  ]},
  ...
]
```

### Phase B — halt and resolve

```
⚠️ Фаза B: 3 реда се нуждаят от резолюция:

| Row | Description                          | Qty | Status     | Suggestions
|-----|--------------------------------------|-----|------------|----------------------------
|  14 | Разкачане и закачане на инсталации   |   2 | unmapped   | (нито една)
|  27 | Кабел СВТ 3х2.5                      |  60 | ambiguous  | "Кабел СВТ 3x2.5 м" / "...мм²"
|  39 | Съставяне на протоколи               |   5 | unmapped   | (нито една)

? Ред 14 — изберете:
  1. Дай ед. цена + обосновка
  2. Маркирай като неприложима
< 1
? Ед. цена за "Разкачане и закачане на инсталации" (лв.):
< 45.00
? Кратка обосновка (записва се в pricing.md):
< Труд - 1.5 ч × 30 лв/ч

✓ pricing.md обновен с нов ред.

? Ред 27 — изберете една от предложените:
  1. Кабел СВТ 3x2.5 м (8.20 лв./м)
  2. Кабел СВТ 3x2.5 мм² (8.20 лв./м)
< 1

? Ред 39 — изберете:
  1. Дай ед. цена + обосновка
  2. Маркирай като неприложима
< 2
✓ Ред 39 ще остане празен; ще се добави бележка в мотивационното писмо.
```

### Phase C — write + cap-check

```
< Phase C: запис + проверка на тавана...
  Total: 142 470 лв. (под прогнозна 145 000 лв.) ✓

✓ Записани:
  - eopowers/offers/12847/offer-draft.docx
  - eopowers/offers/12847/kss-filled.xlsx
  - eopowers/offers/12847/price-analyses.xlsx
```

If the total had exceeded прогнозна, the skill would have refused to write `kss-filled.xlsx` and instructed you to re-run `/eop-price` with a tighter ceiling. It will not auto-shrink prices for you — that's `/eop-price`'s job.

---

## 5. Review before submission

```
> /eop-review 12847
```

Claude runs final compliance checks, converts to PDF, lists what you still need to attach manually (signed scans, garanции, etc.).

```
< Проверки:
  ✓ Всички изисквания от ТС са адресирани в офертата
  ✓ Обща стойност (142 380 лв.) < прогнозна (145 000 лв.)
  ✓ Няма празни задължителни полета
  ⚠️ Изискване #14: липсва декларация за конфликт на интереси (Образец №3)

  Остават 4 дни до крайния срок.

? Конвертиране в PDF? (д/н)
< д
✓ offer-draft.pdf, kss-filled.pdf

✓ Офертата е готова. Не забравяйте да подготвите ръчно:
  - Подписана и сканирана декларация Образец №3
  - Гаранция за участие (3% × 145 000 = 4 350 лв.)
  - Удостоверение за актуално състояние от търговския регистър
```

Submit on eop.bg manually.

---

## What the skills do *not* do

- Submit offers on your behalf — you do that in the eop.bg portal
- Sign or stamp documents — manual step
- Make pricing decisions inside `/eop-generate` — pricing lives in `/eop-price` (this is enforced after [#5](https://github.com/Lutherwaves/eopowers/issues/5))
- Move files outside `eopowers/offers/<id>/` in your workspace

---

## Troubleshooting one-liners

- "Няма анализ" → run `/eop-analyze <id>` first
- "Няма ценообразуване" → run `/eop-price <id>` first
- КСС total > прогнозна → re-run `/eop-price <id>` with a tighter target ceiling, then `/eop-generate <id>` again
- eop.bg login required → Playwright will pause and ask you to log in interactively
