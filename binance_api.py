import requests        
import json           
import pandas as pd    
import numpy as np   
import matplotlib.pyplot as plt    
import datetime as dt 
import time
from numpy import dtype
import os
from binance.client import Client


def _get_historical_data_(symbol, interval , limit):
   while True:
      root_url = "https://fapi.binance.com/fapi/v1/klines"
      url = root_url + '?symbol=' + symbol + '&interval=' + interval + '&limit=' + limit
      data = json.loads(requests.get(url).text)
      global df1
      pd.set_option('display.max_columns',None)
      df1 = pd.DataFrame(data)
      df1.columns = ['open_time',
                     'Open', 'High', 'Low', 'Close', 'Volume',
                     'close_time', 'qav', 'num_trades',
                     'taker_base_vol', 'taker_quote_vol', 'ignore']
                     
      df1['Open'] = df1['Open'].astype(float)
      df1['Close'] = df1['Close'].astype(float)
      df1['High'] = df1['High'].astype(float)
      df1['Low'] = df1['Low'].astype(float)
      df1['Volume'] = df1['Volume'].astype(float)
         
      df1.index = [dt.datetime.fromtimestamp(x/1000.0) for x in df1.close_time]
      return df1
      


_get_historical_data_('SOLUSDT', '5m', '1000')
df = df1



