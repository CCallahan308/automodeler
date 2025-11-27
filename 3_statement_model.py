import dash
from dash import dcc, html, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import xlsxwriter
import pandas as pd
import yfinance as yf
import io

"""
AutoModeler - 3 Statement Financial Model Generator
Automatically fetches financial data and generates linked models.
"""

def fetch_company_data(ticker_symbol):
    """Get financials from yfinance"""
    print(f"Getting {ticker_symbol}...")
    stock = yf.Ticker(ticker_symbol)
    
    is_df = stock.financials.T.sort_index()
    bs_df = stock.balance_sheet.T.sort_index()
    cf_df = stock.cashflow.T.sort_index()
    
    if is_df.empty:
        raise ValueError(f"Can't find {ticker_symbol}")

    def get_col(df, keys):
        # Yfinance sometimes uses different column names
        for k in keys:
            if k in df.columns:
                return df[k].fillna(0)
        return pd.Series(0, index=df.index)

    data = pd.DataFrame(index=is_df.index)
    
    # Pull income statement
    data['Revenue'] = get_col(is_df, ['Total Revenue', 'TotalRevenue'])
    data['COGS'] = get_col(is_df, ['Cost Of Revenue', 'CostOfRevenue'])
    data['SG&A'] = get_col(is_df, ['Selling General And Administration', 'Operating Expense'])
    data['Interest'] = get_col(is_df, ['Interest Expense', 'InterestExpense'])
    data['Tax'] = get_col(is_df, ['Tax Provision', 'TaxProvision'])
    data['Net Income'] = get_col(is_df, ['Net Income', 'NetIncome'])
    
    # Balance sheet
    data['Cash'] = get_col(bs_df, ['Cash And Cash Equivalents', 'CashAndCashEquivalents'])
    data['AR'] = get_col(bs_df, ['Receivables', 'AccountsReceivable', 'NetReceivables'])
    data['PP&E'] = get_col(bs_df, ['Net PPE', 'NetPPE', 'Gross PPE'])
    data['Total Assets'] = get_col(bs_df, ['Total Assets', 'TotalAssets'])
    data['AP'] = get_col(bs_df, ['Accounts Payable', 'AccountsPayable', 'Payables'])
    data['Debt'] = get_col(bs_df, ['Total Debt', 'TotalDebt', 'Long Term Debt'])
    data['Total Liab'] = get_col(bs_df, ['Total Liabilities Net Minority Interest', 'TotalLiabilities'])
    data['Share Capital'] = get_col(bs_df, ['Common Stock', 'CommonStock', 'ShareIssued'])
    data['Retained Earnings'] = get_col(bs_df, ['Retained Earnings', 'RetainedEarnings'])
    
    # Calculate plugs
    data['Other Assets'] = data['Total Assets'] - (data['Cash'] + data['AR'] + data['PP&E'])
    data['Total Equity'] = get_col(bs_df, ['Stockholders Equity', 'StockholdersEquity'])
    data['Other Liab'] = data['Total Liab'] - (data['AP'] + data['Debt'])
    
    # Cash flow
    data['D&A'] = get_col(cf_df, ['Depreciation And Amortization', 'Depreciation'])
    data['Capex'] = get_col(cf_df, ['Capital Expenditure', 'CapitalExpenditure'])
    data['Operating Cash Flow'] = get_col(cf_df, ['Operating Cash Flow', 'OperatingCashFlow'])
    
    data = data.fillna(0)
    
    # Get company info
    info = stock.info
    meta = {
        'name': info.get('shortName', ticker_symbol),
        'sector': info.get('sector', 'Unknown'),
        'industry': info.get('industry', 'Unknown'),
        'currency': info.get('currency', 'USD')
    }
    
    return data, meta

