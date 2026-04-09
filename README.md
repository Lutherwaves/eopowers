# EoPowers

A [Claude Code](https://docs.anthropic.com/en/docs/claude-code) plugin that automates participation in Bulgarian public procurement via the [ЦАИС ЕОП](https://app.eop.bg) portal.

Scans open tenders, downloads and analyzes documentation, calculates price-per-area metrics, generates pricing proposals, and produces ready-to-submit offer documents — all from within Claude Code.

## Quick Start

**Via [skills.sh](https://skills.sh):**
```bash
npx skills add Lutherwaves/eopowers
```

**Via Claude Code plugin system:**
```bash
/plugin marketplace add Lutherwaves/eopowers
/plugin install eopowers@eopowers
```

Then:
```bash
/init      # Set up domain + company profile (one-time)
/start     # Main menu
```

## What It Does

| Skill | Purpose |
|-------|---------|
| `start` | Main menu — pick your next action |
| `init` | One-time company profile setup from your website + manual input |
| `eop-scan` | Scan eop.bg for open tenders, categorize by type, prioritize by ROI |
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

## Domain Configuration

eopowers ships with a construction domain preset but supports any procurement domain.
During `/init`, choose a preset or build a custom domain configuration.

Presets available:
- **Construction** — СМР, thermal insulation, energy efficiency, facades, renovation

Want to add a domain preset? See `domains/README.md` and submit a PR.

## EOP Scan Features

The scanner is the most developed skill. It:

- **Filters** by CPV codes and keywords (positive and negative, configured per domain)
- **Downloads and parses** tender attachments (ZIP, RAR, DOC, DOCX, PDF) to extract domain-specific metrics
- **Calculates cost ratios** (e.g. EUR/m² for construction), flagging tenders below feasibility thresholds
- **Categorizes** tenders using domain-defined taxonomy
- **Ranks by ROI** using value, competency match, time buffer, complexity, and competition factors
- **Auto-saves** scan results to `./eopowers/offers/scan-YYYY-MM-DD.md`

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

All user-facing text is in **Bulgarian** — this tool automates participation in Bulgarian public procurement.

- No company data is baked into the plugin — `init` generates a local `company-profile.md`
- Domain-specific logic (keywords, metrics, pricing) lives in `domain.md`, not hardcoded in skills
- All working data lives in `./eopowers/` in your workspace (offers, profiles, drafts)
- `app.eop.bg/today/*` is a public registry — no authentication needed for reading/downloading

## Plugin Structure

```
.claude-plugin/          # Plugin + marketplace manifests
hooks/                   # SessionStart hook
skills/                  # 7 skills (start, init, eop-scan, eop-analyze, eop-price, eop-generate, eop-review)
agents/                  # 2 subagent prompts (offer-analyzer, market-researcher)
domains/                 # Domain presets (construction.md, ...)
```

## Contributing

PRs welcome. The plugin is prompt-based — skills are in `skills/*/SKILL.md`, agents in `agents/*.md`.

If you work in Bulgarian construction and want to improve keyword matching, area extraction patterns, or add new tender categories, contributions are especially appreciated.

## License

MIT
