# -*- coding: utf-8 -*-
import os

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_table
import plotly.express as px
import pandas as pd
import numpy as np

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])


def custom_date_parser(date):
    return pd.datetime.strptime(date, "%Y-%m-%d") 


#### Fetch ww from local CSV using pandas
ww = pd.read_csv(
    os.path.join(os.path.dirname(__file__), "../../data/mortgage.csv"),
    # index_col=0,
    parse_dates=True,
    date_parser=custom_date_parser,
)

# row-based metrics
# principal percentage and cumsum
ww['prin%'] = np.where(ww['type'] == 'payment', ww['principal'] / (ww['principal'] + ww['interest']), np.nan).round(4)
ww['prin_total'] = round(ww['principal'].cumsum(),2)

# interest percentage and cumsum
ww['int%'] =np.where(ww['type'] == 'payment', ww['interest'] / (ww['principal'] + ww['interest']), np.nan).round(4)
ww['int_total'] = round(ww['interest'].cumsum(),2)

# running balance
ww['balance'] = round(500000 - ww['prin_total'], 2)

ww["date"] = pd.to_datetime(ww["date"], format="%Y-%m-%d")
types = ww["type"].unique()

# total principal and extra payments
total_principal = ww.loc[ww['type'] == 'payment', 'principal'].sum()
total_extra = ww.loc[ww['type'] == 'extra', 'principal'].sum()
####

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}


fig = px.scatter(ww, x="date", y="balance", color="type")

fig.update_layout(
    plot_bgcolor=colors['background'],
    paper_bgcolor=colors['background'],
    font_color=colors['text']
)

table = dash_table.DataTable(
    data=ww.to_dict('records'),
    columns=[{'id': c, 'name': c} for c in ww.columns],
    fixed_rows={'headers': True},
    style_as_list_view=True,
    style_header={'backgroundColor': 'rgb(30, 30, 30)'},
    style_cell={
        'backgroundColor': 'rgb(50, 50, 50)',
        'color': 'white',
        'font-family': "Arial"
    },
)

app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.H3(
        children="Mortgage Portal",
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),

    html.Div(children="Marc's Money-Making Machine", style={
        'textAlign': 'center',
        'color': colors['text']
    }),

    dcc.Graph(
        id='example-graph-2',
        figure=fig
    ),

    html.H4(children="Data table", style={
        'textAlign': 'center',
        'color': colors['text']
    }),

    table
])

if __name__ == '__main__':
    app.run_server(debug=True)
