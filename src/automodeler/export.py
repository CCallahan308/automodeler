from typing import Any

import xlsxwriter
from xlsxwriter.utility import xl_rowcol_to_cell


def build_excel_model(filepath: str, periods: list[dict[str, Any]], drivers: Any):
    wb = xlsxwriter.Workbook(filepath)
    ws = wb.add_worksheet("3-Statement Model")

    fmt_header = wb.add_format({"bold": True, "bottom": 1})
    fmt_blue_pct = wb.add_format({"font_color": "#0000FF", "num_format": "0.0%"})
    fmt_green_num = wb.add_format({"font_color": "#008000", "num_format": "#,##0"})
    fmt_black_num = wb.add_format({"font_color": "#000000", "num_format": "#,##0"})
    fmt_label = wb.add_format({"bold": True})

    ws.freeze_panes(1, 1)
    ws.set_column(0, 0, 30)

    # NOTE: Hardcoding row indices is a bit brittle,
    # but it avoids a massive abstraction for a single sheet.
    R_ASSUMPTIONS_HDR = 1
    R_REV_GROWTH = 2
    R_EBITDA_MARGIN = 3
    R_DA_PCT = 4
    R_DSO = 5
    R_DIO = 6
    R_DPO = 7
    R_CAPEX_PCT = 8
    R_TAX_RATE = 9

    R_IS_HDR = 11
    R_REV = 12
    R_EBITDA = 13
    R_DA = 14
    R_EBIT = 15
    R_TAXES = 16
    R_NI = 17

    R_BS_HDR = 19
    R_CASH = 20
    R_AR = 21
    R_INV = 22
    R_GROSS_PPE = 23
    R_ACC_DEPR = 24
    R_NET_PPE = 25
    R_OTHER_ASSETS = 26
    R_TOTAL_ASSETS = 27

    R_AP = 29
    R_REVOLVER = 30
    R_LT_DEBT = 31
    R_OTHER_LIABILITIES = 32
    R_EQUITY = 33
    R_RE = 34
    R_TOTAL_LE = 35
    R_CHECK = 36

    R_CF_HDR = 38
    R_CFO_NI = 39
    R_CFO_DA = 40
    R_CFO_AR = 41
    R_CFO_INV = 42
    R_CFO_AP = 43
    R_CFO = 44
    R_CFI_CAPEX = 45
    R_CFF_REV = 46
    R_NET_CASH = 47

    # Labels
    ws.write(R_ASSUMPTIONS_HDR, 0, "Assumptions", fmt_label)
    ws.write(R_REV_GROWTH, 0, "Revenue Growth")
    ws.write(R_EBITDA_MARGIN, 0, "EBITDA Margin")
    ws.write(R_DA_PCT, 0, "D&A % Gross PP&E")
    ws.write(R_DSO, 0, "DSO")
    ws.write(R_DIO, 0, "DIO")
    ws.write(R_DPO, 0, "DPO")
    ws.write(R_CAPEX_PCT, 0, "Capex % Rev")
    ws.write(R_TAX_RATE, 0, "Tax Rate")

    ws.write(R_IS_HDR, 0, "Income Statement", fmt_label)
    ws.write(R_REV, 0, "Revenue")
    ws.write(R_EBITDA, 0, "EBITDA")
    ws.write(R_DA, 0, "D&A")
    ws.write(R_EBIT, 0, "EBIT")
    ws.write(R_TAXES, 0, "Taxes")
    ws.write(R_NI, 0, "Net Income")

    ws.write(R_BS_HDR, 0, "Balance Sheet", fmt_label)
    ws.write(R_CASH, 0, "Cash")
    ws.write(R_AR, 0, "Accounts Receivable")
    ws.write(R_INV, 0, "Inventory")
    ws.write(R_GROSS_PPE, 0, "Gross PP&E")
    ws.write(R_ACC_DEPR, 0, "Accumulated Depreciation")
    ws.write(R_NET_PPE, 0, "Net PP&E")
    ws.write(R_OTHER_ASSETS, 0, "Other Assets")
    ws.write(R_TOTAL_ASSETS, 0, "Total Assets")
    ws.write(R_AP, 0, "Accounts Payable")
    ws.write(R_REVOLVER, 0, "Revolver")
    ws.write(R_LT_DEBT, 0, "Long-Term Debt")
    ws.write(R_OTHER_LIABILITIES, 0, "Other Liabilities")
    ws.write(R_EQUITY, 0, "Paid-in Capital / Other Equity")
    ws.write(R_RE, 0, "Retained Earnings")
    ws.write(R_TOTAL_LE, 0, "Total L&E")
    ws.write(R_CHECK, 0, "Check")

    ws.write(R_CF_HDR, 0, "Cash Flow Statement", fmt_label)
    ws.write(R_CFO_NI, 0, "Net Income")
    ws.write(R_CFO_DA, 0, "D&A")
    ws.write(R_CFO_AR, 0, "Change in AR")
    ws.write(R_CFO_INV, 0, "Change in Inventory")
    ws.write(R_CFO_AP, 0, "Change in AP")
    ws.write(R_CFO, 0, "Cash Flow from Operations")
    ws.write(R_CFI_CAPEX, 0, "Capital Expenditures")
    ws.write(R_CFF_REV, 0, "Change in Revolver")
    ws.write(R_NET_CASH, 0, "Net Change in Cash")

    for col_idx, period in enumerate(periods, start=1):
        ws.write(0, col_idx, period["date"], fmt_header)
        ws.set_column(col_idx, col_idx, 15)

        c = xl_rowcol_to_cell

        if not period["is_proj"]:
            # Write hardcoded history in green
            ws.write_number(R_REV, col_idx, period["revenue"], fmt_green_num)
            ws.write_number(R_EBITDA, col_idx, period["ebitda"], fmt_green_num)
            ws.write_number(R_DA, col_idx, period["da"], fmt_green_num)
            ws.write_number(R_EBIT, col_idx, period["ebit"], fmt_green_num)
            ws.write_number(R_TAXES, col_idx, 0, fmt_green_num)
            ws.write_number(R_NI, col_idx, period["ni"], fmt_green_num)

            ws.write_number(R_CASH, col_idx, period["cash"], fmt_green_num)
            ws.write_number(R_AR, col_idx, period["ar"], fmt_green_num)
            ws.write_number(R_INV, col_idx, period["inv"], fmt_green_num)
            ws.write_number(R_GROSS_PPE, col_idx, period["gross_ppe"], fmt_green_num)
            ws.write_number(R_ACC_DEPR, col_idx, period["acc_depr"], fmt_green_num)
            ws.write_number(R_NET_PPE, col_idx, period["net_ppe"], fmt_green_num)
            ws.write_number(R_OTHER_ASSETS, col_idx, period["other_assets"], fmt_green_num)
            ws.write_number(R_TOTAL_ASSETS, col_idx, period["total_assets"], fmt_green_num)

            ws.write_number(R_AP, col_idx, period["ap"], fmt_green_num)
            ws.write_number(R_REVOLVER, col_idx, period["revolver"], fmt_green_num)
            ws.write_number(R_LT_DEBT, col_idx, period["lt_debt"], fmt_green_num)
            ws.write_number(R_OTHER_LIABILITIES, col_idx, period["other_liabilities"], fmt_green_num)
            paid_in_cap = period["equity"] - period["retained_earnings"]
            ws.write_number(R_EQUITY, col_idx, paid_in_cap, fmt_green_num)
            ws.write_number(R_RE, col_idx, period["retained_earnings"], fmt_green_num)
            ws.write_number(R_TOTAL_LE, col_idx, period["total_le"], fmt_green_num)
            ws.write_number(R_CHECK, col_idx, 0, fmt_green_num)

            # Historical CF
            ws.write_number(R_CFO_NI, col_idx, period["ni"], fmt_green_num)
            ws.write_number(R_CFO_DA, col_idx, period["da"], fmt_green_num)
            ws.write_number(R_CFO_AR, col_idx, 0, fmt_green_num)
            ws.write_number(R_CFO_INV, col_idx, 0, fmt_green_num)
            ws.write_number(R_CFO_AP, col_idx, 0, fmt_green_num)
            ws.write_number(R_CFO, col_idx, period["cfo"], fmt_green_num)
            ws.write_number(R_CFI_CAPEX, col_idx, -period["capex"], fmt_green_num)
            ws.write_number(R_CFF_REV, col_idx, period["cff"], fmt_green_num)

            ws.write_formula(R_NET_CASH, col_idx, f"=SUM({c(R_CFO, col_idx)}:{c(R_CFF_REV, col_idx)})", fmt_black_num)
        else:
            # Write assumptions (Blue)
            ws.write_number(R_REV_GROWTH, col_idx, drivers.revenue_growth, fmt_blue_pct)
            ws.write_number(R_EBITDA_MARGIN, col_idx, drivers.ebitda_margin, fmt_blue_pct)
            ws.write_number(R_DA_PCT, col_idx, drivers.da_pct_gross_ppe, fmt_blue_pct)
            ws.write_number(R_DSO, col_idx, drivers.dso, fmt_blue_pct)
            # Overwrite DPO/DIO styles directly for inputs
            fmt_blue_num = wb.add_format({"font_color": "#0000FF", "num_format": "#,##0"})
            ws.write_number(R_DSO, col_idx, drivers.dso, fmt_blue_num)
            ws.write_number(R_DIO, col_idx, drivers.dio, fmt_blue_num)
            ws.write_number(R_DPO, col_idx, drivers.dpo, fmt_blue_num)
            ws.write_number(R_CAPEX_PCT, col_idx, drivers.capex_pct_rev, fmt_blue_pct)
            ws.write_number(R_TAX_RATE, col_idx, drivers.tax_rate, fmt_blue_pct)

            # Income Statement Formulas
            ws.write_formula(R_REV, col_idx, f"={c(R_REV, col_idx-1)}*(1+{c(R_REV_GROWTH, col_idx)})", fmt_black_num)
            ws.write_formula(R_EBITDA, col_idx, f"={c(R_REV, col_idx)}*{c(R_EBITDA_MARGIN, col_idx)}", fmt_black_num)
            ws.write_formula(R_DA, col_idx, f"={c(R_GROSS_PPE, col_idx-1)}*{c(R_DA_PCT, col_idx)}", fmt_black_num)
            ws.write_formula(R_EBIT, col_idx, f"={c(R_EBITDA, col_idx)}-{c(R_DA, col_idx)}", fmt_black_num)
            ws.write_formula(R_TAXES, col_idx, f"=MAX(0, {c(R_EBIT, col_idx)}*{c(R_TAX_RATE, col_idx)})", fmt_black_num)
            ws.write_formula(R_NI, col_idx, f"={c(R_EBIT, col_idx)}-{c(R_TAXES, col_idx)}", fmt_black_num)

            # Cash Flow formulas
            ws.write_formula(R_CFO_NI, col_idx, f"={c(R_NI, col_idx)}", fmt_black_num)
            ws.write_formula(R_CFO_DA, col_idx, f"={c(R_DA, col_idx)}", fmt_black_num)
            ws.write_formula(R_CFO_AR, col_idx, f"={c(R_AR, col_idx-1)}-{c(R_AR, col_idx)}", fmt_black_num)
            ws.write_formula(R_CFO_INV, col_idx, f"={c(R_INV, col_idx-1)}-{c(R_INV, col_idx)}", fmt_black_num)
            ws.write_formula(R_CFO_AP, col_idx, f"={c(R_AP, col_idx)}-{c(R_AP, col_idx-1)}", fmt_black_num)
            ws.write_formula(R_CFO, col_idx, f"=SUM({c(R_CFO_NI, col_idx)}:{c(R_CFO_AP, col_idx)})", fmt_black_num)

            # Capex
            ws.write_formula(R_CFI_CAPEX, col_idx, f"=-({c(R_REV, col_idx)}*{c(R_CAPEX_PCT, col_idx)})", fmt_black_num)

            # Balance Sheet (Non-Cash) Formulas
            ws.write_formula(R_AR, col_idx, f"=({c(R_DSO, col_idx)}/365)*{c(R_REV, col_idx)}", fmt_black_num)
            # Implied COGS for working capital logic (Rev - EBITDA)
            cogs_formula = f"({c(R_REV, col_idx)}-{c(R_EBITDA, col_idx)})"
            ws.write_formula(R_INV, col_idx, f"=({c(R_DIO, col_idx)}/365)*{cogs_formula}", fmt_black_num)
            ws.write_formula(R_AP, col_idx, f"=({c(R_DPO, col_idx)}/365)*{cogs_formula}", fmt_black_num)

            ws.write_formula(R_GROSS_PPE, col_idx, f"={c(R_GROSS_PPE, col_idx-1)}-{c(R_CFI_CAPEX, col_idx)}", fmt_black_num)
            ws.write_formula(R_ACC_DEPR, col_idx, f"={c(R_ACC_DEPR, col_idx-1)}+{c(R_DA, col_idx)}", fmt_black_num)
            ws.write_formula(R_NET_PPE, col_idx, f"={c(R_GROSS_PPE, col_idx)}-{c(R_ACC_DEPR, col_idx)}", fmt_black_num)
            ws.write_formula(R_OTHER_ASSETS, col_idx, f"={c(R_OTHER_ASSETS, col_idx-1)}", fmt_black_num)

            ws.write_formula(R_LT_DEBT, col_idx, f"={c(R_LT_DEBT, col_idx-1)}", fmt_black_num)
            ws.write_formula(R_OTHER_LIABILITIES, col_idx, f"={c(R_OTHER_LIABILITIES, col_idx-1)}", fmt_black_num)
            ws.write_formula(R_EQUITY, col_idx, f"={c(R_EQUITY, col_idx-1)}", fmt_black_num)
            ws.write_formula(R_RE, col_idx, f"={c(R_RE, col_idx-1)}+{c(R_NI, col_idx)}", fmt_black_num)

            # Plug Logic in Excel
            pre_plug_cash = f"({c(R_CASH, col_idx-1)}+{c(R_CFO, col_idx)}+{c(R_CFI_CAPEX, col_idx)})"

            ws.write_formula(R_REVOLVER, col_idx, f"={c(R_REVOLVER, col_idx-1)}+IF({pre_plug_cash}<0, ABS({pre_plug_cash}), 0)", fmt_black_num)
            ws.write_formula(R_CASH, col_idx, f"=MAX(0, {pre_plug_cash})", fmt_black_num)

            # Finalize Totals & CF Linkages
            ws.write_formula(R_CFF_REV, col_idx, f"={c(R_REVOLVER, col_idx)}-{c(R_REVOLVER, col_idx-1)}", fmt_black_num)
            ws.write_formula(R_NET_CASH, col_idx, f"={c(R_CFO, col_idx)}+{c(R_CFI_CAPEX, col_idx)}+{c(R_CFF_REV, col_idx)}", fmt_black_num)

            ws.write_formula(R_TOTAL_ASSETS, col_idx, f"=SUM({c(R_CASH, col_idx)}:{c(R_OTHER_ASSETS, col_idx)})", fmt_black_num)
            ws.write_formula(R_TOTAL_LE, col_idx, f"=SUM({c(R_AP, col_idx)}:{c(R_RE, col_idx)})", fmt_black_num)
            ws.write_formula(R_CHECK, col_idx, f"={c(R_TOTAL_ASSETS, col_idx)}-{c(R_TOTAL_LE, col_idx)}", fmt_black_num)

    wb.close()
