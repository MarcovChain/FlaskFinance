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
st, st_summary, tickers = m4_functions.st_fetch()
st_graph = st_summary
st_summary = st_summary.drop(columns=['buy_date'])

#### graphical elements ####

# set up plots
mt_balance = px.scatter(mt, x="date", y="balance", color="type", size="principal")
mt_interest = px.scatter(mt, x="date", y=["prin_total", "int_total"])
mt_interest.update_layout(hovermode='x')

# adjust plots for time of day
mt_balance = m4_functions.time_of_day(mt_balance)
mt_interest = m4_functions.time_of_day(mt_interest)

# set up tables
mt_table = m4_functions.table_setup(mt)
mt_summary_table = m4_functions.table_setup(mt_summary)
st_table = m4_functions.table_setup(st)
st_summary_table = m4_functions.table_setup(st_summary)

## selection options for stock chart
form_card_group = dbc.Card(
    [
        dbc.FormGroup(
            [
                dbc.Label("Choose a Stock Symbol"),
                dcc.Dropdown(
                    id="stock-ticker-select",
                    options=[
                        {
                            "label": ticker,
                            "value": ticker,
                        }
                        for ticker in tickers
                    ],
                    multi=False, 
                    value=tickers[0],
                ),
            ]
        )])

# sidebar
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": "50px",
    "left": 0,
    "bottom": 0,
    "width": "28rem",
    "padding": "2rem 1rem",
}


#### app layout ####

app.layout = html.Div(style={'backgroundColor': m4_functions.colors['background']}, children=[
    html.H3(
        children="Marc's Money-Making Machine",
        style={'textAlign': 'center','color': '#2fa4e7'}
    ),
    dcc.Tabs(id='tabs-example', value='tab-1', children=[
        dcc.Tab(label='Mortgage charts', value='tab-1', style=m4_parameters.tab_style, selected_style=m4_parameters.tab_selected_style),
        dcc.Tab(label='Mortgage table', value='tab-2', style=m4_parameters.tab_style, 
        selected_style=m4_parameters.tab_selected_style),
        dcc.Tab(label='Stock table', value='tab-3', style=m4_parameters.tab_style, 
        selected_style=m4_parameters.tab_selected_style),
        dcc.Tab(label='Stock charts', value='tab-4', style=m4_parameters.tab_style, 
        selected_style=m4_parameters.tab_selected_style),
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

    elif tab == 'tab-2':
        return (html.Div([
        html.H3(children='Summary stats',
        style={'textAlign': 'center','color': '#2fa4e7'}),
        mt_summary_table
        ]),  
    # New Div for all elements in the new 'row' of the page
    html.Div([
        html.H3(children='Transactions',
        style={'textAlign': 'center','color': '#2fa4e7'}),
        mt_table
        ]),  
    )

    elif tab == 'tab-3':
        return (html.Div([
        html.H3(children='Summary stats',
        style={'textAlign': 'center','color': '#2fa4e7'}),
        st_summary_table
        ]),  
    # New Div for all elements in the new 'row' of the page
    html.Div([
        html.H3(children='Transactions', 
        style={'textAlign': 'center','color': '#2fa4e7'}),
        st_table
        ]),  
    )

    if tab == 'tab-4':
        return (html.Div([
        html.H3(children='Stock history',
        style={'textAlign': 'center','color': '#2fa4e7'}),
        form_card_group,
        dcc.Graph(id="stock-price-graph"
                # figure = stock-price-graph
                ),
        html.H3(children='Summary stats',
        style={'textAlign': 'center','color': '#2fa4e7'}),
        st_summary_table
        ]))

## stock chart callback
@app.callback(
    Output("stock-price-graph", "figure"),
    Input("stock-ticker-select", "value"),
)

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
    quote_date = st_graph.loc[st_graph['ticker'] == ticker]['buy_date'].iloc[0]
    quote_cost = float(st_graph.loc[st_graph['ticker'] == ticker]['buy_price'])

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
        height=800,
        legend_orientation="h",
        showlegend=False,
        # plot_bgcolor='#f4f1f9'
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
    # fig.show()

if __name__ == '__main__':
    app.run_server(debug=True)