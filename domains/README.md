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
