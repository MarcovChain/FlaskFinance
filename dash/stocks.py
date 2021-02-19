from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators
from matplotlib.pyplot import figure
import matplotlib.pyplot as plt

# Your key here
key = 'A0YD8RR1JNNH5Z1G'
# Chose your output format, or default to JSON (python dict)
ts = TimeSeries(key, output_format='pandas', indexing_type='date')
ti = TechIndicators(key, output_format='pandas', indexing_type='date')

# Get the data, returns a tuple
# aapl_data is a pandas dataframe, aapl_meta_data is a dict
aapl_data, aapl_meta_data = ts.get_daily(symbol='AAPL', outputsize='compact')
# aapl_sma is a dict, aapl_meta_sma also a dict
aapl_sma, aapl_meta_sma = ti.get_sma(symbol='AAPL')

aapl_data['date'] = aapl_data.index
aapl_data.index.name = None
#aapl_data

aapl_sma_50, aapl_meta_sma_50 = ti.get_sma(symbol='AAPL', time_period=50)
#aapl_sma_50.rename({'SMA':'SMA_50'}, axis='columns')
aapl_sma_50['SMA_50']=aapl_sma_50['SMA']
aapl_sma_50.drop(['SMA'], axis=1, inplace = True)
#aapl_sma_50

aapl_sma_200, aapl_meta_sma_200 = ti.get_sma(symbol='AAPL', time_period=200)
aapl_sma_200['SMA_200']=aapl_sma_200['SMA']
aapl_sma_200.drop(['SMA'], axis=1, inplace = True)
#aapl_sma_200

aapl = aapl_data.merge(aapl_sma_50, left_on='date', right_on='date')
aapl = aapl.merge(aapl_sma_200, left_on='date', right_on='date')
#aapl

# Marc's AAPL cost
aapl_cost = 260
aapl_date = '2020-03-30'

# Using plotly.express
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Create traces
fig = go.Figure()
fig.add_trace(go.Scatter(x=aapl['date'], y=aapl['4. close'],
                    mode='lines',
                    name='close',
                    line = dict(color='blue', width=2)))
fig.add_trace(go.Scatter(x=aapl['date'], y=aapl['SMA_50'],
                    mode='lines',
                    name='50-day SMA',
                    line = dict(color='LightSeaGreen', width=2)))
fig.add_trace(go.Scatter(x=aapl['date'], y=aapl['SMA_200'],
                    mode='lines', 
                    name='200-day SMA',
                    line = dict(color='LightSeaGreen', width=2)))

fig.add_shape(
        # Line Horizontal
            type="line",
            x0='2020-03-30',
            y0=aapl_cost,
            x1='2020-04-28',
            y1=aapl_cost,
            line=dict(color="firebrick", width=2,
            ),
    )

# update layout
fig.update_layout(
    autosize=True,
    # width=800,
    height=600,
    legend_orientation="h",
    showlegend=False,
    # plot_bgcolor='#f4f1f9'
    plot_bgcolor='#f5f0eb'
)

# render slider
fig.update_xaxes(
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

import plotly.graph_objects as go

import dash
import dash_core_components as dcc
import dash_html_components as html

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H1(children="Marc's Money Making Machine"),

    html.Div(children='''
        Dash: A web application framework for Python.
    '''),
    dcc.Graph(figure=fig)
])

app.run_server(debug=True)