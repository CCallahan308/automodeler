# Adding Screenshots to AutoModeler

## Image File Guide

The project README references 4 screenshot images. Save them to the `/assets` folder with these exact filenames:

### 1. Dashboard Overview with KPI Metrics
**Filename**: `01-dashboard-overview.png`
**Description**: Shows the main dashboard with KPI cards displaying Revenue, Net Income, Cash, and Debt metrics
**From**: First screenshot showing the Margin Analysis tab

### 2. Historical Performance - Revenue & Net Income Trends
**Filename**: `02-historical-performance.png`
**Description**: Shows the Historical Performance tab with combined bar/line chart of revenue vs net income
**From**: Second screenshot showing revenue bars and net income line with dual axes

### 3. Classic Model View - Full 3-Statement Table
**Filename**: `03-classic-model-view.png`
**Description**: Shows the Classic Model View tab displaying the Income Statement and Balance Sheet in table format
**From**: Third screenshot showing formatted financial statement tables

### 4. Cash Flow Analysis
**Filename**: `04-cash-flow-analysis.png`
**Description**: Shows the Cash Flow tab with OCF and Capex bars plus FCF trend line
**From**: Fourth screenshot showing the cash flow breakdown

## How to Save Images

1. Save each screenshot to `/assets` folder with the names above
2. Images should be PNG format (recommended for GitHub)
3. Keep images at reasonable size (screenshot resolution is fine)

## Next Steps

After saving images to `/assets`:

```bash
cd assets
ls  # Verify all 4 files are present
cd ..
git add assets/
git commit -m "Add screenshot assets to README"
git push
```

The README will automatically display these images when pushed to GitHub!
