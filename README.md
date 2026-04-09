# BloxPowers

A [Claude Code](https://docs.anthropic.com/en/docs/claude-code) plugin that automates participation in Bulgarian public procurement via the [ЦАИС ЕОП](https://app.eop.bg) portal.

Scans open tenders, downloads and analyzes documentation, calculates price-per-area metrics, generates pricing proposals, and produces ready-to-submit offer documents — all from within Claude Code.

## Quick Start

```bash
# Install the plugin
/plugin marketplace add Lutherwaves/bloxpowers
/plugin install bloxpowers@bloxpowers

# Set up your company profile (one-time)
/init

# Start working
/start
```

## What It Does

| Skill | Purpose |
|-------|---------|
| `start` | Main menu — pick your next action |
| `init` | One-time company profile setup from your website + manual input |
| `eop-scan` | Scan eop.bg for open construction tenders, categorize by type, prioritize by ROI |
| `eop-analyze` | Download tender docs, extract requirements, produce structured analysis |
| `eop-price` | Interactive pricing session — labor, materials, markup |
| `eop-generate` | Generate offer documents from template + company data + pricing |
| `eop-review` | Final compliance check before submission |

### Typical Workflow

```
/eop-scan        → Find relevant tenders
/eop-analyze     → Analyze tender documentation
/eop-price       → Build pricing proposal
/eop-generate    → Generate offer documents
/eop-review      → Review and finalize
```

## EOP Scan Features

The scanner is the most developed skill. It:

- **Filters** by CPV codes and keywords (positive: СМР, Довършителни, Топлоизолация, ЕЕ, Облицовки; negative: пътно, мостове, канализации, etc.)
- **Downloads and parses** tender attachments (ZIP, RAR, DOC, DOCX, PDF) to extract building area (ЗП/РЗП)
- **Calculates EUR/m²** for each tender, flagging anything under 100 EUR/m² as potentially unfeasible
- **Categorizes** tenders (Топлоизолация, ЕЕ, Ново строителство, Ремонт, Фасади, etc.)
- **Ranks by ROI** using value, competency match, time buffer, complexity, and competition factors
- **Auto-saves** scan results to `./bloxpowers/offers/scan-YYYY-MM-DD.md`

## Prerequisites

| Dependency | Why |
|------------|-----|
| [Playwright MCP plugin](https://github.com/anthropics/claude-code-playwright) | Browser automation for eop.bg |
| [python-docx](https://pypi.org/project/python-docx/) | Read/write Word documents |
| [openpyxl](https://pypi.org/project/openpyxl/) | Read/write Excel files (КСС) |
| [LibreOffice](https://www.libreoffice.org/) | Convert .doc to .docx |
| `unrar` | Extract RAR archives |
| `pdftotext` (poppler-utils) | PDF text extraction fallback |

Install on Ubuntu/Debian:

```bash
sudo apt install libreoffice unrar poppler-utils
pip install python-docx openpyxl pdfplumber
```

## How It Works

All user-facing text is in **Bulgarian** — this is a tool built for Bulgarian construction companies participating in Bulgarian public procurement.

- No company data is baked into the plugin — `init` generates a local `company-profile.md`
- All working data lives in `./bloxpowers/` in your workspace (offers, profiles, drafts)
- `app.eop.bg/today/*` is a public registry — no authentication needed for reading/downloading
- КСС (Excel quantity surveys) are the primary pricing artifact in Bulgarian construction tenders

## Plugin Structure

```
.claude-plugin/          # Plugin + marketplace manifests
hooks/                   # SessionStart hook
skills/                  # 7 skills (start, init, eop-scan, eop-analyze, eop-price, eop-generate, eop-review)
agents/                  # 2 subagent prompts (offer-analyzer, market-researcher)
```

## Contributing

PRs welcome. The plugin is prompt-based — skills are in `skills/*/SKILL.md`, agents in `agents/*.md`.

If you work in Bulgarian construction and want to improve keyword matching, area extraction patterns, or add new tender categories, contributions are especially appreciated.

## License

MIT
