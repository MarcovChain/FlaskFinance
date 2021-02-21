# -*- coding: utf-8 -*-
import os

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import numpy as np

MIN_DATE = pd.Timestamp(2015, 12, 1, 0).date()
MAX_DATE = pd.Timestamp(2021, 2, 28, 0).date()

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
ww['prin_total'] = ww['principal'].cumsum()

# interest percentage and cumsum
ww['int%'] =np.where(ww['type'] == 'payment', ww['interest'] / (ww['principal'] + ww['interest']), np.nan).round(4)
ww['int_total'] = ww['interest'].cumsum()

# running balance
ww['balance'] = 500000 - ww['prin_total']

ww["date"] = pd.to_datetime(ww["date"], format="%Y-%m-%d")
types = ww["type"].unique()

# total principal and extra payments
total_principal = ww.loc[ww['type'] == 'payment', 'principal'].sum()
total_extra = ww.loc[ww['type'] == 'extra', 'principal'].sum()
total_principal, total_extra
####

# top nav bar
nav = dbc.Navbar(
    children=[
        dbc.Row(
            [
                dbc.Col(dbc.NavbarBrand("Marc's Money Making Machine (M4)", className="ml-2")),
            ],
            align="center",
            no_gutters=True,
        ),
    ],
    sticky="top",
)

# left side grouping of selction options
form_card_group = dbc.Card(
    [
        dbc.FormGroup(
            [
                dbc.Label("Choose a Stock Symbol"),
                dcc.Dropdown(
                    id="stock-type-select",
                    options=[
                        {
                            "label": type,
                            "value": type,
                        }
                        for type in types
                    ],
                    multi=True,
                    value=[types[0]],
                ),
            ]
        ),
        dbc.FormGroup(
            [
                dbc.Label("Price"),
                dbc.Col(
                    dbc.RadioItems(
                        id="stock-type-price",
                        options=[
                            {
                                "label": "Payment",
                                "value": "payment",
                            },
                            {
                                "label": "Extra",
                                "value": "extra",
                            },
                        ],
                        value="close",
                    ),
                    width=10,
                ),
            ]
        ),
        html.Div(
            [
                dcc.Markdown(
                    """
Selecting data in the **price** graph
will adjust the x-axis date range in the bottom **balance** graph.
"""
                ),
                html.Pre(id="selected-data"),
            ],
        ),
    ],
    body=True,
)

# sidebar
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": "50px",
    "left": 0,
    "bottom": 0,
    "width": "28rem",
    "padding": "2rem 1rem",
}

sidebar = html.Div(
    form_card_group,
    style=SIDEBAR_STYLE,
)

# price and balance graphs
graphs = [
    dbc.Alert(
        "📊 Hover over the charts to highlight data points and show graph utilities. "
        "All data is historical.",
        color="info",
    ),
    dcc.Graph(id="stock-price-graph", animate=True),
    dcc.Graph(
        id="stock-balance-graph",
        animate=True,
    ),
]


body_container = dbc.Container(
    [
        html.Div(
            children=[
                dbc.Row(
                    [
                        dbc.Col(
                            sidebar,
                            md=4,
                        ),
                        dbc.Col(
                            graphs,
                            md=8 ,
                        ),
                    ],
                ),
            ],
            className="m-4",
        ),
    ],
    fluid=True,
)

# main app ui entry
app.layout = html.Div([nav, body_container])


def filter_data_by_date(df, type, start_date, end_date):
    """Apply filter to the input dataframe

    Args:
        df: dateframe to filter
        type: stock type symbol for filter criteria
        start_date: min date threshold
        end_date: max date threshold
    Returns:
        a filtered dataframe by type and date range
    """
    if start_date is None:
        start_date = MIN_DATE

    if end_date is None:
        end_date = MAX_DATE

    filtered = df[
        (df["type"] == type) & (df["date"] >= start_date) & (df["date"] <= end_date)
    ]
    return filtered


def balance_figure_layout(selected_types, xaxis_range=None):
    """Add layout specific to x-axis

    Args:
        selected_types: stock types for title
        xaxis_range: `dict` with layout.xaxis.range config
    Returns:
        a layout dict
    """
    layout = dict(xaxis={}, yaxis={})
    layout["title"] = "Trading balance (%s)" % (" & ").join(selected_types)
    layout["yaxis"] = {"autorange": True}
    layout["yaxis"]["title"] = "balance"
    layout["xaxis"]["title"] = "Trading balance by Date"

    if xaxis_range:
        layout["xaxis"]["range"] = xaxis_range
        layout["xaxis"]["autorange"] = True

    return layout


@app.callback(
    Output("stock-price-graph", "figure"),
    [
        Input("stock-type-select", "value"),
        Input("stock-type-price", "value"),
    ],
)
def update_price_figure(types, price):
    """Create a plot of stock ww

    Args:
        types: type symbols from the dropdown select
        price: the radio button price selection
    Returns:
        a graph `figure` dict containing the specificed
        price data points per stock
    """

    return {
        "data": [
            {
                "x": [date for date in ww.loc[(ww.type == stock)]["date"]],
                "y": [p for p in ww.loc[(ww.type == stock)]["principal"]],
                "type": "scatter",
                "mode": "lines",
                "name": stock,
            }
            for stock in types
        ],
        "layout": {
            "title": "Stock Price - %s (%s)" % (price.title(), (" & ").join(types)),
            "xaxis": {"title": "Date"},
            "yaxis": {"title": "Price"},
        },
    }


@app.callback(
    Output("stock-balance-graph", "figure"),
    [
        Input("stock-type-select", "value"),
        Input("stock-price-graph", "relayoutData"),
    ],
)
def update_balance_figure(selected_types, relayoutData):
    """Create a plot of stock balance

    Args:
        selected_types: type symbols from the dropdown select
        relayoutData: data emitted from a `selection` on the price graph
    Returns:
        a graph `figure` dict containing the specificed
        balance data points per stock within the relayoutData
        date range.
    """

    data = []
    from_date = None
    to_date = None

    if relayoutData:
        from_date = relayoutData.get("xaxis.range[0]", None)
        to_date = relayoutData.get("xaxis.range[1]", None)

        if from_date and to_date:
            from_date = pd.Timestamp(from_date)
            to_date = pd.Timestamp(to_date)

            for stock in selected_types:
                filtered = filter_data_by_date(ww, stock, from_date, to_date)
                data.append(
                    {
                        "x": filtered["date"],
                        "y": filtered["balance"],
                        "type": "bar",
                        "name": stock,
                    }
                )

            xaxis_range = [from_date, to_date]

            return {
                "data": data,
                "layout": balance_figure_layout(selected_types, xaxis_range),
            }

        else:
            data = [
                {
                    "x": [item for item in ww[(ww.type == stock)]["date"]],
                    "y": [item for item in ww[(ww.type == stock)]["balance"]],
                    "type": "bar",
                    "name": stock,
                }
                for stock in selected_types
            ]

            # default dates
            xaxis_range = [MIN_DATE, MAX_DATE]

            return {
                "data": data,
                "layout": balance_figure_layout(selected_types, xaxis_range),
            }

    return {"data": data, "layout": balance_figure_layout(selected_types)}


if __name__ == "__main__":
    app.run_server(debug=True)
