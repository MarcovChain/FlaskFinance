# helper functions for the mortgage tabs

# libraries
import os
import time
import pandas as pd
import numpy as np
import dash_table
import m4_parameters
import yahoo_fin.stock_info as si
from datetime import datetime

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

# stock dataframe

def st_fetch():

    st = pd.read_csv(
    os.path.join(os.path.dirname(__file__), "../../data/stocks.csv"))
    st['date'] =  pd.to_datetime(st['date'])

    tickers = st['ticker'].unique()

    # results dataframe
    col_names =  ['ticker', 'buy_date', 'years_held' , 'book_value', 
                    'current_value', 'total_gain', 'capital_gain', 'div_gain',  
                    'capital_return', 'total_return', 'daily_return']
    st_summary = pd.DataFrame(columns = col_names)

    for ticker in tickers:
        # get current data from Yahoo
        quote = si.get_data(ticker)
        current_date = quote.last('1D').index[0]
        current_price = quote.last('1D')['close'][0]
        
        # book value calculations
        book = st.loc[np.where((st['ticker'] == ticker) & (st['type'] == "buy"))]
        book['current_date'] = current_date
        book['current_price'] = current_price
        book['days_held'] = book['current_date'] - book['date']
        book['years_held'] = round(book['days_held'] / np.timedelta64(1, 'Y'), 2)
        book['current_value'] = book['current_price'] * book['number']
        book['gain'] = (book['current_value'] - book['total'])
        # scalar book results
        current_value = round(book['current_value'].sum(), 2)
        book_value = round(book['total'].sum(), 2)
        buy_date = np.datetime_as_string(book['date'], unit='D')[0]
        years_held = book['years_held'].max()
        days_held = book['days_held'].max() / np.timedelta64(1, 'D')
        
        # dividend value calculations
        div = st.loc[np.where((st['ticker'] == ticker) & (st['type'] == "dividend"))]
        div['current_price'] = current_price
        div['gain'] = div['number'] * div['current_price'] + div['total']
        div_gain = round(div['gain'].sum(), 2)

        # return calculations
        total_value = round(current_value + div_gain, 2)
        total_gain = round(total_value - book_value, 2)
        capital_gain = round(current_value - book_value, 2)
        capital_return = round((current_value - book_value) / book_value * 100, 2)
        total_return = round((total_gain / book_value) * 100, 2) 
        daily_return = round(total_return / days_held * 100, 2)

        # if years_held >= 1:
        #     annual_return = round(((total_value/book_value)**(1/years_held) - 1) * 100, 2)
        # else:
        #     annual_return = None

        # add to results dataframe
        new_row = {'ticker' : ticker, 
                    'buy_date' : buy_date,
                    'years_held' : years_held,
                    'book_value' : book_value, 
                    'current_value' : current_value,
                    'total_gain' : total_gain,
                    'capital_gain' : capital_gain,
                    'div_gain' : div_gain,
                    'capital_return' : capital_return,
                    'total_return' : total_return,
                    'daily_return' : daily_return}

        st_summary = st_summary.append(new_row, ignore_index = True)

    st_summary = st_summary.sort_values(by = 'daily_return', ascending = False)
    return st, st_summary

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