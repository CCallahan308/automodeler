import os
import time

import httpx
from pydantic import BaseModel, ValidationError


class FMPIs(BaseModel):
    date: str
    revenue: float
    costOfRevenue: float
    grossProfit: float
    operatingExpenses: float
    ebitda: float
    depreciationAndAmortization: float
    operatingIncome: float
    netIncome: float


class FMPBs(BaseModel):
    date: str
    cashAndCashEquivalents: float
    netReceivables: float
    inventory: float
    propertyPlantEquipmentNet: float
    grossPropertyPlantEquipment: float | None = None
    accountPayables: float
    totalDebt: float
    retainedEarnings: float
    totalStockholdersEquity: float
    totalAssets: float
    totalLiabilities: float


class FMPCf(BaseModel):
    date: str
    operatingCashFlow: float
    capitalExpenditure: float


def _fetch(url, params, retries=3):
    # HACK: linear backoff because FMP rate limits are usually short.
    # might need exponential + jitter if we scale this.
    for attempt in range(retries):
        try:
            resp = httpx.get(url, params=params, timeout=10.0)
            resp.raise_for_status()
            data = resp.json()
            if not isinstance(data, list):
                raise ValueError(f"Expected list response from FMP, got {type(data)}")
            return data
        except httpx.HTTPError as e:
            if attempt == retries - 1:
                raise RuntimeError(f"FMP API request failed after {retries} attempts: {e}")
            time.sleep(2)
    return []


def get_financials(ticker: str) -> tuple[list[FMPIs], list[FMPBs], list[FMPCf]]:
    api_key = os.environ.get("FMP_API_KEY")
    if not api_key:
        raise ValueError("FMP_API_KEY environment variable is required.")

    if not (1 <= len(ticker) <= 5 and ticker.isalpha()):
        raise ValueError(f"Invalid ticker format: {ticker}")

    ticker = ticker.upper()
    base_url = "https://financialmodelingprep.com/stable"
    params = {"apikey": api_key, "symbol": ticker, "limit": 5}

    is_raw = _fetch(f"{base_url}/income-statement", params)
    bs_raw = _fetch(f"{base_url}/balance-sheet-statement", params)
    cf_raw = _fetch(f"{base_url}/cash-flow-statement", params)

    is_raw.reverse()
    bs_raw.reverse()
    cf_raw.reverse()

    try:
        income_statements = [FMPIs(**item) for item in is_raw]
        balance_sheets = [FMPBs(**item) for item in bs_raw]
        cash_flows = [FMPCf(**item) for item in cf_raw]
        return income_statements, balance_sheets, cash_flows
    except ValidationError as err:
        missing = [e["loc"][0] for e in err.errors() if e["type"] == "missing"]
        raise ValueError(f"missing critical fields: {missing}")
