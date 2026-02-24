import os
import tempfile
from pathlib import Path

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Form, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .export import build_excel_model
from .fetch import get_financials
from .model import Drivers, FinancialModel, ingest_fmp_data

# Load environment variables from .env file if it exists
load_dotenv()

app = FastAPI(title="Automodeler")

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

TEMP_DIR = Path(tempfile.gettempdir()) / "automodeler"
TEMP_DIR.mkdir(exist_ok=True)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/", response_class=HTMLResponse)
async def process_form(
    request: Request,
    ticker: str = Form(...),
    horizon: int = Form(5),
    rev_growth: float = Form(5.0),
    ebitda_margin: float = Form(20.0),
):
    symbol = ticker.upper().strip()
    error_msg = None
    results = None
    dl_link = None

    if not os.environ.get("FMP_API_KEY"):
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error": "The FMP_API_KEY environment variable is missing.",
            "ticker": symbol,
            "horizon": horizon,
            "rev_growth": rev_growth,
            "ebitda_margin": ebitda_margin
        })

    try:
        is_stmts, bs_stmts, cf_stmts = get_financials(symbol)
        history = ingest_fmp_data(is_stmts, bs_stmts, cf_stmts)

        base_drivers = Drivers(
            revenue_growth=rev_growth / 100.0,
            ebitda_margin=ebitda_margin / 100.0,
            da_pct_gross_ppe=0.08,
            dso=45.0,
            dio=60.0,
            dpo=30.0,
            capex_pct_rev=0.04,
            tax_rate=0.21
        )

        engine = FinancialModel(history, base_drivers)
        projected = engine.project(horizon)

        # HACK: writing to the system temp dir works fine for a local single-user tool,
        # but this will absolutely break if multiple people hit this at the exact same second
        # for the same ticker. We'd need unique hashes for the filenames in prod.
        fname = f"{symbol}_model.xlsx"
        out_path = TEMP_DIR / fname
        build_excel_model(str(out_path), projected, base_drivers)

        terminal_yr = projected[-1]
        results = {
            "ticker": symbol,
            "end_year": terminal_yr["date"],
            "revenue": f"${terminal_yr['revenue']:,.0f}",
            "ebitda": f"${terminal_yr['ebitda']:,.0f}",
            "cash": f"${terminal_yr['cash']:,.0f}",
            "assets": f"${terminal_yr['total_assets']:,.0f}",
        }
        dl_link = f"/download/{fname}"

    except Exception as e:
        error_msg = str(e)

    return templates.TemplateResponse("index.html", {
        "request": request,
        "error": error_msg,
        "summary": results,
        "download_url": dl_link,
        "ticker": symbol,
        "horizon": horizon,
        "rev_growth": rev_growth,
        "ebitda_margin": ebitda_margin
    })


@app.get("/download/{filename}")
async def fetch_excel(filename: str):
    target = TEMP_DIR / filename
    if not target.exists():
        return HTMLResponse("File not found", status_code=404)

    return FileResponse(
        path=target,
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


def main():
    uvicorn.run("automodeler.app:app", host="0.0.0.0", port=8000, reload=False)


if __name__ == "__main__":
    main()
