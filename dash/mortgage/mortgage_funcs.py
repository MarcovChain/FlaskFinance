# helper functions for the mortgage tabs

# libraries
import os
import time
import pandas as pd
import numpy as np
import dash_table
import m4_parameters

# mortgage dataframe 

def custom_date_parser(date):
    return pd.datetime.strptime(date, "%Y-%m-%d") 

def mt_fetch():

    mt = pd.read_csv(
    os.path.join(os.path.dirname(__file__), "../../data/mortgage.csv"),
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
    mt['balance'] = round(m4_parameters.mt_balance - mt['prin_total'], 2)
    mt['balance2'] = mt['balance'].map("{:,}".format)

    # summary dataframe
    col_names =  ['total payments', 'total extra', 'total principal',
                  'principal %', 'total interest', 'interest %', 
                  'remaining balance']
    mt_summary = pd.DataFrame(columns = col_names)
    mt_summary = pd.DataFrame({
                        'total payments': mt.loc[mt['type'] == 'payment', 'principal'].sum(),  
                        'total extra': [mt.loc[mt['type'] == 'extra', 'principal'].sum()],
                        'total principal': mt['prin_total'].max(),
                        'principal %': mt['prin%'].max(),
                        'total interest': mt['int_total'].max(),
                        'interest %': mt['int%'].min(), 
                        'remaining balance': mt['balance'].min(),
                        })

    #mt_summary = mt_summary.head().style.format("{:,.0f}")
    #mt_summary = mt_summary.style.format('{:,}')

    return mt, mt_summary

# update time of day style for plots

### time of day style
mytime = time.localtime()
if mytime.tm_hour < m4_parameters.morning or mytime.tm_hour > m4_parameters.night:
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

def time_of_day(df): 
    mytime = time.localtime()
    if mytime.tm_hour < m4_parameters.morning or mytime.tm_hour > m4_parameters.night:
        # night
        df.update_layout(
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text']
        )
    else:
        df.update_layout(
        paper_bgcolor=colors['background'],
        font_color=colors['text']
        )
    return df

# table set up function for plotly
def table_setup (df):
    table = dash_table.DataTable(
        data=df.to_dict('records'),
        columns=[{'id': c, 'name': c} for c in df.columns],
        style_as_list_view=True,
        fixed_rows={'headers': True},
        style_table={'height': 600},
        style_header={'backgroundColor': '#2fa4e7'},
        style_cell={
            'backgroundColor': colors['background'],
            'color': colors['text'],
            'font-family': "Arial"
        },
    )
    return table