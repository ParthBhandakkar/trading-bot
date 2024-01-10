import numpy as np
from numpy import NaN
import pandas as pd
import json
import requests
import datetime as dt
from binance.client import Client
import warnings
from datetime import datetime

warnings.filterwarnings('ignore')

client = Client("1e1c2bf69302d1f442b606d2bb4792d84f14eab2f8c37b4c96db99f7aa82ba3c",
                "0ba00fab8eeb44fcccb7d0612e176422c258069ec4756ae5b0e778c77c639f07", {"verify": False, "timeout": 20})

def _get_historical_data_(symbol, interval, limit):
    root_url = "https://fapi.binance.com/fapi/v1/klines"
    url = root_url + '?symbol=' + symbol + '&interval=' + interval + '&limit=' + limit
    data = json.loads(requests.get(url).text)
    # global df1
    pd.set_option('display.max_columns', None)
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

    df1.index = [dt.datetime.fromtimestamp(x / 1000.0) for x in df1.close_time]
    return df1
df_eth = _get_historical_data_('ETHUSDT', '15m', '500')

close = df_eth['Close'].to_list()
high = df_eth['High'].to_list()
low = df_eth['Low'].to_list()
open = df_eth['Open'].to_list()

def sma(source, length):
    sma_out = source.rolling(length).mean()
    return sma_out

def rma(source, length):
    alpha = 1 / length
    rma_out = [NaN, 0]
    for i in range(length-1):
        rma_out.append(sma(source, length) if rma_out[-2] == float('nan') else (alpha * source[i]) + ((1 - alpha) * (0 if rma_out[-1] == float('nan') else rma_out[-1])))
    return rma_out

def atr(length):
    trueRange = [NaN, 0]
    for i in range(length-1):
        trueRange.append(
            high[i] - low[i] if high[i - 1] == float('nan') else max(max(high[i] - low[i], abs(high[i] - close[i - 1])),
                                                                     abs(low[i] - close[i - 1])))
    return rma(trueRange, length)

def highest(source, length):
    return -2 + np.argmax(source[-(length + 1):])

def lowest(source, length):
    return -2 + np.argmin(source[-(length + 1):])


# df_eth['atr'] = 3.0 * atr(22)
# df_eth['longStop'] = (highest(close, 22)) - atr
# df_eth['shortStop'] = (lowest(close, 22)) + atr
dir = [1]
length = 22
mult = 3.0
showLabels = True
useClose = True
longStop = [NaN]
shortStop = [NaN]

while True:
    atr_val = mult * (atr(length)[-1])

    longStop.append((highest(close, length)) - atr_val)  #if useClose == True else highest(high, length)
    longStopPrev = longStop[-1] if longStop[-2] == NaN else longStop[-2]
    longStop = max(longStop, longStopPrev) if close[-2] > longStopPrev else longStop

    shortStop.append((lowest(close, length)) + atr_val)   # if useClose else lowest(low, length)
    shortStopPrev = shortStop[-1] if shortStop[-2] == NaN else shortStop[-2]
    shortStop = min(shortStop, shortStopPrev) if close[-2] < shortStopPrev else shortStop

    dir.append(1 if close[-1] > shortStopPrev else -1 if close[-1] < longStopPrev else 1)

    signal = 'buy' if dir[-1] == 1 and dir[-2] == -1 else 'sell' if dir[-1] == -1 and dir[-2] == 1 else 'NoTrade'
    print(signal)
