import pandas as pd
import numpy as np
from tqdm.auto import tqdm
import os
import yfinance as yf
import time


def get_financials_data(ticker, freq='A'):
    income_url = f'https://stockrow.com/api/companies/{ticker}/financials.xlsx?dimension={freq}&section=Income%20Statement&sort=desc'
    balance_url = f'https://stockrow.com/api/companies/{ticker}/financials.xlsx?dimension={freq}&section=Balance%20Sheet&sort=desc'
    cash_url = f'https://stockrow.com/api/companies/{ticker}/financials.xlsx?dimension={freq}&section=Cash%20Flow&sort=desc'
    metrics_url = f'https://stockrow.com/api/companies/{ticker}/financials.xlsx?dimension={freq}&section=Metrics&sort=desc'
    growth_url = f'https://stockrow.com/api/companies/{ticker}/financials.xlsx?dimension={freq}&section=Growth&sort=desc'
    
    income_df = pd.read_excel(income_url)
    balance_df = pd.read_excel(balance_url)
    cash_df = pd.read_excel(cash_url)
    metrics_df = pd.read_excel(metrics_url)
    growth_df = pd.read_excel(growth_url)
    
    financial_df = pd.concat([income_df, balance_df, cash_df, metrics_df, growth_df], axis=0, ignore_index=True)
    financial_df = financial_df.set_index('Unnamed: 0')
    financial_df.index.name = 'Date'
    financial_df = financial_df.T
    financial_df.index = financial_df.index.to_series().apply(lambda x: x.date())
    financial_df = financial_df.sort_index()
    return financial_df


def parse_divs(ticker):
    '''
    To do:
    - "Date" to datetime
    - "Dividends" to float
    '''
    
    url = f'https://finance.yahoo.com/quote/{ticker}/history?period1=438220800&period2=1604793600&interval=div%7Csplit&filter=div&frequency=1d&includeAdjustedClose=true'
    div_df = pd.read_html(url)
    div_df = div_df[0][['Date', 'Dividends']].iloc[:-1]
    div_df.columns = ['Date', 'Dividends']
    return div_df


def parse_data(ticker, freq):
    print('Ticker:', ticker)
    # financial info
    print('Reading financial data...', end=' ')
    financial_df = get_financials_data(ticker, freq)
    financial_df['year'] = financial_df.index.to_series().apply(lambda x: x.year).astype(int)
    print('Ok')
    
    # price info
    print('Reading price data...', end=' ')
    prices = yf.download(ticker,'1950-01-01', '2020-12-31', progress=False)
    print('Ok')
    
    # div info
    print('Reading div data...', end=' ')
    div_df = parse_divs(ticker)
    div_df = div_df.set_index('Date')
    print('Ok')

    return financial_df, prices, div_df


def save_data(financial_df, prices, div_df, path, ticker):
    save_path = f'{path}/{ticker}'
    if not os.path.isdir(save_path):
        os.mkdir(save_path)
    financial_df.to_pickle(f'{save_path}/financials.pickle')
    prices.to_pickle(f'{save_path}/prices.pickle')
    div_df.to_pickle(f'{save_path}/divs.pickle')
    print('Everything is saved!')
    