def generate_excel_file(ticker):
    try:
        hist_data, meta = fetch_company_data(ticker)
    except Exception as e:
        return None, None, str(e)

    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    
    # Workbook formats
    header_fmt = workbook.add_format({'bold': True, 'bg_color': '#2F5597', 'font_color': 'white', 'align': 'center', 'border': 1})
    blue_fmt = workbook.add_format({'font_color': '#0000FF', 'num_format': '#,##0'}) 
    black_fmt = workbook.add_format({'font_color': '#000000', 'num_format': '#,##0'}) 
    pct_fmt = workbook.add_format({'font_color': '#0000FF', 'num_format': '0.0%'})
    bold_fmt = workbook.add_format({'bold': True})
    title_fmt = workbook.add_format({'bold': True, 'font_size': 14, 'font_color': '#2F5597'})

    ws_inputs = workbook.add_worksheet('Assumptions')
    ws_model = workbook.add_worksheet('Model')
    
    # Set up timeline
    hist_years = [d.strftime('%Y') + "A" for d in hist_data.index]
    proj_years = [str(int(hist_years[-1][:4]) + i) + "E" for i in range(1, 6)]
    all_years = hist_years + proj_years
    hist_cols = len(hist_years)
    proj_cols = len(proj_years)
    
    # Assumptions sheet
    ws_inputs.set_column('A:A', 30)
    ws_inputs.write(0, 0, f"{meta['name']} Drivers", title_fmt)
    ws_inputs.write_row(2, 1, all_years, header_fmt)
    
    drivers = [
        "Revenue Growth %", 
        "COGS % of Revenue", 
        "SG&A % of Revenue", 
        "Tax Rate %", 
        "D&A % of PP&E", 
        "Capex % of Revenue"
    ]
    
    for r, driver in enumerate(drivers):
        ws_inputs.write(r+3, 0, driver, bold_fmt)
        for c, date_idx in enumerate(hist_data.index):
            col_idx = c + 1
            val = 0
            if driver == "Revenue Growth %":
                if c > 0:
                    curr = hist_data.loc[date_idx, 'Revenue']
                    prev = hist_data.iloc[c-1]['Revenue']
                    val = (curr / prev) - 1 if prev != 0 else 0
            elif driver == "COGS % of Revenue":
                val = hist_data.loc[date_idx, 'COGS'] / hist_data.loc[date_idx, 'Revenue'] if hist_data.loc[date_idx, 'Revenue'] != 0 else 0
            elif driver == "SG&A % of Revenue":
                val = hist_data.loc[date_idx, 'SG&A'] / hist_data.loc[date_idx, 'Revenue'] if hist_data.loc[date_idx, 'Revenue'] != 0 else 0
            elif driver == "Tax Rate %":
                pre_tax = hist_data.loc[date_idx, 'Revenue'] - hist_data.loc[date_idx, 'COGS'] - hist_data.loc[date_idx, 'SG&A'] - hist_data.loc[date_idx, 'Interest']
                val = hist_data.loc[date_idx, 'Tax'] / pre_tax if pre_tax != 0 else 0.21
            elif driver == "D&A % of PP&E":
                val = hist_data.loc[date_idx, 'D&A'] / hist_data.loc[date_idx, 'PP&E'] if hist_data.loc[date_idx, 'PP&E'] != 0 else 0
            elif driver == "Capex % of Revenue":
                val = abs(hist_data.loc[date_idx, 'Capex']) / hist_data.loc[date_idx, 'Revenue'] if hist_data.loc[date_idx, 'Revenue'] != 0 else 0

            ws_inputs.write(r+3, col_idx, val, pct_fmt)
            
        # Link projection years to last historical
        last_val_col = xlsxwriter.utility.xl_col_to_name(hist_cols)
        curr_row = r + 4
        for c in range(proj_cols):
            ws_inputs.write_formula(r+3, hist_cols + 1 + c, f"={last_val_col}{curr_row}", pct_fmt)

    ws_model.set_column('A:A', 35)
    ws_model.set_column(1, len(all_years), 14)
    ws_model.write(0, 0, f"{meta['name']} 3-Statement Model", title_fmt)
    ws_model.write_row(2, 1, all_years, header_fmt)
    
    r = 3
    ws_model.write(r, 0, "INCOME STATEMENT", bold_fmt)
    is_items = [
        ("Revenue", 'Revenue'), 
        ("COGS", 'COGS'), 
        ("Gross Profit", 'Calc'), 
        ("SG&A", 'SG&A'), 
        ("EBITDA", 'Calc'), 
        ("D&A", 'D&A'), 
        ("EBIT", 'Calc'), 
        ("Interest Expense", 'Interest'), 
        ("EBT", 'Calc'), 
        ("Tax", 'Tax'), 
        ("Net Income", 'Net Income')
    ]
    row_map = {}
    
    for label, key in is_items:
        r += 1
        row_map[label] = r + 1
        ws_model.write(r, 0, label)
        for c, date_idx in enumerate(hist_data.index):
            col = xlsxwriter.utility.xl_col_to_name(c+1)
            if key != 'Calc':
                ws_model.write(r, c+1, hist_data.loc[date_idx, key], blue_fmt)
            else:
                if label == "Gross Profit": ws_model.write_formula(r, c+1, f"={col}{row_map['Revenue']}-{col}{row_map['COGS']}", black_fmt)
                if label == "EBITDA": ws_model.write_formula(r, c+1, f"={col}{row_map['Gross Profit']}-{col}{row_map['SG&A']}", black_fmt)
                if label == "EBIT": ws_model.write_formula(r, c+1, f"={col}{row_map['EBITDA']}-{col}{row_map['D&A']}", black_fmt)
                if label == "EBT": ws_model.write_formula(r, c+1, f"={col}{row_map['EBIT']}-{col}{row_map['Interest Expense']}", black_fmt)
        
        for c in range(proj_cols):
            curr_col = hist_cols + 1 + c
            col = xlsxwriter.utility.xl_col_to_name(curr_col)
            prev_col = xlsxwriter.utility.xl_col_to_name(curr_col-1)
            asm_col = xlsxwriter.utility.xl_col_to_name(curr_col)
            
            if label == "Revenue": ws_model.write_formula(r, curr_col, f"={prev_col}{r+1}*(1+Assumptions!{asm_col}4)", black_fmt)
            elif label == "COGS": ws_model.write_formula(r, curr_col, f"={col}{row_map['Revenue']}*Assumptions!{asm_col}5", black_fmt)
            elif label == "SG&A": ws_model.write_formula(r, curr_col, f"={col}{row_map['Revenue']}*Assumptions!{asm_col}6", black_fmt)
            elif label == "Interest Expense": ws_model.write(r, curr_col, 0, black_fmt)
            elif label == "Tax": ws_model.write_formula(r, curr_col, f"={col}{row_map['EBT']}*Assumptions!{asm_col}7", black_fmt)
            elif label == "D&A": ws_model.write_formula(r, curr_col, f"={prev_col}{r+1}", black_fmt)
            
            if label == "Gross Profit": ws_model.write_formula(r, curr_col, f"={col}{row_map['Revenue']}-{col}{row_map['COGS']}", black_fmt)
            if label == "EBITDA": ws_model.write_formula(r, curr_col, f"={col}{row_map['Gross Profit']}-{col}{row_map['SG&A']}", black_fmt)
            if label == "EBIT": ws_model.write_formula(r, curr_col, f"={col}{row_map['EBITDA']}-{col}{row_map['D&A']}", black_fmt)
            if label == "EBT": ws_model.write_formula(r, curr_col, f"={col}{row_map['EBIT']}-{col}{row_map['Interest Expense']}", black_fmt)
            if label == "Net Income": ws_model.write_formula(r, curr_col, f"={col}{row_map['EBT']}-{col}{row_map['Tax']}", black_fmt)

    # Balance sheet
    r += 3
    ws_model.write(r, 0, "BALANCE SHEET", bold_fmt)
    bs_items = [
        ("Cash", 'Cash'), 
        ("Accounts Receivable", 'AR'), 
        ("PP&E", 'PP&E'), 
        ("Other Assets", 'Other Assets'), 
        ("Total Assets", 'Calc'), 
        ("Accounts Payable", 'AP'), 
        ("Debt", 'Debt'), 
        ("Other Liabilities", 'Other Liab'), 
        ("Total Liabilities", 'Calc'), 
        ("Share Capital", 'Share Capital'), 
        ("Retained Earnings", 'Retained Earnings'), 
        ("Total Equity", 'Calc'), 
        ("Check", 'Calc')
    ]
    
    for label, key in bs_items:
        r += 1
        row_map[label] = r + 1
        ws_model.write(r, 0, label)
        for c, date_idx in enumerate(hist_data.index):
            col = xlsxwriter.utility.xl_col_to_name(c+1)
            if key != 'Calc':
                ws_model.write(r, c+1, hist_data.loc[date_idx, key], blue_fmt)
            else:
                if label == "Total Assets": ws_model.write_formula(r, c+1, f"=SUM({col}{row_map['Cash']}:{col}{row_map['Other Assets']})", black_fmt)
                if label == "Total Liabilities": ws_model.write_formula(r, c+1, f"=SUM({col}{row_map['Accounts Payable']}:{col}{row_map['Other Liabilities']})", black_fmt)
                if label == "Total Equity": ws_model.write_formula(r, c+1, f"={col}{row_map['Share Capital']}+{col}{row_map['Retained Earnings']}", black_fmt)
                if label == "Check": ws_model.write_formula(r, c+1, f"={col}{row_map['Total Assets']}-({col}{row_map['Total Liabilities']}+{col}{row_map['Total Equity']})", black_fmt)
        
        for c in range(proj_cols):
            curr_col = hist_cols + 1 + c
            col = xlsxwriter.utility.xl_col_to_name(curr_col)
            prev_col = xlsxwriter.utility.xl_col_to_name(curr_col-1)
            if key not in ['Calc', 'Cash', 'Retained Earnings']:
                ws_model.write_formula(r, curr_col, f"={prev_col}{r+1}", black_fmt)
            if label == "Retained Earnings": ws_model.write_formula(r, curr_col, f"={prev_col}{r+1}+{col}{row_map['Net Income']}", black_fmt)
            if label == "Cash": ws_model.write_formula(r, curr_col, f"={prev_col}{r+1}", black_fmt) 
            if label == "Total Assets": ws_model.write_formula(r, curr_col, f"=SUM({col}{row_map['Cash']}:{col}{row_map['Other Assets']})", black_fmt)
            if label == "Total Liabilities": ws_model.write_formula(r, curr_col, f"=SUM({col}{row_map['Accounts Payable']}:{col}{row_map['Other Liabilities']})", black_fmt)
            if label == "Total Equity": ws_model.write_formula(r, curr_col, f"={col}{row_map['Share Capital']}+{col}{row_map['Retained Earnings']}", black_fmt)
            if label == "Check": ws_model.write_formula(r, curr_col, f"={col}{row_map['Total Assets']}-({col}{row_map['Total Liabilities']}+{col}{row_map['Total Equity']})", black_fmt)

    workbook.close()
    output.seek(0)
    return output, hist_data, meta

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LITERA, "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css"])

