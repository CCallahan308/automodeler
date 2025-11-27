# AutoModeler

## Overview
AutoModeler is a web-based tool for generating linked 3-statement financial models from public company data. Perfect for financial analysts, students, and anyone doing quick company analysis or building AFM practice models.

## Key Features
✅ Automated financial statement collection from Yahoo Finance
✅ Linked Excel model export with formulas and assumptions
✅ Interactive web dashboard with multiple views
✅ Professional formatting with KPI metrics
✅ 5-year forward projections

## Quick Start

```bash
pip install -r requirements.txt
python 3_statement_model.py
```

Open browser to `http://127.0.0.1:8050/`

## Project Structure

```
AutoModeler/
├── 3_statement_model.py      # Main application
├── requirements.txt           # Python dependencies
├── README.md                 # Full documentation
└── .gitignore               # Git ignore file
```

## What You Can Do

1. **Generate Models** - Enter any ticker, get a 3-statement model in seconds
2. **View Dashboards** - Interactive charts for performance, margins, and cash flow analysis
3. **Export Excel** - Download fully-linked models ready for further analysis
4. **Analyze Drivers** - See historical financial drivers and forward assumptions

## Stack

- **Frontend**: Dash + Bootstrap + Plotly
- **Backend**: Python + Pandas
- **Data**: Yahoo Finance (yfinance)
- **Export**: xlsxwriter

## Use Cases

- **Quick Analysis**: Get financial snapshots of any public company
- **Practice Models**: Build AFM/FP&A exam practice models
- **Learning Tool**: Understand 3-statement integration and financial drivers
- **Starting Point**: Export and customize models for deeper analysis

## Notes

This is a simplified model generator focused on core financial statements. It's great for quick analysis but doesn't include:
- Detailed operating assumptions
- Sensitivity analysis
- DCF valuations
- Multi-scenario modeling

Perfect as a foundation to build more complex models on top of!
