import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
import glob
from collections import defaultdict




def standartize_column(col):
    col = col.replace('(', ' ').replace(')', ' ').replace('&', ' ').replace('/', ' ').replace('.', ' ').replace(',', ' ').replace('-', ' ').lower().strip()
    col = '_'.join([i for i in col.split(' ') if i])
    return col


def cut_data(df, start_date, end_date):
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    df = df.loc[start_date:end_date]
    return df


def read_single_data(ticker, path_to_data, start_date, end_date, selected_cols):
    final_path = f'{path_to_data}/{ticker}/*'
    files = glob.glob(final_path)

    divs_path = [i for i in files if 'divs' in i][0]
    financials_path = [i for i in files if 'financials' in i][0]
    prices_path = [i for i in files if 'prices' in i][0]

    divs = pd.read_pickle(divs_path)
    financials = pd.read_pickle(financials_path) 
    prices = pd.read_pickle(prices_path)[['Adj Close']]
    
    financials = financials[selected_cols]
    financials.index = pd.to_datetime(financials.index)

    prices = cut_data(prices, start_date, end_date)
    financials = cut_data(financials, start_date, end_date)

    dataset = prices.merge(financials, left_index=True, right_index=True, how='left')  # FIXME: добавить ffill и маркер апдейта
    dataset.columns = [standartize_column(i) for i in dataset.columns]
    
    return dataset


def warmup(tickers, path_to_data, start_date, end_date, selected_cols):
    '''
    Считывает данные по указаным тикерам и формирует датасет
    -------------------------------
    Output example:
    {'2015-01-02': {'AMD':  {'adj_close':  2.67, 'eps_basic': 2},
                    'INTC': {'adj_close': 30.67, 'eps_basic': 3}
                    }}
    '''

    dfs = []
    for ticker in tickers:
        df = read_single_data(ticker, path_to_data, start_date, end_date, selected_cols)
        print(ticker, df.shape)
        df.index = df.index.to_series().apply(lambda x: str(x.date()))
        df = {key: {ticker: value} for key, value in df.to_dict('index').items()}
        dfs.append(df.copy())

    data_dict = defaultdict(dict)
    for df in dfs:
        for key, value in df.items():
            if key not in data_dict:
                data_dict[key] = {}
            data_dict[key].update(value)
    
    # FIXME: добавить проверку размерности датасетов
    return dict(data_dict)