def kpi_card(title, value, subtitle, icon, color):
    return dbc.Card(
        dbc.CardBody([
            html.Div([
                html.Div([
                    html.H6(title, className="text-muted text-uppercase small mb-1"),
                    html.H3(value, className="mb-0", style={"color": color})
                ], className="flex-grow-1"),
                html.I(className=f"fas {icon} fa-2x", style={"opacity": "0.3", "color": color})
            ], className="d-flex align-items-center mb-2"),
            html.Small(subtitle, className="text-muted")
        ]),
        className="shadow-sm border-0 mb-4"
    )

sidebar = html.Div([
    html.Div([
        html.I(className="fas fa-chart-line fa-lg me-2 text-primary"),
        html.H4("AutoModeler", className="d-inline align-middle fw-bold text-primary")
    ], className="mb-5 text-center"),
    
    html.Label("Ticker", className="fw-bold text-muted small mb-2"),
    dbc.Input(id="ticker-input", placeholder="AAPL, MSFT...", type="text", className="mb-3 form-control-lg"),
    
    dbc.Button([html.I(className="fas fa-magic me-2"), "Generate"], 
               id="btn-generate", color="primary", size="lg", className="w-100 mb-4 shadow"),
    
    html.Div(id="status-alert-container"),
    html.Hr(),
    html.Small("3-Statement financial model generator.", className="text-muted fst-italic")
], style={
    "position": "fixed", "top": 0, "left": 0, "bottom": 0, "width": "300px",
    "padding": "2rem", "backgroundColor": "#f8f9fa", "borderRight": "1px solid #dee2e6"
})

