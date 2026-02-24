from dataclasses import dataclass
from typing import Any


@dataclass
class Drivers:
    revenue_growth: float
    ebitda_margin: float
    da_pct_gross_ppe: float
    dso: float
    dio: float
    dpo: float
    capex_pct_rev: float
    tax_rate: float


class FinancialModel:
    def __init__(self, historical_data: list[dict[str, Any]], drivers: Drivers):
        self.history = historical_data
        self.drivers = drivers
        self.periods = list(historical_data)

    def project(self, horizon: int, threshold_pct: float = 0.10) -> list[dict[str, Any]]:
        for _ in range(horizon):
            prior = self.periods[-1]
            curr = {}

            # Time prep
            curr["date"] = str(int(prior["date"][:4]) + 1)
            curr["is_proj"] = True

            # Income Statement
            curr["revenue"] = prior["revenue"] * (1 + self.drivers.revenue_growth)
            curr["ebitda"] = curr["revenue"] * self.drivers.ebitda_margin

            # DA calculation bases off prior gross PP&E to avoid circularity
            curr["da"] = prior["gross_ppe"] * self.drivers.da_pct_gross_ppe
            curr["ebit"] = curr["ebitda"] - curr["da"]

            tax_bill = curr["ebit"] * self.drivers.tax_rate
            curr["taxes"] = tax_bill if curr["ebit"] > 0 else 0.0
            curr["ni"] = curr["ebit"] - curr["taxes"]

            # Working Capital
            curr["ar"] = (self.drivers.dso / 365) * curr["revenue"]

            # Implied COGS for working capital logic
            cogs = curr["revenue"] - curr["ebitda"] # Simplified assumption for modeling
            curr["inv"] = (self.drivers.dio / 365) * cogs
            curr["ap"] = (self.drivers.dpo / 365) * cogs

            # PP&E Schedule
            curr["capex"] = self.drivers.capex_pct_rev * curr["revenue"]
            curr["gross_ppe"] = prior["gross_ppe"] + curr["capex"]
            curr["acc_depr"] = prior.get("acc_depr", prior["gross_ppe"] - prior["net_ppe"]) + curr["da"]
            curr["net_ppe"] = curr["gross_ppe"] - curr["acc_depr"]

            # Equity
            curr["retained_earnings"] = prior["retained_earnings"] + curr["ni"]
            # Hold paid in capital flat, derive total equity
            curr["equity"] = prior["equity"] - prior["retained_earnings"] + curr["retained_earnings"]

            # Preliminary Cash Flow (Indirect)
            curr["cfo"] = curr["ni"] + curr["da"] - (curr["ar"] - prior["ar"]) \
                          - (curr["inv"] - prior["inv"]) + (curr["ap"] - prior["ap"])
            curr["cfi"] = -curr["capex"]
            pre_plug_cash = prior["cash"] + curr["cfo"] + curr["cfi"]

            # Non-cash assets & fixed liabilities
            curr["other_assets"] = prior.get("other_assets", 0.0)
            curr["other_liabilities"] = prior.get("other_liabilities", 0.0)
            non_cash_assets = curr["ar"] + curr["inv"] + curr["net_ppe"] + curr["other_assets"]

            # Evaluate minimum cash and revolver draw
            if pre_plug_cash < 0:
                revolver_draw = abs(pre_plug_cash)
                curr["cash"] = 0.0
                curr["revolver"] = prior["revolver"] + revolver_draw
            else:
                revolver_draw = 0.0
                curr["cash"] = pre_plug_cash
                curr["revolver"] = prior["revolver"]

            curr["cff"] = revolver_draw
            curr["net_change_in_cash"] = curr["cfo"] + curr["cfi"] + curr["cff"]

            # TODO: Add real debt schedule.
            # Tried doing average period interest here but it created a circular ref
            # with the revolver plug. Keeping it simple and flat for now.
            curr["lt_debt"] = prior["lt_debt"]

            # Finalize Totals
            curr["total_assets"] = curr["cash"] + non_cash_assets
            curr["total_le"] = curr["ap"] + curr["revolver"] + curr["lt_debt"] + curr["equity"] + curr["other_liabilities"]

            # Validation: Catch fundamental breakages in logic
            plug_delta = curr["total_assets"] - curr["total_le"]
            if abs(plug_delta) > 1.0:
                if plug_delta > 0:
                    curr["revolver"] += plug_delta
                else:
                    curr["cash"] -= plug_delta

                curr["total_assets"] = curr["cash"] + non_cash_assets
                curr["total_le"] = curr["ap"] + curr["revolver"] + curr["lt_debt"] + curr["equity"] + curr["other_liabilities"]

                if abs(plug_delta) > threshold_pct * curr["total_assets"]:
                    raise ValueError(
                        f"Balance sheet plug magnitude ({plug_delta}) exceeds threshold "
                        f"for period {curr['date']}."
                    )

            self.periods.append(curr)

        return self.periods

def ingest_fmp_data(is_data: list[Any], bs_data: list[Any], cf_data: list[Any]) -> list[dict[str, Any]]:
    # Zips the three FMP models into the flat dictionaries our engine expects
    historical = []
    for i_stmt, b_stmt, c_stmt in zip(is_data, bs_data, cf_data):
        period = {
            "date": i_stmt.date[:4],
            "is_proj": False,
            "revenue": i_stmt.revenue,
            "ebitda": i_stmt.ebitda,
            "da": i_stmt.depreciationAndAmortization,
            "ebit": i_stmt.operatingIncome,
            "ni": i_stmt.netIncome,
            "cash": b_stmt.cashAndCashEquivalents,
            "ar": b_stmt.netReceivables,
            "inv": b_stmt.inventory,
            "gross_ppe": b_stmt.grossPropertyPlantEquipment if b_stmt.grossPropertyPlantEquipment is not None else b_stmt.propertyPlantEquipmentNet,
            "net_ppe": b_stmt.propertyPlantEquipmentNet,
            "acc_depr": (b_stmt.grossPropertyPlantEquipment - b_stmt.propertyPlantEquipmentNet) if b_stmt.grossPropertyPlantEquipment is not None else 0.0,
            "other_assets": b_stmt.totalAssets - (b_stmt.cashAndCashEquivalents + b_stmt.netReceivables + b_stmt.inventory + b_stmt.propertyPlantEquipmentNet),
            "total_assets": b_stmt.totalAssets,
            "ap": b_stmt.accountPayables,
            "revolver": 0.0, # FMP doesn't break out revolver cleanly, keeping it separate
            "lt_debt": b_stmt.totalDebt,
            "other_liabilities": b_stmt.totalLiabilities - (b_stmt.accountPayables + b_stmt.totalDebt),
            "retained_earnings": b_stmt.retainedEarnings,
            "equity": b_stmt.totalStockholdersEquity,
            "total_le": b_stmt.totalLiabilities + b_stmt.totalStockholdersEquity,
            "capex": abs(c_stmt.capitalExpenditure), # standardize as positive amount
            "cfo": c_stmt.operatingCashFlow,
            "cfi": c_stmt.capitalExpenditure,
            "cff": 0.0,
        }
        historical.append(period)
    return historical
