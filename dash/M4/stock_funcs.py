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

# stocks dataframe 

def custom_date_parser(date):
    return pd.datetime.strptime(date, "%Y-%m-%d") 

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

