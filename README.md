# AutoModeler - 3 Statement Financial Model Generator

A web-based financial modeling tool that automatically generates linked 3-statement financial models from publicly available company data.

## Features

- **Automated Data Fetching**: Pull historical financial statements directly from Yahoo Finance
- **Fully Linked Excel Model**: Generate professional 3-statement models with integrated assumptions sheet
- **Interactive Dashboard**: View financial performance, margins, and cash flow trends
- **Classic Model View**: Display financials in traditional spreadsheet format
- **Real-time Analysis**: KPI cards showing revenue, net income, cash position, and debt metrics

## Screenshots

### Dashboard Overview with KPI Metrics
![Dashboard Overview](assets/01-dashboard-overview.png)

### Historical Performance - Revenue & Net Income Trends
![Historical Performance](assets/02-historical-performance.png)

### Classic Model View - Full 3-Statement Table
![Classic Model View](assets/03-classic-model-view.png)

### Cash Flow Analysis
![Cash Flow](assets/04-cash-flow-analysis.png)

## What's Included

- **Income Statement**: Revenue, COGS, SG&A, EBITDA, EBIT, Tax, Net Income
- **Balance Sheet**: Cash, AR, PP&E, Total Assets, AP, Debt, Equity
- **Cash Flow**: Operating cash flow, Capex, Free cash flow
- **Assumptions Sheet**: Drivers for revenue growth, margins, tax rate, D&A, and Capex
- **Projections**: 5-year forward projections based on historical averages

## Installation

```bash
git clone https://github.com/yourusername/automodeler.git
cd automodeler
pip install -r requirements.txt
```

## Requirements

- Python 3.8+
- dash
- plotly
- pandas
- yfinance
- xlsxwriter
- dash-bootstrap-components

## Usage

```bash
python 3_statement_model.py
```

Then navigate to `http://127.0.0.1:8050/` in your browser.

### How to Use

1. Enter a stock ticker symbol (e.g., AAPL, MSFT, TSLA)
2. Click "Generate" to build the model
3. Review KPI metrics at the top
4. Switch between tabs to view different analyses:
   - **Historical Performance**: Revenue vs Net Income trends
   - **Margin Analysis**: Gross, EBIT, and Net margin progression
   - **Cash Flow**: Operating cash flow and Capex breakdown
   - **Classic Model View**: Full 3-statement model in table format
5. Download the Excel file with the complete linked model

## Tabs

### Historical Performance
Combined bar and line chart showing revenue and net income over time with dual axes.

### Margin Analysis
Line chart tracking gross margin, EBIT margin, and net margin trends to analyze profitability evolution.

### Cash Flow
Stacked bar chart with OCF and Capex, plus FCF line showing available cash generation.

### Classic Model View
Formatted table view displaying the full Income Statement and Balance Sheet with all years side-by-side.

## Excel Export Features

The exported Excel file includes:

- **Assumptions Sheet**: Historical driver calculations with 5-year forward projections
- **Model Sheet**: Complete 3-statement model with formulas
  - Income Statement calculations
  - Balance sheet that balances
  - Fully integrated assumptions

All financial figures are in the company's native currency.

## Data Sources

Financial data is sourced from Yahoo Finance via the `yfinance` library. Historical data typically covers 5+ years depending on company and availability.

## Limitations

- Data quality depends on Yahoo Finance availability
- Some companies may have incomplete or non-standard reporting
- Historical drivers are used as basis for projections
- Single-scenario model (no sensitivity analysis included)

## Future Enhancements

- Scenario analysis and sensitivity tables
- DCF valuation module
- Multi-company comparison
- Custom assumption inputs before export
- Database integration for faster reloads

## License

MIT License - feel free to use and modify for your needs.

## Author

Built as a financial modeling tool for quick analysis and practice.

## Contributing

Feel free to submit issues and enhancement requests!
