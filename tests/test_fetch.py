import os
from unittest.mock import MagicMock, patch

import pytest
from httpx import HTTPError

from automodeler.fetch import get_financials


@pytest.fixture
def mock_env():
    os.environ["FMP_API_KEY"] = "testkey"
    yield
    del os.environ["FMP_API_KEY"]


def get_valid_is():
    return [{
        "date": "2023-12-31",
        "revenue": 1000,
        "costOfRevenue": 400,
        "grossProfit": 600,
        "operatingExpenses": 200,
        "ebitda": 400,
        "depreciationAndAmortization": 50,
        "operatingIncome": 350,
        "netIncome": 250
    }]


def get_valid_bs():
    return [{
        "date": "2023-12-31",
        "cashAndCashEquivalents": 100,
        "netReceivables": 50,
        "inventory": 40,
        "propertyPlantEquipmentNet": 300,
        "grossPropertyPlantEquipment": 400,
        "accountPayables": 60,
        "totalDebt": 150,
        "retainedEarnings": 100,
        "totalStockholdersEquity": 200,
        "totalAssets": 490,
        "totalLiabilities": 290
    }]


def get_valid_cf():
    return [{
        "date": "2023-12-31",
        "operatingCashFlow": 300,
        "capitalExpenditure": -50
    }]


@patch("automodeler.fetch.httpx.get")
def test_valid_ticker(mock_get, mock_env):
    mock_get.side_effect = [
        MagicMock(json=lambda: get_valid_is()),
        MagicMock(json=lambda: get_valid_bs()),
        MagicMock(json=lambda: get_valid_cf())
    ]

    is_data, bs_data, cf_data = get_financials("AAPL")
    assert len(is_data) == 1
    assert is_data[0].revenue == 1000


def test_invalid_ticker_format(mock_env):
    with pytest.raises(ValueError, match="Invalid ticker format"):
        get_financials("AAPL123")


@patch("automodeler.fetch.httpx.get")
def test_missing_critical_fields(mock_get, mock_env):
    bad_bs = get_valid_bs()
    del bad_bs[0]["totalAssets"] # Remove critical field

    mock_get.side_effect = [
        MagicMock(json=lambda: get_valid_is()),
        MagicMock(json=lambda: bad_bs),
        MagicMock(json=lambda: get_valid_cf())
    ]

    with pytest.raises(ValueError, match="missing critical fields"):
        get_financials("AAPL")


@patch("automodeler.fetch.httpx.get")
@patch("automodeler.fetch.time.sleep")
def test_rate_limit_retry(mock_sleep, mock_get, mock_env):
    # Fail twice, succeed on third
    mock_resp = MagicMock(json=lambda: get_valid_is())

    mock_get.side_effect = [
        HTTPError("Rate Limit"),
        HTTPError("Rate Limit"),
        mock_resp,
        MagicMock(json=lambda: get_valid_bs()),
        MagicMock(json=lambda: get_valid_cf())
    ]

    is_data, _, _ = get_financials("AAPL")
    assert len(is_data) == 1
    assert mock_get.call_count == 5
