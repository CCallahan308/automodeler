# Automodeler

A pragmatic 3-statement financial modeling tool. It pulls historical data from Financial Modeling Prep (FMP), projects future performance using basic operating drivers, and drops out a fully linked Excel model.

## What's in it

*   Handles indirect cash flow reconciliation and retained earnings flow.
*   Balance sheet balancing via automated cash or revolver plugs. If the plug gets too big, it throws an error instead of failing silently.
*   Hits the live FMP `/stable/` endpoints with Pydantic validation.
*   Generates an `.xlsx` file where projected periods are actual native Excel formulas (like `=B5*B6`) using `xlsxwriter`.
*   Fast stateless web interface to tweak model drivers on the fly.

## Setup & Usage

You need an FMP API key to pull the data.

### On Mac / Linux
```bash
export FMP_API_KEY="your_api_key_here"
pip install -e .
automodeler
```

### On Windows (PowerShell)
```powershell
$env:FMP_API_KEY="your_api_key_here"
pip install -e .
automodeler
```

Once it's running, open your browser to **http://localhost:8000**. Enter a ticker (e.g. AAPL), mess with the base revenue and margin assumptions, and it will output the metrics and a download link for the Excel file.

## Known Limitations

*   **Tax & Interest:** Right now it uses static assumptions. Next step is building out a real debt schedule.
*   **Share Buybacks:** The model holds equity flat outside of retained earnings. Share repurchases are ignored.
*   Working capital drivers (DSO, DIO, DPO) are standard but we should probably add deferred revenue for software tickers.
