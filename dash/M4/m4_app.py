# -*- coding: utf-8 -*-

# Dash code for mortgage & stock tabs
# (c) 2021 Marc Boulet

#### libraries ####
import os
import time
from numpy.core.arrayprint import format_float_positional
import pandas as pd
import numpy as np 

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import plotly.express as px
import plotly.graph_objects as go

import m4_functions
import m4_parameters 
import yahoo_fin.stock_info as si

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

#### Fetch data 
mt, mt_summary = m4_functions.mt_fetch()
st, st_summary, tickers, current_date = m4_functions.st_fetch()
csa, csa_sell = m4_functions.csa_fetch()
sal = m4_functions.sal_fetch()

#### graphical elements ####

# set up plots
mt_balance = px.scatter(mt, x="date", y="balance", color="type", size="principal")
mt_balance.update_traces(hovertemplate = 'Date: %{x}<br>Balance: %{y:$,.0f}<br>Principal: %{marker.size:$,.2f}')
mt_interest = px.scatter(mt, x="date", y=["prin_total", "int_total"])
mt_interest.update_layout(hovermode='x')
csa_graph = px.line(csa, x="date", y="price")
csa_graph.add_trace(go.Scatter(x=csa_sell.date, y=csa_sell.price, 
                                name = "sell price", mode="markers", marker_size = 9,
                                marker_color='rgba(200, 40, 0, .8)',
                                marker_line_width=1,
                                showlegend=False))
sal_graph = px.line(sal, x="date", y="amount", color="type")
sal_graph.add_trace(go.Scatter(x=sal.date, y=sal.amount, 
                                name = 'amount', mode="markers", marker_size = 12,
                                marker_line_width=3))
sal_graph.update_traces(hovertemplate = 'Date: %{x}<br>Amount: %{y:$,.0f}')

# adjust plots for time of day
mt_balance = m4_functions.time_of_day(mt_balance)
mt_interest = m4_functions.time_of_day(mt_interest)
csa_graph = m4_functions.time_of_day(csa_graph)
sal_graph = m4_functions.time_of_day(sal_graph)

# set up tables
mt_table = m4_functions.table_setup(mt, 1500)
mt_summary_table = m4_functions.table_setup(mt_summary, 100)
st_table = m4_functions.table_setup(st)
st_summary_table = m4_functions.table_setup(st_summary, 300)
csa_table = m4_functions.table_setup(csa)
csa_sell_table = m4_functions.table_setup(csa_sell)
sal_table = m4_functions.table_setup(sal, 1000)

## selection options for stock chart
form_card_group = dbc.Card(
    [
        dbc.FormGroup(
            [
                dbc.Label("Choose a Stock Symbol"),
                dcc.Dropdown(
                    id="stock-ticker-select",
                    options=[{"label": ticker, "value": ticker,}
                        for ticker in tickers
                    ],
                    multi=False, 
                    value=tickers[0],
                ),
            ]
        )])

#### app layout ####

app.layout = html.Div(style={'backgroundColor': m4_functions.colors['background']}, children=[
    html.H3(
        children="Marc's Money-Making Machine",
        style={'textAlign': 'center','color': '#2fa4e7'}
    ),
    dcc.Tabs(id='tabs-example', value='tab-1', children=[
        dcc.Tab(label='Investment data', value='tab-1', style=m4_parameters.tab_style, 
        selected_style=m4_parameters.tab_selected_style),
        dcc.Tab(label='Mortgage charts', value='tab-2', style=m4_parameters.tab_style, selected_style=m4_parameters.tab_selected_style),
        dcc.Tab(label='Mortgage table', value='tab-3', style=m4_parameters.tab_style, 
        selected_style=m4_parameters.tab_selected_style),
        dcc.Tab(label='CSA data', value='tab-4', style=m4_parameters.tab_style, selected_style=m4_parameters.tab_selected_style),
        dcc.Tab(label='Salary data', value='tab-5', style=m4_parameters.tab_style, selected_style=m4_parameters.tab_selected_style),
    ]),
    html.Div(id='tabs-example-content')
])

#### app callback ####

# tabs callback
@app.callback(Output('tabs-example-content', 'children'),
              Input('tabs-example', 'value'))