content = html.Div([
    dbc.Row([
        dbc.Col([
            html.H2(id="company-name", children="Financial Model", className="fw-bold mb-0"),
            html.Span(id="company-meta", children="Enter a ticker", className="text-muted")
        ])
    ], className="mb-4 align-items-center"),

    dcc.Loading(id="loader", type="cube", color="#2F5597", children=[
        dbc.Row(id="kpi-row", className="mb-2"),
        
        dbc.Card([
            dbc.CardHeader([
                dbc.Tabs([
                    dbc.Tab(label="Historical Performance", tab_id="tab-1"),
                    dbc.Tab(label="Margin Analysis", tab_id="tab-2"),
                    dbc.Tab(label="Cash Flow", tab_id="tab-3"),
                    dbc.Tab(label="Classic Model View", tab_id="tab-4"),
                ], id="tabs", active_tab="tab-1", className="card-tabs")
            ], className="bg-transparent border-bottom-0"),
            dbc.CardBody([
                html.Div(id="tab-content", style={"overflowX": "auto"})
            ])
        ], className="shadow-sm border-0 mb-4"),
    ]),
    
    dcc.Download(id="download-excel")
    
], style={"marginLeft": "300px", "padding": "2rem"})

app.layout = html.Div([sidebar, content])

stored_data = {}

