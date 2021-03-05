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


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

def custom_date_parser(date):
    return pd.datetime.strptime(date, "%Y-%m-%d") 

#### Fetch data 
mt, mt_summary = m4_functions.mt_fetch()
st, st_summary = m4_functions.st_fetch()

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

#### app layout ####

app.layout = html.Div(style={'backgroundColor': m4_functions.colors['background']}, children=[
    html.H3(
        children="Marc's Money-Making Machine",
        style={'textAlign': 'center','color': '#2fa4e7'}
    ),
    dcc.Tabs(id='tabs-example', value='tab-1', children=[
        dcc.Tab(label='Mortgage charts', value='tab-1', style=m4_parameters.tab_style, selected_style=m4_parameters.tab_selected_style),
        dcc.Tab(label='Mortgage table', value='tab-2', style=m4_parameters.tab_style, selected_style=m4_parameters.tab_selected_style),
        dcc.Tab(label='Stock table', value='tab-3', style=m4_parameters.tab_style, selected_style=m4_parameters.tab_selected_style),
        dcc.Tab(label='Stock charts', value='tab-4', style=m4_parameters.tab_style, selected_style=m4_parameters.tab_selected_style),
    ]),
    html.Div(id='tabs-example-content')
])

#### app callback ####

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

if __name__ == '__main__':
    app.run_server(debug=True)