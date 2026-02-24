import pytest

from automodeler.model import Drivers, FinancialModel


def get_base_history():
    return [{
        "date": "2023",
        "is_proj": False,
        "revenue": 1000.0,
        "ebitda": 200.0,
        "da": 50.0,
        "ebit": 150.0,
        "ni": 118.5,
        "cash": 100.0,
        "ar": 120.0,
        "inv": 80.0,
        "gross_ppe": 500.0,
        "net_ppe": 300.0,
        "acc_depr": 200.0,
        "other_assets": 0.0,
        "total_assets": 600.0,
        "ap": 90.0,
        "revolver": 0.0,
        "lt_debt": 200.0,
        "other_liabilities": 0.0,
        "equity": 310.0,
        "retained_earnings": 100.0,
        "total_le": 600.0,
        "capex": 60.0,
        "cfo": 150.0,
        "cfi": -60.0,
        "cff": 0.0,
    }]


def get_base_drivers():
    return Drivers(
        revenue_growth=0.10,
        ebitda_margin=0.25,
        da_pct_gross_ppe=0.10,
        dso=30.0,
        dio=45.0,
        dpo=35.0,
        capex_pct_rev=0.05,
        tax_rate=0.21
    )


def test_balance_sheet_balances():
    model = FinancialModel(get_base_history(), get_base_drivers())
    periods = model.project(horizon=3)

    for p in periods[1:]:
        assert pytest.approx(p["total_assets"], 0.1) == p["total_le"]


def test_ni_rolls_into_retained_earnings():
    model = FinancialModel(get_base_history(), get_base_drivers())
    periods = model.project(horizon=2)

    p1 = periods[0] # History
    p2 = periods[1] # Proj 1

    expected_re = p1["retained_earnings"] + p2["ni"]
    assert pytest.approx(p2["retained_earnings"], 0.1) == expected_re


def test_cfo_reconciles_to_cash_change():
    model = FinancialModel(get_base_history(), get_base_drivers())
    periods = model.project(horizon=2)

    p1 = periods[0]
    p2 = periods[1]

    expected_cash = p1["cash"] + p2["cfo"] + p2["cfi"] + p2["cff"]
    assert pytest.approx(p2["cash"], 0.1) == expected_cash


def test_cash_deficit_plug():
    drivers = get_base_drivers()
    # Force heavy cash burn
    drivers.revenue_growth = -0.50
    drivers.ebitda_margin = -0.50
    drivers.capex_pct_rev = 0.50

    model = FinancialModel(get_base_history(), drivers)
    periods = model.project(horizon=1)

    p2 = periods[-1]

    assert p2["cash"] == 0.0
    assert p2["revolver"] > 0.0
    assert pytest.approx(p2["total_assets"], 0.1) == p2["total_le"]
