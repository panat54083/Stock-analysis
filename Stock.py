import numpy as np
import pandas as pd
import yfinance as yf
import plotly.graph_objs as go
from datetime import date, timedelta

class stock_data(): #  Class สำหรับดึงข้อมูล ของ Stock

    def __init__(self):
        pass
    
    def get_data(self, name, start_time = None, end_time = None): # get data of stock
        data = yf.download(tickers= name, start=start_time, end=end_time)
        return data
    
    def get_data_all(self, name, start_time = None, end_time = None): # get data and remove whitespace by add prev. data
        data = yf.download(tickers= name, start=start_time, end=end_time)
        list_d = data.index # get index
        date_set = set(list_d[0] + timedelta(x) for x in range((list_d[-1] - list_d[0]).days)) # get set of date
        missing = sorted(date_set - set(list_d)) # find missing date
        list_date = []
        # print(missing)
        for miss in missing: # prev missing data = current missing data
            prev = miss - pd.DateOffset(1)
            list_date.append(miss)
            data.loc[miss] = data.loc[prev]
        print(list_date)
        data = data.sort_index()    # sort data  
        return data


if __name__ == '__main__':

    sc = stock_data()
    df = sc.get_data('DOD.BK','2021-03-10','2021-03-19')
    df_new = sc.get_data_all('DOD.BK','2021-03-10','2021-03-19')
    print(type(df))
    print('---------------------')
    print(type(df_new))
