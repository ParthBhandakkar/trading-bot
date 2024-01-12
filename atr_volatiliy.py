from pandas.core.frame import DataFrame
import yfinance as yf
from yahoo_fin import stock_info as si
import pandas as pd
import numpy as np
import openpyxl
from datetime import datetime
import matplotlib.pyplot as plt

stock_list = ["RELIANCE", "UPL", "ICICIBANK", "HDFCBANK"]
stock = "RELIANCE" + ".NS"
price = si.get_live_price(stock)
df = yf.download(tickers=stock, period="30d", interval ="5m").reset_index(drop=True)

def _atr_():
    while True:
        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - df['Close'].shift())
        low_close = np.abs(df['Low'] - df['Close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        df['atr'] = true_range.rolling(14).mean()
        
        atr_list = df['atr'].tolist()
        last_value = atr_list[-1]
        if last_value>30 and last_value<60:
            print('RSI -> buy')
            break
        elif last_value >60:
            print('RSI -> sell')
            break