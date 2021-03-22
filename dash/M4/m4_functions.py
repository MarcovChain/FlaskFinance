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
                        'total payments': round(mt.loc[mt['type'] == 'payment', 'principal'].sum(), 2),  
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
    col_names =  ['ticker', 'buy_date', 'shares', 'buy_price', 'current_price',
                    'book_value', 'current_value', 'total_gain', 'capital_gain', 'div_gain',  
                    'capital_return', 'total_return', 'daily_return']
    st_summary = pd.DataFrame(columns = col_names)

    for ticker in tickers:
        # get current data from Yahoo
        quote = si.get_data(ticker)
        current_date = quote.last('1D').index[0]
        current_price = round(quote.last('1D')['close'][0], 2)
        
        # book value calculations
        book = st.loc[np.where((st['ticker'] == ticker) & (st['type'] == "buy"))]
        book['current_date'] = current_date
        book['current_price'] = current_price
        book['days_held'] = book['current_date'] - book['date']
        book['years_held'] = round(book['days_held'] / np.timedelta64(1, 'Y'), 2)
        book['current_value'] = book['current_price'] * book['number']
        book['gain'] = (book['current_value'] - book['total'])

        # scalar book results
        book_value = round(book['total'].sum(), 2)
        buy_date = book['date'].iloc[0].date()
        buy_price = book['price'].min()
        years_held = book['years_held'].max()
        days_held = book['days_held'].max() / np.timedelta64(1, 'D')
        
        # dividend value calculations
        div = st.loc[np.where((st['ticker'] == ticker) & (st['type'] == "dividend"))]
        div['current_price'] = current_price
        div['gain'] = div['number'] * div['current_price'] + div['total']
        div_gain = round(div['gain'].sum(), 2)

        # calculate current value with dividend values
        current_value = round(book['current_value'].sum() + div_gain, 2)
        shares = book['number'].sum() + div['number'].sum()

        # return calculations
        total_gain = round(current_value - book_value, 2)
        capital_gain = round(total_gain - div_gain, 2)
        capital_return = round(capital_gain / book_value * 100, 2)
        total_return = round(total_gain / book_value * 100, 2) 
        daily_return = round(total_return / days_held * 100, 2)

        # add to results dataframe
        new_row = {'ticker' : ticker, 
                    'buy_date' : buy_date,
                    'buy_price' : buy_price,
                    'current_price': current_price,
                    #'current_date': current_date,
                    #'years_held' : years_held,
                    'shares': shares,
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
    return st, st_summary, tickers, current_date

# Cenvous share account

def csa_fetch():

    # suppress pandas error
    pd.set_option('mode.chained_assignment', None)

    csa = pd.read_csv(
    os.path.join(os.path.dirname(__file__), "../../data/csa.csv"))
    csa['date'] =  pd.to_datetime(csa['date'])

    # add hypothetical sell row at end of dataframe
    csa = csa.append(csa.iloc[ -1:,:])
    csa.iloc[ -1:,:]['type'] = 'sell'

    # calculate acb totals
    csa['sell'] = np.where(csa['type'] == 'sell', 1, 0)
    csa['cumsum'] = csa['sell'].cumsum()
    csa['total_acb']= csa.groupby(['cumsum'])['acb'].cumsum()
    csa['total_shares']= csa.groupby(['cumsum'])['shares'].cumsum()
    csa = csa.drop(['sell', 'cumsum'], axis=1)

    # calculate return per sell period
    csa['acb'] = round(csa['total_acb'].shift(1).where(csa['type'] == 'sell', csa['acb']), 2)
    csa['shares'] = round(csa['total_shares'].shift(1).where(csa['type'] == 'sell', csa['shares']), 2)
    csa['profit'] = round((csa.proceeds - csa.acb), 2)
    csa['return'] = round(csa.profit / csa.acb * 100, 2)
    csa = csa.drop(['total_acb', 'total_shares'], axis=1)

    # calculate hypothetical current return
    quote = si.get_data('CVE.TO')
    quote['date'] = quote.index
    csa.iloc[ -1:,:]['date'] = quote.iloc[ -1:,:]['date'][0]
    csa.iloc[ -1:,:]['price'] = round(quote.iloc[ -1:,:]['close'][0], 2)
    csa.iloc[ -1:,:]['proceeds'] = round(csa.iloc[ -1:,:]['shares'] * csa.iloc[ -1:,:]['price'], 2)
    csa.iloc[ -1:,:]['profit'] = (csa.iloc[ -1:,:]['proceeds'] - csa.iloc[ -1:,:]['acb'])
    csa['return'] = round(csa.profit / csa.acb * 100, 2)

    csa_sell = csa.query('type == "sell"')
    #csa_profit = round(csa_sell.profit.sum(), 2)
    #csa_shares = csa_sell.shares.sum()

    # get extra metrics
    csa_sell['acb/share'] = round(csa_sell['acb'] / csa_sell['shares'], 2)
    csa_sell['days'] = csa_sell['date'].diff()
    csa_sell['days'][54] = csa_sell['date'][54] - csa['date'][0]
    csa_sell['days'] = csa_sell['days'] / np.timedelta64(1,'D')
    csa_sell['daily-return'] = round(csa_sell['return'] / csa_sell['days'] * 100, 2)

# rearrange dataframe
    csa_sell= csa_sell[csa_sell.columns[[0,9, 1,8,2,3,4, 6, 7, 10]]]

    return csa, csa_sell

# Cenvous salary

def sal_fetch():

    sal = pd.read_csv(
    os.path.join(os.path.dirname(__file__), "../../data/salary.csv"))
    sal['date'] =  pd.to_datetime(sal['date'])

    return sal


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
        height=650,
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text'],
        ),
    else:
        df.update_layout(
        height=650,
        paper_bgcolor=colors['background'],
        font_color=colors['text'],
        ),
    return df

# table set up function for plotly
def table_setup (df, height = 350):
    table = dash_table.DataTable(
        data=df.to_dict('records'),
        columns=[{'id': c, 'name': c} for c in df.columns],
        #style_as_list_view=True,
        fixed_rows={'headers': True},
        style_table={'height': height},
        style_header={'backgroundColor': '#2fa4e7'},
        style_cell={
            'backgroundColor': colors['background'],
            'color': colors['text'],
            'font-family': "Arial"
        },
    )
    return table