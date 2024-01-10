import numpy as np
import pandas as pd
import json
import requests
import datetime as dt
import time
from datetime import date, datetime
from numpy import nan as npNaN
from ta.trend import ADXIndicator
from pandas_ta.volatility import atr
from pandas_ta.utils import get_offset, pascals_triangle, verify_series
from pandas_ta.overlap import hl2
from binance.client import Client
import warnings

warnings.filterwarnings('ignore')

client = Client("ZOwAm0l1XLQxvDaHGwnsVyUSGuhNqKMAJwqyXmJdCbWmpPFKfwxltuOIJK5UZY3X",
                "Q07zJXytFZMPiTrt5D2oKlvqmyEsn5deizijvwGqto1P8RzAXguD2go05fqWlzmA", {"verify": False, "timeout": 20})

def _get_historical_data_(symbol, interval, limit):
    root_url = "https://fapi.binance.com/fapi/v1/klines"
    url = root_url + '?symbol=' + symbol + '&interval=' + interval + '&limit=' + limit
    data = json.loads(requests.get(url).text)
    global df1
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
df = _get_historical_data_('ETHUSDT', '15m', '150')
df = df.iloc[:-1,:]
open_ = df['Open']
high = df['High']
low = df['Low']
close = df['Close']
volume = df['Volume']

def rma(source, length):
    alpha = 1 / length
    rma_out = []
    for i in range(length-1):
        rma_out.append((alpha * source[i]) + ((1 - alpha) * (0))) #rma_out[-1] if rma_out[-1] else
    return rma_out

def atr(length):
    trueRange = [npNaN, 0]
    for i in range(length-1):
        trueRange.append(max(max(high[i] - low[i], abs(high[i] - close[i - 1])),abs(low[i] - close[i - 1])) if close[i-1] else \
                         high[i] - low[i])
    return rma(trueRange, length)

lensig = 14
leng = 14
tr = (max(max(high[-1] - low[-1], abs(high[-1] - close[-2])),abs(low[-1] - close[-2])))
up = []
down = []
for i in range(0, len(high)):
    up.append(high[i]-high[i-14])
    down.append(-(low[i] - low[i-14]))

if up[-1] > down[-1] and up[-1] > 0:
    plusDM = up
else:
    plusDM = 0
if down > up and down > 0:
    minusDM = down
else:
    minusDM = 0

trur = atr(leng)
plus = 100*rma(plusDM, leng)
plus_dmi = [i / j for i, j in zip(plus, trur)]
minus = 100*rma(minusDM, leng)
minus_dmi = [i / j for i, j in zip(minus, trur)]
sum = plus_dmi + minus_dmi

dx = abs(plus_dmi - minus_dmi)/sum
adx = 100*rma(dx, lensig)
print('plus = ', plus, 'minus = ', minus, 'adx = ', adx)



