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

#### Fetch mt from local CSV using pandas
mt = pd.read_csv(
    os.path.join(os.path.dirname(__file__), "../../data/mortgage.csv"),
    # index_col=0,
    parse_dates=True,
    date_parser=custom_date_parser,
)

# row-based metrics
# principal percentage and cumsum
mt['prin%'] = np.where(mt['type'] == 'payment', (mt['principal'] / (mt['principal'] + mt['interest'])*100), np.nan).round(2)
mt['prin_total'] = round(mt['principal'].cumsum(),2)

# interest percentage and cumsum
mt['int%'] =np.where(mt['type'] == 'payment', (mt['interest'] / (mt['principal'] + mt['interest'])* 100), np.nan).round(2) 
mt['int_total'] = round(mt['interest'].cumsum(),2)

# running balance
mt['balance'] = round(500000 - mt['prin_total'], 2)
mt['balance2'] = mt['balance'].map("{:,}".format)
mt["date"] = pd.to_datetime(mt["date"], format="%Y-%m-%d")
types = mt["type"].unique()

# total principal and extra payments
total_principal = mt.loc[mt['type'] == 'payment', 'principal'].sum()
total_extra = mt.loc[mt['type'] == 'extra', 'principal'].sum()

# summary dataframe
col_names =  ['total_principal', 'total_extra']
mt_summary = pd.DataFrame(columns = col_names)
mt_summary = pd.DataFrame({'total_principal': [total_principal],  
                      'total_extra': [total_extra],  
                      })
mt_summary['total_principal'] = total_principal

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
balance = px.scatter(mt, x="date", y="balance", color="type", size="principal")
interest = px.line(mt, x="date", y="int%", color="type")
#interest.add_trace(px.line(mt, x="date", y="prin%"))

# define background according to time of day
mytime = time.localtime()
if mytime.tm_hour < 9 or mytime.tm_hour > 20:
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
    data=mt.to_dict('records'),
    columns=[{'id': c, 'name': c} for c in mt.columns],
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

total = dash_table.DataTable(
    data=mt_summary.to_dict('records'),
    columns=[{'id': c, 'name': c} for c in mt_summary.columns],
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
        return (html.Div([
        html.H3(children='Summary stats'),

        total
        ]),  
    # New Div for all elements in the new 'row' of the page
    html.Div([
        html.H3(children='Data table'),

        table
        ]),  
    )

if __name__ == '__main__':
    app.run_server(debug=True)
