# Getting Started with AutoModeler

## Installation Steps

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/automodeler.git
cd automodeler
```

### 2. Create Virtual Environment (Recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

## Running the Application

```bash
python 3_statement_model.py
```

The app will start at `http://127.0.0.1:8050/`

## First Time Usage

1. **Enter a Ticker**: Type a stock ticker (e.g., AAPL, MSFT, GOOGL, TSLA)
2. **Click Generate**: Wait for data to load and model to build
3. **Review Dashboard**: Check KPIs and financial metrics
4. **Explore Tabs**:
   - Historical Performance - Revenue and net income trends
   - Margin Analysis - Profitability margins over time
   - Cash Flow - Operating cash flow and capex
   - Classic Model View - Full 3-statement table
5. **Export Model**: Download the Excel file for further analysis

## What the Tool Does

### Data Collection
- Pulls 5+ years of historical financials from Yahoo Finance
- Standardizes account names across different companies
- Calculates derived metrics (margins, growth rates)

### Model Generation
- Creates 5-year forward projections
- Builds fully-linked Excel model with formulas
- Includes assumptions sheet with driver calculations
- Ensures balance sheet balances

### Dashboard
- Interactive charts with Plotly
- Real-time KPI calculations
- Multiple view options for analysis
- Professional Bootstrap styling

## Common Issues

### Yahoo Finance Data Unavailable
Some tickers or companies may not have complete data in Yahoo Finance. Try:
- Entering a different ticker
- Checking if it's a public company
- Verifying ticker symbol spelling

### Memory Issues with Large Files
Very large companies might have extensive historical data. The tool handles this automatically, but very old companies might take longer.

### Excel Export Not Working
Make sure you have write permissions to your Downloads folder or where the file is being saved.

## Tips for Best Results

1. Use major public companies (S&P 500 stocks tend to work best)
2. Check the KPI metrics to validate data quality
3. Review the Assumptions sheet in Excel for driver calculations
4. Use the Classic Model View to verify all statements balance
5. Export and customize the model for deeper analysis

## Next Steps

After generating a model, you can:
- Add more detailed assumptions
- Build sensitivity analysis
- Create DCF valuations
- Model different scenarios
- Share with colleagues

## Troubleshooting

**Issue**: "Can't find [TICKER]"
- Solution: Verify the ticker symbol is correct and the company is public

**Issue**: App won't start
- Solution: Make sure all requirements are installed: `pip install -r requirements.txt`

**Issue**: Browser shows connection refused
- Solution: The app runs on port 8050 by default. Check it's not blocked by firewall

**Issue**: No financial data appearing
- Solution: Some tickers have limited historical data. Try another company

## Support

For issues or questions, check the main README.md or open an issue on GitHub.

Happy modeling!
