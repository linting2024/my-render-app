import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import dash_bootstrap_components as dbc

import streamlit as st

st.title("微型保險財務敏感度分析")
st.write("歡迎使用 Streamlit 應用程式！")

# 初始化 Dash 應用，使用 Bootstrap 主題
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# 定義初始參數
INITIAL_YEAR = 10
INITIAL_INSURED = 10000
INITIAL_PREMIUM = 200  # 每人每月
INITIAL_INSURANCE_LIABILITY_RATIO = 0.7  # 70%
INITIAL_OPERATING_EXPENSE_RATIO = 0.1  # 10%
INITIAL_GROWTH_RATE = 0.10  # 10%

# 定義風險因子選項
insurance_liability_options = [
    {'label': '60%', 'value': 0.6},
    {'label': '65%', 'value': 0.65},
    {'label': '70%', 'value': 0.7},
    {'label': '75%', 'value': 0.75},
    {'label': '80%', 'value': 0.8},
]

operating_expense_options = [
    {'label': '10%', 'value': 0.10},
    {'label': '12.5%', 'value': 0.125},
    {'label': '15%', 'value': 0.15},
    {'label': '17.5%', 'value': 0.175},
    {'label': '20%', 'value': 0.20},
]

growth_rate_options = [
    {'label': '5%', 'value': 0.05},
    {'label': '7.5%', 'value': 0.075},
    {'label': '10%', 'value': 0.10},
    {'label': '12.5%', 'value': 0.125},
    {'label': '15%', 'value': 0.15},
]

premium_options = [
    {'label': '$180', 'value': 180},
    {'label': '$190', 'value': 190},
    {'label': '$200', 'value': 200},
    {'label': '$210', 'value': 210},
    {'label': '$220', 'value': 220},
]

# 定義應用的佈局
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("微型保險財務敏感度分析 Dashboard"), width=12)
    ], className="mb-4"),

    dbc.Row([
        dbc.Col([
            html.Label("保險負債比例"),
            dcc.Dropdown(
                id='insurance-liability-dropdown',
                options=insurance_liability_options,
                value=INITIAL_INSURANCE_LIABILITY_RATIO,
                clearable=False
            ),
        ], width=3),

        dbc.Col([
            html.Label("營業費用比例"),
            dcc.Dropdown(
                id='operating-expense-dropdown',
                options=operating_expense_options,
                value=INITIAL_OPERATING_EXPENSE_RATIO,
                clearable=False
            ),
        ], width=3),

        dbc.Col([
            html.Label("承保人數成長率"),
            dcc.Dropdown(
                id='growth-rate-dropdown',
                options=growth_rate_options,
                value=INITIAL_GROWTH_RATE,
                clearable=False
            ),
        ], width=3),

        dbc.Col([
            html.Label("保費設定 ($/人/月)"),
            dcc.Dropdown(
                id='premium-dropdown',
                options=premium_options,
                value=INITIAL_PREMIUM,
                clearable=False
            ),
        ], width=3),
    ], className="mb-4"),

    dbc.Row([
        dbc.Col([
            dcc.Graph(id='net-income-graph')
        ], width=6),

        dbc.Col([
            dcc.Graph(id='net-profit-rate-graph')
        ], width=6),
    ], className="mb-4"),

    dbc.Row([
        dbc.Col([
            dcc.Graph(id='insured-people-graph')
        ], width=12),
    ], className="mb-4"),

    dbc.Row([
        dbc.Col([
            html.H4("風險因子概覽"),
            html.Ul([
                html.Li("保險負債比例：資產價值在保險收入中的比例。"),
                html.Li("營業費用比例：保險收入中用於營運的比例。"),
                html.Li("承保人數成長率：每年承保人數的增長速度。"),
                html.Li("保費設定：每位客戶每月繳納的保費金額。"),
            ])
        ], width=12)
    ])
], fluid=True)

# 定義回調函數來更新圖表
@app.callback(
    [Output('net-income-graph', 'figure'),
     Output('net-profit-rate-graph', 'figure'),
     Output('insured-people-graph', 'figure')],
    [Input('insurance-liability-dropdown', 'value'),
     Input('operating-expense-dropdown', 'value'),
     Input('growth-rate-dropdown', 'value'),
     Input('premium-dropdown', 'value')]
)
def update_graphs(insurance_liability_ratio, operating_expense_ratio, growth_rate, premium):
    years = list(range(1, INITIAL_YEAR + 1))
    net_income = []
    net_profit_rate = []
    insured_people = []

    current_insured = INITIAL_INSURED
    for year in years:
        # 計算保費收入
        annual_premium_income = current_insured * premium * 12

        # 第1~3年的營業費用比例為15%
        if year <= 3:
            current_operating_expense_ratio = 0.25
        else:
            current_operating_expense_ratio = operating_expense_ratio

        # 計算保險負債和營業費用
        insurance_liabilities = annual_premium_income * insurance_liability_ratio
        operating_expenses = annual_premium_income * current_operating_expense_ratio

        # 計算淨收入
        net_inc = annual_premium_income - (insurance_liabilities + operating_expenses)
        net_income.append(net_inc)

        # 計算淨利潤率
        net_profit = (net_inc / annual_premium_income) * 100
        net_profit_rate.append(net_profit)

        # 計算下一年的承保人數
        current_insured = current_insured * (1 + growth_rate)
        insured_people.append(current_insured)

    # 準備淨收入圖表
    net_income_fig = go.Figure(
        data=[
            go.Bar(
                x=years,
                y=net_income,
                name='淨收入 (TWD)',
                marker_color='indianred'
            )
        ],
        layout=go.Layout(
            title='淨收入隨年份變化',
            xaxis_title='年份',
            yaxis_title='淨收入 (TWD)',
            template='plotly_white'
        )
    )

    # 準備淨利潤率圖表
    net_profit_rate_fig = go.Figure(
        data=[
            go.Scatter(
                x=years,
                y=net_profit_rate,
                mode='lines+markers',
                name='淨利潤率 (%)',
                line=dict(color='green')
            )
        ],
        layout=go.Layout(
            title='淨利潤率隨年份變化',
            xaxis_title='年份',
            yaxis_title='淨利潤率 (%)',
            template='plotly_white'
        )
    )

    # 準備承保人數圖表
    insured_people_fig = go.Figure(
        data=[
            go.Scatter(
                x=years,
                y=insured_people,
                mode='lines+markers',
                name='承保人數',
                line=dict(color='blue')
            )
        ],
        layout=go.Layout(
            title='承保人數隨年份變化',
            xaxis_title='年份',
            yaxis_title='承保人數',
            template='plotly_white'
        )
    )

    return net_income_fig, net_profit_rate_fig, insured_people_fig

# 運行應用
if __name__ == '__main__':
    app.run_server(debug=True)
