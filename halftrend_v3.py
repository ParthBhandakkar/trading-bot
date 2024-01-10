import ta_py as ta
import numpy as np
import pandas as pd
import json
import requests
import datetime as dt
import time
from datetime import date, datetime
from numpy import nan as npNaN
from pandas_ta.volatility import atr
from pandas_ta.utils import get_offset, pascals_triangle, verify_series
from pandas_ta.overlap import hl2
from binance.client import Client
import warnings
from backtesting import Strategy
from backtesting import Backtest



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

def sma(source, length):
    sma_out = source.rolling(length).mean()
    return sma_out


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

def highestbars(src, len) :
    index = 0
    highest = 0.0
    for i in range(0, len-1):
        if src[i] >= highest:
            highest = src[i]
            index = -i
    return index

def lowestbars(src, len):
    index = 0
    lowest = 0.0
    for i in range(0, len-1):
        if src[i]<=lowest:
            lowest = src[i]
            index = -i
    return index

amplitude = 2
channel_deviation = 2
trend = [0]
nexttrend = [0]


up = [0]
down = [0]
atrhigh = [0]
atrlow = [0]

while True:

    df = _get_historical_data_('ETHUSDT', '1m', '150')
    df.columns = ['datetime', 'Open', 'High', 'Low', 'Close', 'Volume','Close_time', 'qav', 'num_trades','taker_base_vol', 'taker_quote_vol', 'ignore']
    df.index = [dt.datetime.fromtimestamp(x/1000.0) for x in df.datetime]
    df=df.astype(float)
    high = df['High']
    low = df['Low']
    close = df['Close']
    open = df['Open']

    # halftrend code

    maxlowprice = low[-2]
    minhighprice = high[-2]

    atr2 = atr(100)[-1]/2
    dev = channel_deviation*atr2

    highprice = high[highestbars(high, amplitude)]
    lowprice = low[lowestbars(low, amplitude)]
    highma = sma(high,amplitude)
    lowma = sma(low, amplitude)

    if nexttrend[-1] == 1:
        maxlowprice = max(lowprice, maxlowprice)
        if highma < maxlowprice and close[-1] < low[-2]:
            trend.append(1)
            nexttrend.append(0)
            minhighprice = highprice

    else:
        minhighprice = min(highprice, minhighprice)
        if lowma > minhighprice and close[-1] > high[-2]:
            trend.append(0)
            nexttrend.append(1)
            maxlowprice = lowprice

    if trend[-1] == 0:
        if len(trend) > 1 and trend[-2] != 1:
            up[-1] = down[-2]
        else:
            up = max(maxlowprice, up[-2])
        atrhigh.append(up[-1] + dev[-1])
        atrlow.append(up[-1] - dev[-1])

    else:
        if len(trend) > 1 and trend[-2]!=1:
            down[-1] = up[-2]
        else:
            down = min(minhighprice, down[-2])
        atrhigh.append(down[-1] + dev[-1])
        atrlow.append(down[-1] - dev[-1])

    if trend == 0:
        ht = up[-1]
        action = 'buy'
    else:
        ht = down[-1]
        action = 'sell'
    print(ht)
    print(action)
    time.sleep(60)
            