def render_content(tab):
    if tab == 'tab-1':
        return (html.Div([
        html.H3(children= 'Summary as of ' + str(current_date)[0:10],
        style={'textAlign': 'center','color': '#2fa4e7'}),
        html.Div(st_summary_table, style = {"padding": "1rem 1rem"}),
        html.H3(children='Stock history',
        style={'textAlign': 'center','color': '#2fa4e7'}),
        html.Div(form_card_group),
        dcc.Graph(id="stock-price-graph"),
        html.H3(children='Transactions', 
        style={'textAlign': 'center','color': '#2fa4e7'}),
        html.Div(st_table, style = {"padding": "1rem 1rem"}),
        ])),
  
    elif tab == 'tab-2':
        return (html.Div([
        html.H3(children='Summary stats',
        style={'textAlign': 'center','color': '#2fa4e7'}),
        html.Div(mt_summary_table, style = {"padding": "1rem 1rem"}),
        html.H3(children='Balance',
        style={'textAlign': 'center','color': '#2fa4e7'}),

        dcc.Graph(
            id='graph1',
            figure=mt_balance
        ),  
    ]),
    # New Div for all elements in the new 'row' of the page
    html.Div([
        html.H3(children='Principal & Interest',
        style={'textAlign': 'center','color': '#2fa4e7'}),
        dcc.Graph(
            id='graph2',
            figure=mt_interest
        ),  
    ]))

    elif tab == 'tab-3':
        return (html.Div([
        html.H3(children='Summary stats',
        style={'textAlign': 'center','color': '#2fa4e7'}),
        html.Div(mt_summary_table, style = {"padding": "1rem 1rem"}),
        ]),  
    # New Div for all elements in the new 'row' of the page
    html.Div([
        html.H3(children='Transactions',
        style={'textAlign': 'center','color': '#2fa4e7'}),
        html.Div(mt_table, style = {"padding": "1rem 1rem"}),
        ]),  
    )

    elif tab == 'tab-4':
        return (html.Div([
        html.H3(children='CSA history',
         style={'textAlign': 'center','color': '#2fa4e7'}),
        dcc.Graph(
            id='graph3',
            figure=csa_graph
        ), 
        html.H3(children='Summary stats',
        style={'textAlign': 'center','color': '#2fa4e7'}),
        html.Div(csa_sell_table, style = {"padding": "1rem 1rem"}),
        html.H3(children='Transactions', 
        style={'textAlign': 'center','color': '#2fa4e7'}),
        html.Div(csa_table, style = {"padding": "1rem 1rem"}),
        ]))

    elif tab == 'tab-5':
        return (html.Div([
        html.H3(children='Salary history',
         style={'textAlign': 'center','color': '#2fa4e7'}),
        dcc.Graph(
            id='graph3',
            figure=sal_graph
        ), 
        html.H3(children='Transactions', 
        style={'textAlign': 'center','color': '#2fa4e7'}),
        html.Div(sal_table, style = {"padding": "1rem 1rem"}),
        ]))

    

## stock chart callback
@app.callback(
    Output("stock-price-graph", "figure"),
    Input("stock-ticker-select", "value"),
)
# def update_price_figure(ticker):
#     fig = m4_functions.update_price_figure(ticker)
#     return fig

def update_price_figure(ticker):
    """Create a plot of stock prices
    Args:
        tickers: ticker symbols from the dropdown select
    Returns:
        a graph `figure` dict containing the specificed
        price data points per stock
    """

    quote = si.get_data(ticker)
    quote['date'] = quote.index
    quote.index.name = None
    quote['SMA_50'] = quote['close'].rolling(window=50).mean()
    quote['SMA_200'] = quote['close'].rolling(window=200).mean()

    # Marc's purchase date & cost 
    quote_date = st_summary.loc[st_summary['ticker'] == ticker]['buy_date'].iloc[0]
    quote_cost = float(st_summary.loc[st_summary['ticker'] == ticker]['buy_price'])

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=quote['date'], y=quote['close'],
                        mode='lines',
                        name='close',
                        line = dict(color='black', width=2)
                        ))
    fig.add_trace(go.Scatter(x=quote['date'], y=quote['SMA_50'],
                        mode='lines',
                        name='50-day SMA',
                        line = dict(color='LightSeaGreen', width=2)
                        ))
    fig.add_trace(go.Scatter(x=quote['date'], y=quote['SMA_200'],
                        mode='lines', 
                        name='200-day SMA',
                        line = dict(color='SeaGreen', width=2),

                        ))

    fig.add_shape(
            # Line Horizontal 
                type="line",
                x0=quote_date,
                y0=quote_cost,
                x1=quote['date'].max(),
                y1=quote_cost,
                line=dict(color="firebrick", width=2, dash = 'dot',
                ),
        )

    # update layout

    fig.update_layout(
        autosize=True,
        # width=800,
        height=650,
        legend_orientation="h",
        showlegend=False,
        hovermode="x unified"
        #plot_bgcolor=colors['background'],
        #plot_bgcolor='#f5f0eb'
        )

    # render slider
    fig.update_xaxes(
        range=[quote_date, quote['date'].max()],
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=6, label="6m", step="month", stepmode="backward"),
                dict(count=1, label="YTD", step="year", stepmode="todate"),
                dict(count=1, label="1y", step="year", stepmode="backward"),
                dict(count=2, label="2y", step="year", stepmode="backward"),
                dict(count=5, label="5y", step="year", stepmode="backward"),
                dict(step="all")
            ])
        )
    )

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)