@app.callback(
    [Output("download-excel", "data"),
     Output("tab-content", "children"),
     Output("kpi-row", "children"),
     Output("company-name", "children"),
     Output("company-meta", "children"),
     Output("status-alert-container", "children")],
    [Input("btn-generate", "n_clicks"),
     Input("tabs", "active_tab")],
    [State("ticker-input", "value")],
    prevent_initial_call=True
)
def update_dashboard(n_clicks, active_tab, ticker):
    ctx = callback_context
    trigger = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # Tab switch without new input
    if trigger == 'tabs' and ticker and 'df' in stored_data:
        content = build_tab_content(active_tab, stored_data['df'], stored_data['meta'])
        return dash.no_update, content, dash.no_update, dash.no_update, dash.no_update, dash.no_update
        
    if not ticker:
        return None, html.Div(), [], "Financial Dashboard", "Enter a ticker", []

    try:
        excel_file, df, meta = generate_excel_file(ticker.upper())
        stored_data['df'] = df
        stored_data['meta'] = meta
        
        if excel_file is None:
            alert = dbc.Alert([html.I(className="fas fa-exclamation-circle me-2"), meta], color="danger", dismissable=True)
            return None, html.Div(), [], "Error", "Failed", alert
        
        latest = df.iloc[-1]
        prev = df.iloc[-2] if len(df) > 1 else latest
        
        def fmt_money(x): 
            return f"${x/1e9:.1f}B" if x > 1e9 else f"${x/1e6:.0f}M"
        
        rev_growth = (latest['Revenue'] - prev['Revenue']) / prev['Revenue'] if prev['Revenue'] else 0
        net_margin = latest['Net Income'] / latest['Revenue'] if latest['Revenue'] else 0
        d2e = latest['Debt'] / latest['Total Equity'] if latest['Total Equity'] else 0
        
        kpis = [
            dbc.Col(kpi_card("Revenue", fmt_money(latest['Revenue']), f"{rev_growth:+.1%} YoY", "fa-coins", "#2F5597"), width=3),
            dbc.Col(kpi_card("Net Income", fmt_money(latest['Net Income']), f"{net_margin:.1%} margin", "fa-chart-pie", "#28a745"), width=3),
            dbc.Col(kpi_card("Cash", fmt_money(latest['Cash']), "On hand", "fa-wallet", "#17a2b8"), width=3),
            dbc.Col(kpi_card("Debt", fmt_money(latest['Debt']), f"{d2e:.2f}x D/E", "fa-file-invoice-dollar", "#dc3545"), width=3),
        ]
        
        content = build_tab_content(active_tab, df, meta)
        
        download = dash.no_update
        if trigger == 'btn-generate':
            download = dcc.send_bytes(excel_file.read(), f"{ticker.upper()}_Model.xlsx")

        return download, content, kpis, f"{meta['name']} ({ticker.upper()})", f"{meta['sector']} | {meta['industry']}", []

    except Exception as e:
        alert = dbc.Alert([html.I(className="fas fa-bug me-2"), str(e)], color="danger", dismissable=True)
        return None, html.Div(), [], "Error", "Processing failed", alert

