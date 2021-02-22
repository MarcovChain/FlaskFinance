# -*- coding: utf-8 -*-

# Dash code for mortgage tabs
# (c) 2021 Marc Boulet

# libraries
import os
import time
import pandas as pd
import numpy as np 

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import plotly.express as px
import plotly.graph_objects as go

import mortgage_funcs # source file for mortgage functions

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

def custom_date_parser(date):
    return pd.datetime.strptime(date, "%Y-%m-%d") 

#### Fetch mortgage data csv file
df = pd.read_csv(
    os.path.join(os.path.dirname(__file__), "../../data/mortgage.csv"),
    parse_dates=True,
    date_parser=custom_date_parser,
)

mt, mt_summary = mortgage_funcs.mt_transformation(df)

##### graphical elements

### time of day style
mytime = time.localtime()
if mytime.tm_hour < 9 or mytime.tm_hour > 19:
    # night
    colors = {
    'background': '#111111',
    'text': '#ffffe5'
    }
else:
    # day
    colors = {
    'background': '#fdfcfa',
    'text': '#000000'
    }

# set up plots
mt_balance = px.scatter(mt, x="date", y="balance", color="type", size="principal")
mt_interest = px.line(mt, x="date", y="int%", color="type")
#mt_interest.add_trace(px.line(mt, x="date", y="prin%"))

# adjust plots for time of day
mt_balance = mortgage_funcs.time_of_day(mt_balance)
mt_interest = mortgage_funcs.time_of_day(mt_interest)

# set up tables
mt_table = mortgage_funcs.table_setup(mt)
mt_summary_table = mortgage_funcs.table_setup(mt_summary)

# tab styles
tabs_styles = {
    'height': '44px'
}
tab_style = {
    'borderBottom': '1px solid #d6d6d6',
    'padding': '6px',
    'fontWeight': 'bold'
}

tab_selected_style = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': '#CCCCCC',
    'color': 'white',
    'padding': '6px'
}

#### app layout

app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.H3(
        children="Marc's Money-Making Machine",
        style={
            'textAlign': 'center'
            #'color': colors['text']
        }
    ),
    dcc.Tabs(id='tabs-example', value='tab-1', children=[
        dcc.Tab(label='Mortgage plots', value='tab-1', style=tab_style, selected_style=tab_selected_style),
        dcc.Tab(label='Mortgage table', value='tab-2', style=tab_style, selected_style=tab_selected_style),
    ]),
    html.Div(id='tabs-example-content')
])

#### app callback ####

@app.callback(Output('tabs-example-content', 'children'),
              Input('tabs-example', 'value'))
def render_content(tab):
    if tab == 'tab-1':
        return (html.Div([
        html.H3(children='Payment plot',
        style={'textAlign': 'center'}),

        dcc.Graph(
            id='graph1',
            figure=mt_balance
        ),  
    ]),
    # New Div for all elements in the new 'row' of the page
    html.Div([
        html.H3(children='Interest plot',
        style={'textAlign': 'center'}),

        dcc.Graph(
            id='graph2',
            figure=mt_interest
        ),  
    ]))

    elif tab == 'tab-2':
        return (html.Div([
        html.H3(children='Summary stats',
        style={'textAlign': 'center'}),
        mt_summary_table
        ]),  
    # New Div for all elements in the new 'row' of the page
    html.Div([
        html.H3(children='Transactions',
        style={'textAlign': 'center'}),
        mt_table
        ]),  
    )

if __name__ == '__main__':
    app.run_server(debug=True)