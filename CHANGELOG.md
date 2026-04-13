# Changelog

## 1.1.0 (2026-04-13)

### Added
- **eop-scan:** Multi-keyword search — runs separate searches per keyword and merges results (eop.bg uses AND, not OR)
- **eop-scan:** Regional buyer filtering — groups results by municipality from domain.md
- **eop-scan:** Export ZIP as primary download method with Windows path normalization
- **eop-scan:** Visual PDF fallback for scanned documents (energy certificates)
- **eop-price:** Batch pricing mode (default) — section-level multiplier instead of position-by-position Q&A
- **eop-price:** Unit price analyses generation (П1-П5) as `price-analyses.xlsx`
- **eop-generate:** Fuzzy template matching for dot-filled and empty fields
- **eop-generate:** os.walk file discovery for Windows ZIP compatibility
- **eop-generate:** price-analyses.xlsx in output file list
- **eop-review:** Expanded validation checklist (file existence, unfilled fields, ЕЕДОП reminder)
- **init:** Region auto-detection from company address
- **domains/construction.md:** Added `Допълнителни ключови думи`, `Регион`, and `П1-П5` sections

### Changed
- **eop-price:** Detailed mode is now opt-in (say "детайлен"); batch mode is default
- **pricing-guide.md:** Added batch methodology, hourly norms table, and П1-П5 formula reference

## 1.0.0 (2026-04-09)

- Renamed plugin: bloxpowers → eopowers
- Domain-configurable: construction-specific logic extracted into domain.md config
- New: domains/construction.md preset (ships with plugin)
- New: /init Step 0 — domain selection (preset or custom)
- All skills now read from ./eopowers/domain.md instead of hardcoded values
- Migration support for existing ./bloxpowers/ users

## 0.1.0 (2026-03-25)

- Първоначална версия
- Skills: start, init, eop-scan, eop-analyze, eop-price, eop-generate, eop-review
