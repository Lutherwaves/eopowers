# Domain Presets

Domain presets define how eopowers searches, categorizes, prices, and evaluates tenders for a specific industry.

## Available Presets

| File | Domain | Description |
|------|--------|-------------|
| `construction.md` | Строителство | СМР, thermal insulation, energy efficiency, facades, renovation |

## Creating a Custom Preset

Copy `construction.md` as a template and modify each section:

### Required sections

1. **Търсене** — search configuration
   - `Ключова дума за филтър` — primary eop.bg search keyword
   - `Положителни ключови думи` — CPV codes and keywords per category (table)
   - `Отрицателни ключови думи` — auto-exclude keywords (table)
   - `Приоритет при множество категории` — category priority order
   - `Бележки за категоризация` — special rules
   - `Допълнителни ключови думи за търсене` — extra keywords searched separately (eop.bg uses AND, not OR, so each keyword runs as a separate search and results are merged)
2. **Метрики** — what to extract from tender documents (regex patterns), feasibility thresholds
3. **Ценообразуване** — cost categories, daily rates, pricing strategy, suppliers

### Optional sections

4. **Регион** — municipality names for buyer-based regional filtering. If present, eop-scan groups results by region. Format:
   ```
   ## Регион (eop-scan)
   - Общини: City1, City2, City3
   - Радиус: до XX км от City1
   ```
5. **Параметри за анализ на единични цени** (under Ценообразуване) — П1-П5 parameters for Bulgarian construction unit price analyses. If absent, eop-price skips price-analyses.xlsx generation. Format:
   ```
   ### Параметри за анализ на единични цени
   - П1: X.XX лв./час (средна часова ставка)
   - П2: X.XX (допълнителни трудови разходи)
   - П3: X.XX (допълнителни механизация разходи)
   - П4: X.XX (доставно-складови разходи)
   - П5: X.XX (печалба)
   ```
6. **Фирмен профил** — extra fields for company-profile.md specific to your domain

All text should be in Bulgarian (user-facing output is in Bulgarian).

## Contributing

Submit a PR with your `domains/<domain-name>.md` file. It will appear automatically in the `/init` domain selection menu.
