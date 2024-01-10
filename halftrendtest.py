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

warnings.filterwarnings('ignore')

client = Client("ZOwAm0l1XLQxvDaHGwnsVyUSGuhNqKMAJwqyXmJdCbWmpPFKfwxltuOIJK5UZY3X",
                "Q07zJXytFZMPiTrt5D2oKlvqmyEsn5deizijvwGqto1P8RzAXguD2go05fqWlzmA", {"verify": False, "timeout": 20})

trend =[0]
nextTrend = [0]
up = [npNaN, 0]
down = [npNaN, 0]
amplitude = 2
channelDeviation = 2


def sma(source, length):
    sma_out = source.rolling(length).mean()
    return sma_out


def rma(source, length):
    alpha = 1 / length
    rma_out = [npNaN, 0]
    for i in range(length-1):
        rma_out.append(sma(source, length) if rma_out[-2] == float('nan') else (alpha * source[i]) + ((1 - alpha) * (0 if rma_out[-1] == float('nan') else rma_out[-1])))
    return rma_out

def atr(length):
    trueRange = [npNaN, 0]
    for i in range(length-1):
        trueRange.append(
            high[i] - low[i] if high[i - 1] == float('nan') else max(max(high[i] - low[i], abs(high[i] - close[i - 1])),
                                                                     abs(low[i] - close[i - 1])))
    return rma(trueRange, length)

def highestbars(source, length):
    lastbar = float(source[-1])
    secondlastbar = float(source[-2])
    thirdlastbar = float(source[-3])
    # print(thirdlastbar, secondlastbar, lastbar)
    return -2 + np.argmax(source[-(length + 1):])

def lowestbars(source, length):
    lastbar = float(source[-1])
    secondlastbar = float(source[-2])
    thirdlastbar = float(source[-3])
    # print(thirdlastbar, secondlastbar, lastbar)
    return -2 + np.argmin(source[-(length + 1):])

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

while True:
    now = datetime.now()
    _get_historical_data_('ETHUSDT', '15m', '150')
    df = df1
    df = df.iloc[:-1,:]
    open_ = df['Open']
    high = df['High']
    low = df['Low']
    close = df['Close']
    volume = df['Volume']

    open_list = open_.tolist()
    close_list = close.tolist()
    high_list = high.tolist()
    low_list = low.tolist()

    open_last = float(open_list[-2])
    open_second_last = float(open_list[-3])
    open_third_last = float(open_list[-4])
    open_fourth_last = float(open_list[-5])
    open_fifth_last = float(open_list[-6])
    close_last = float(close_list[-2])
    close_second_last = float(close_list[-3])
    close_third_last = float(close_list[-4])
    close_fourth_last = float(close_list[-5])
    close_fifth_last = float(close_list[-6])
    high_last = float(high_list[-2])
    high_second_last = float(high_list[-3])
    high_third_last = float(high_list[-4])
    low_last = float(low_list[-2])
    low_second_last = float(low_list[-3])
    low_third_last = float(low_list[-4])

    atr2 = atr(100)[-1] / 2
    dev = channelDeviation * atr2


    highPrice = high[-1 + highestbars(high, amplitude)]
    lowPrice = low[-1 + lowestbars(low, amplitude)]


    highma = sma(high, amplitude)
    lowma = sma(low, amplitude)

    maxLowPrice = float(low[-1]) if low[-2] == float('nan') else float(low[-2])
    minHighPrice = float(high[-1]) if high[-2] == float('nan') else float(high[-2])


    if nextTrend[-1] == 1:
        maxLowPrice = max(low[-3], low[-2], low[-1]) #(lowPrice, maxLowPrice)
        if low[-1] == float('nan'):
            if highma[-1] < maxLowPrice and close[-1] < low[-2]:
                # if low[-1] == float('nan')
                trend.append(1)
                nextTrend.append(0)
                minHighPrice = max(high[-3], high[-2], high[-1])
        else:
            if highma[-1] < maxLowPrice and close[-1] < low[-1]:
                trend.append(1)
                nextTrend.append(0)
                minHighPrice = max(high[-3], high[-2], high[-1]) #highPrice

    else:
        minHighPrice = min(high[-3], high[-2], high[-1]) #(highPrice, minHighPrice)

        if lowma[-1] > minHighPrice and close[-1] > high[-2] if high[-1] == float('nan') else high[-1]:
            trend.append(0)
            nextTrend.append(1)
            maxLowPrice = min(low[-3], low[-2], low[-1]) #lowPrice
    if trend[-1] == 0:
        if not True if trend[-2] == float('nan') else False and trend[-2] != 0:
        # if trend[-2] == 0 and False if trend[-2] != float('nan') else True:
            up.append(down[-1] if down[-2] == float('nan') else down[-2])
        else:
            up.append(maxLowPrice if up[-2] == float('nan') else max(maxLowPrice, up[-2]))

    else:
        if not True if trend[-2] == float('nan') else False and trend[-2] != 1:
        # if trend[-2] == 1 and False if trend[-2] != float('nan') else True:
            down.append(up[-1] if up[-2] == float('nan') else up[-2])
        else:
            down.append(minHighPrice if down[-2] == float('nan') else min(minHighPrice, down[-2]))


    ht = up[-1] if trend[-1] == 0 else down[-1]
    print(df.index[-1], ht, 'buy' if ht == up[-1] else 'sell')
    # print(trend, nextTrend)
    # time.sleep(900)