def build_tab_content(active_tab, df, meta):
    if active_tab == "tab-1":
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df.index.strftime('%Y'), y=df['Revenue'], name='Revenue',
            marker_color='#2F5597', opacity=0.8
        ))
        fig.add_trace(go.Scatter(
            x=df.index.strftime('%Y'), y=df['Net Income'], name='Net Income',
            mode='lines+markers', line=dict(color='#FFC000', width=3), yaxis='y2'
        ))
        fig.update_layout(
            yaxis=dict(title="Revenue", showgrid=False),
            yaxis2=dict(title="Net Income", overlaying='y', side='right', showgrid=False),
            template="plotly_white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=40, r=40, t=40, b=40),
            hovermode="x unified"
        )
        return dcc.Graph(figure=fig, config={'displayModeBar': False}, style={"height": "450px"})
        
    elif active_tab == "tab-2":
        fig = go.Figure()
        gross_margin = (df['Revenue'] - df['COGS']) / df['Revenue']
        ebit_margin = (df['Revenue'] - df['COGS'] - df['SG&A'] - df['D&A']) / df['Revenue']
        net_margin = df['Net Income'] / df['Revenue']
        
        fig.add_trace(go.Scatter(x=df.index.strftime('%Y'), y=gross_margin, name='Gross', line=dict(color='#28a745', width=3)))
        fig.add_trace(go.Scatter(x=df.index.strftime('%Y'), y=ebit_margin, name='EBIT', line=dict(color='#2F5597', width=3)))
        fig.add_trace(go.Scatter(x=df.index.strftime('%Y'), y=net_margin, name='Net', line=dict(color='#17a2b8', width=3, dash='dot')))
        fig.update_layout(
            yaxis=dict(tickformat='.1%', title="Margin"),
            template="plotly_white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=40, r=40, t=40, b=40),
            hovermode="x unified"
        )
        return dcc.Graph(figure=fig, config={'displayModeBar': False}, style={"height": "450px"})

    elif active_tab == "tab-3":
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df.index.strftime('%Y'), y=df['Operating Cash Flow'], name='OCF', marker_color='#28a745'))
        fig.add_trace(go.Bar(x=df.index.strftime('%Y'), y=df['Capex'], name='Capex', marker_color='#dc3545'))
        fcf = df['Operating Cash Flow'] + df['Capex']
        fig.add_trace(go.Scatter(x=df.index.strftime('%Y'), y=fcf, name='FCF', line=dict(color='#2F5597', width=3, dash='dash')))
        fig.update_layout(
            template="plotly_white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=40, r=40, t=40, b=40),
            hovermode="x unified"
        )
        return dcc.Graph(figure=fig, config={'displayModeBar': False}, style={"height": "450px"})
    
    elif active_tab == "tab-4":
        # Classic model view - formatted table
        table_rows = []
        
        # Income Statement
        table_rows.append(html.Tr([
            html.Td("INCOME STATEMENT", colSpan=len(df)+1, style={"fontWeight": "bold", "backgroundColor": "#2F5597", "color": "white", "padding": "10px"})
        ]))
        
        is_items = ["Revenue", "COGS", "Gross Profit", "SG&A", "EBITDA", "D&A", "EBIT", "Interest", "Net Income"]
        for item in is_items:
            if item in df.columns:
                row_vals = [html.Td(item, style={"fontWeight": "bold", "padding": "8px", "borderBottom": "1px solid #ddd"})]
                for val in df[item]:
                    row_vals.append(html.Td(f"{val:,.0f}", style={"textAlign": "right", "padding": "8px", "borderBottom": "1px solid #ddd", "fontFamily": "monospace"}))
                table_rows.append(html.Tr(row_vals))
        
        # Balance Sheet
        table_rows.append(html.Tr([
            html.Td("BALANCE SHEET", colSpan=len(df)+1, style={"fontWeight": "bold", "backgroundColor": "#2F5597", "color": "white", "padding": "10px", "marginTop": "20px"})
        ]))
        
        bs_items = ["Cash", "AR", "PP&E", "Total Assets", "AP", "Debt", "Total Liab", "Total Equity"]
        for item in bs_items:
            if item in df.columns:
                row_vals = [html.Td(item, style={"fontWeight": "bold", "padding": "8px", "borderBottom": "1px solid #ddd"})]
                for val in df[item]:
                    row_vals.append(html.Td(f"{val:,.0f}", style={"textAlign": "right", "padding": "8px", "borderBottom": "1px solid #ddd", "fontFamily": "monospace"}))
                table_rows.append(html.Tr(row_vals))
        
        # Header row with years
        header = [html.Tr([
            html.Th("", style={"padding": "8px", "fontWeight": "bold", "backgroundColor": "#f5f5f5"})
        ] + [
            html.Th(yr, style={"padding": "8px", "fontWeight": "bold", "backgroundColor": "#f5f5f5", "textAlign": "center"})
            for yr in df.index.strftime('%Y')
        ])]
        
        return html.Div([
            html.Table(
                header + table_rows,
                style={
                    "borderCollapse": "collapse",
                    "width": "100%",
                    "fontSize": "14px",
                    "fontFamily": "Arial, sans-serif"
                }
            )
        ], style={"overflowX": "auto"})
    
    return html.Div()

if __name__ == "__main__":
    app.run(debug=True)