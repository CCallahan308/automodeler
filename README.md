<div align="center">

# AutoModeler

**3-statement financial models from public data, in seconds.**

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![CI](https://github.com/CCallahan308/automodeler/actions/workflows/ci.yml/badge.svg)](https://github.com/CCallahan308/automodeler/actions/workflows/ci.yml)

</div>

---

## What this does

Type a ticker. Get a fully-linked, projection-ready Excel file — income statement, balance sheet, cash flow, all wired together with native Excel formulas (`=B5*B6`, not pasted values).

Pulls historical financials from Financial Modeling Prep (FMP), drives projections with a small set of operating assumptions you can tweak in the browser, and downloads as `.xlsx`.

## Why it's interesting

Most "auto-modeling" tools dump numbers into a sheet and call it done. Two things this one does differently:

- **Balance sheet plug as a circuit breaker.** When the model doesn't balance, most tools silently fudge a row. AutoModeler routes the difference into a cash or revolver plug — but if that plug exceeds a sanity threshold, it **throws an error** instead of pretending nothing's wrong. You want loud failures here.
- **Real Excel formulas, not values.** Projected periods are emitted as live `xlsxwriter` formulas, so opening the file in Excel and editing an assumption actually recalculates the model. Auditors and analysts can trace every cell back to its inputs.

## How it works

```
        FMP API (validated by Pydantic)
              │
              ▼
        Historicals (5y income, balance, cash flow)
              │
              ▼
   Operating drivers ── revenue, margin, capex, WC days
              │
              ▼
        Projection engine (cash / revolver plug)
              │
              ▼
        xlsxwriter — linked .xlsx download
```

The web UI is a single FastAPI page — no DB, no auth, stateless. Change a driver, see the metrics update, download the file.

## Quick start

You'll need an FMP API key (free tier works).

**macOS / Linux:**

```bash
export FMP_API_KEY="your_api_key_here"
pip install -e .
automodeler
```

**Windows (PowerShell):**

```powershell
$env:FMP_API_KEY="your_api_key_here"
pip install -e .
automodeler
```

Then open <http://localhost:8000>, enter a ticker (`AAPL`, `MSFT`, `NVDA`), and adjust the base revenue and margin assumptions. The page returns key metrics and a download link for the Excel file.

## Repo structure

```
src/automodeler/
├── app.py           # FastAPI routes + Jinja templates
├── fetch.py         # FMP API client, Pydantic-validated
├── model.py         # 3-statement model assembly + plug logic
├── export.py        # xlsxwriter formula emission
├── templates/       # browser UI
└── static/
tests/
├── test_fetch.py
└── test_model.py
```

## Known limitations

- **Tax & interest** use static assumptions. A real debt schedule is the next obvious step.
- **Share buybacks** are ignored — equity is held flat outside retained earnings.
- **Working capital** drivers (DSO, DIO, DPO) are standard, but software tickers really want deferred revenue modeled separately.
- **No DCF or LBO** — this is a 3-statement model only; valuation overlays are out of scope for v1.

## When you'd use this

- Vetting an investment thesis quickly without rebuilding a model from scratch
- Teaching the mechanics of 3-statement linkage to analysts or students
- Spot-checking a sell-side model against a clean baseline

## License

MIT — see [LICENSE](LICENSE).
