# -*- coding: utf-8 -*-
import os
import time
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_table
import plotly.express as px
import plotly.graph_objects as go
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
ww['balance2'] = ww['balance'].map("{:,}".format)
ww["date"] = pd.to_datetime(ww["date"], format="%Y-%m-%d")
types = ww["type"].unique()

# total principal and extra payments
total_principal = ww.loc[ww['type'] == 'payment', 'principal'].sum()
total_extra = ww.loc[ww['type'] == 'extra', 'principal'].sum()

##### graphical elements

# tab style
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

# set up balance plot
balance = px.scatter(ww, x="date", y="balance", color="type", size="principal")
interest = px.line(ww, x="date", y="int%", color="type")
#interest.add_trace(px.line(ww, x="date", y="prin%"))

# define background according to time of day
mytime = time.localtime()
if mytime.tm_hour < 9 or mytime.tm_hour > 19:
    # night
    colors = {
    'background': '#111111',
    'text': '#ffffe5'
    }

    balance.update_layout(
    plot_bgcolor=colors['background'],
    paper_bgcolor=colors['background'],
    font_color=colors['text']
    )
    
else:
    # day
    colors = {
    'background': '#fdfcfa',
    'text': '#000000'
    }

    balance.update_layout(
    paper_bgcolor=colors['background'],
    font_color=colors['text']
    )

# set up table
table = dash_table.DataTable(
    data=ww.to_dict('records'),
    columns=[{'id': c, 'name': c} for c in ww.columns],
    style_as_list_view=True,
    fixed_rows={'headers': True},
    style_table={'height': 600},  # defaults to 500
    style_header={'backgroundColor': '#2fa4e7'},
    style_cell={
        'backgroundColor': colors['background'],
        'color': colors['text'],
        'font-family': "Arial"
    },
)

#### app layout

app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.H3(
        children="Marc's Money-Making Machine",
        style={
            'textAlign': 'center',
            'color': colors['text']
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
        html.H3(children='Payment plot'),

        dcc.Graph(
            id='graph1',
            figure=balance
        ),  
    ]),
    # New Div for all elements in the new 'row' of the page
    html.Div([
        html.H3(children='Interest plot'),

        dcc.Graph(
            id='graph2',
            figure=interest
        ),  
    ]))

        
    elif tab == 'tab-2':
        return table

if __name__ == '__main__':
    app.run_server(debug=True)
