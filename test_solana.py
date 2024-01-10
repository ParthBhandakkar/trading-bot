import time
from datetime import date, datetime
import numpy as np
import pandas as pd
import json
import requests
import datetime as dt
from binance.client import Client
import warnings

warnings.filterwarnings('ignore')

client = Client("ZOwAm0l1XLQxvDaHGwnsVyUSGuhNqKMAJwqyXmJdCbWmpPFKfwxltuOIJK5UZY3X",
                "Q07zJXytFZMPiTrt5D2oKlvqmyEsn5deizijvwGqto1P8RzAXguD2go05fqWlzmA", {"verify": False, "timeout": 20})

trend =[0]
nextTrend = [0]
up = [0]
down = [0]
amplitude = 2
channelDeviation = 2
color = 'red'


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
    trueRange = []
    for i in range(length-1):
        trueRange.append(max(max(high[i] - low[i], abs(high[i] - close[i - 1])),abs(low[i] - close[i - 1])) if close[i-1] else \
                         high[i] - low[i])
    return rma(trueRange, length)

def highestbars(source, length):
    # lastbar = float(source[-1])
    # secondlastbar = float(source[-2])
    # thirdlastbar = float(source[-3])
    # print(thirdlastbar, secondlastbar, lastbar)
    return -2 + np.argmax(source[-(length + 1):])

def lowestbars(source, length):
    # lastbar = float(source[-1])
    # secondlastbar = float(source[-2])
    # thirdlastbar = float(source[-3])
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


def sma_adx(source, length):
    source = pd.Series(source)
    sma_out = source.rolling(length).mean()
    return sma_out

def rma_adx(source, length):
    alpha = 1 / length

    rma_out = []

    for i in range(len(source)):
        rma_out.append(sma_adx(source, length)[length] if len(rma_out) < 2 else (alpha * source[i]) + ((1 - alpha) * rma_out[-1]))
    return rma_out

def atr_adx(length):
    trueRange = []
    for i in range(length-1):
        trueRange.append(max(high[i] - low[i], abs(high[i] - close[i - 1]), abs(low[i] - close[i - 1])) if close[i-1] else high[i] - low[i])
    return rma_adx(trueRange, length)

while True:
    df = _get_historical_data_('SOLUSDT', '15m', '150')
    # df = df.iloc[:-1,:]
    open_ = df['Open']
    high = df['High']
    low = df['Low']
    close = df['Close']
    volume = df['Volume']
    now = datetime.now()

    lensig, leng = 14, 14

    tr = [max(high[i] - low[i], abs(high[i] - close[i - 1]), abs(low[i] - close[i - 1])) for i in range(len(high))]

    up_adx = [high[i] - high[i - 1] for i in range(len(high))]
    down_adx = [-(low[i] - low[i - 1]) for i in range(len(high))]

    plusDM = [up_adx[i] if up_adx[i] > down_adx[i] and up_adx[i] > 0 else 0 for i in range(len(high))]
    minusDM = [down_adx[i] if down_adx[i] > up_adx[i] and down_adx[i] > 0 else 0 for i in range(len(low))]

    trur = rma_adx(tr, 14)

    plus = [(100 * rma_adx(plusDM, 14)[i] / trur[i]) for i in range(len(plusDM))]

    minus = [(100 * rma_adx(minusDM, 14)[i] / trur[i]) for i in range(len(minusDM))]

    sum = [plus[i] + minus[i] if plus[i] + minus[i] != 0 else 1 for i in range(len(plus))]
    diff = [abs(plus[i] - minus[i]) for i in range(len(plus))]
    deno = [1 if sum[i] == 0 else sum[i] for i in range(len(sum))]
    fact = [diff[i] / deno[i] for i in range(len(diff))]

    adx = [100 * rma_adx(fact, 14)[i] for i in (range(len(plus)))]
    last_adx = adx[-1]
    last_plus_di = plus[-1]
    last_minus_di = minus[-1]


    # print(f'adx = {last_adx} plus = {last_plus_di} minus = {last_minus_di}' )
    atr2 = atr(100)[-1] / 2
    dev = channelDeviation * atr2


    highPrice = high[-1 + highestbars(high, amplitude)]
    lowPrice = low[-1 + lowestbars(low, amplitude)]


    highma = sma(high, amplitude)
    lowma = sma(low, amplitude)

    maxLowPrice = float(low[-2])                                    #float(low[-1]) if low[-2] == float('nan') else float(low[-2]))
    minHighPrice = float(high[-2])                                  #float(high[-1]) if high[-2] == float('nan') else float(high[-2])

    sma_low = sma(low, 2).to_list()
    sma_high = sma(high, 2).to_list()

    sma_low_last = sma_low[-1]
    sma_high_last = sma_high[-1]

    open_list = open_.tolist()
    close_list = close.tolist()
    high_list = high.tolist()
    low_list = low.tolist()

    open_last = float(open_list[-1])
    open_second_last = float(open_list[-2])
    open_third_last = float(open_list[-3])
    open_fourth_last = float(open_list[-5])
    open_fifth_last = float(open_list[-6])
    close_last = float(close_list[-1])
    close_second_last = float(close_list[-2])
    close_third_last = float(close_list[-3])
    close_fourth_last = float(close_list[-5])
    close_fifth_last = float(close_list[-6])
    high_last = float(high_list[-1])
    high_second_last = float(high_list[-2])
    high_third_last = float(high_list[-3])
    low_last = float(low_list[-1])
    low_second_last = float(low_list[-2])
    low_third_last = float(low_list[-3])

    if nextTrend[-1] == 1:
        maxLowPrice = max(low[-3], low[-2], low[-1])                                                #(lowPrice, maxLowPrice)

        if highma[-1] < maxLowPrice and close[-1] < low[-2]:            #low[-2] if low[-1] == float('nan') else low[-1]:
            trend.append(1)
            nextTrend.append(0)
            minHighPrice = max(high[-3], high[-2], high[-1])                                        #highPrice

    else:
        minHighPrice = min(high[-3], high[-2], high[-1])                                              #(highPrice, minHighPrice)

        if lowma[-1] > minHighPrice and close[-1] > high[-2]:               #high[-2] if high[-1] == float('nan') else high[-1]:
            trend.append(0)
            nextTrend.append(1)
            maxLowPrice = min(low[-3], low[-2], low[-1])                                              #lowPrice
    if trend[-1] == 0:                              # if not True if trend[-2] == float('nan') else False and trend[-2] != 0:
        if len(trend) > 1:
            if trend[-2] != 0:
                up.append(down[-2] if down[-2] else down[-1])                                                  #down[-1] if down[-2] == float('nan') else down[-2]
        else:
            up.append(max(low[-1], up[-2]) if len(up) > 1 else low[-1])                    #maxLowPrice if up[-2] == float('nan') else max(maxLowPrice, up[-2])

    else:
        if trend[-2] == 1:                              # if not True if trend[-2] == float('nan') else False and trend[-2] != 1:
            down.append(up[-2] if up[-2] else up[-1])                                              #up[-1] if up[-2] == float('nan') else up[-2]
        else:
            down.append(min(high[-1], down[-2]))        #minHighPrice if down[-2] == float('nan') else min(minHighPrice, down[-2])


    ht = up[-1] if trend[-1] == 0 else down[-1]

    if color == 'red':
        maxLowPrice = max(low[-3], low[-2], low[-1])
        if maxLowPrice > sma_low_last and close_last > high_second_last:
            color = 'green'
        else:
            color = 'red'
    elif color == 'green':
        minHighPrice = min(high[-3], high[-2], high[-1])
        if minHighPrice < sma_high_last and close_last < low_second_last:
            color = 'red'
        else:
            color = 'green'
    # print('maxlowprice = ', maxLowPrice, 'maxhighprice = ', minHighPrice, 'smalow =', sma_low_last, 'smahigh =', sma_high_last )
    if color == 'green' and last_adx > 24 and last_plus_di > last_minus_di:
        action = 'buy'
        print(df.index[-1], ht, color)
        print(action)
        print('plusdi = ', last_plus_di, 'minusdi = ', last_minus_di, 'adx = ', last_adx)
        print("sma_low_last = ", sma_low_last, "smahighlast =", sma_high_last, "maxlowprice = ", maxLowPrice, "minhighprice = ", minHighPrice)
        print("------------------------------------------")
    elif color == 'red' and last_adx > 24 and last_minus_di > last_plus_di:
        action = 'sell'
        print(df.index[-1], ht, color)
        print(action)
        print('plusdi = ', last_plus_di, 'minusdi = ', last_minus_di, 'adx = ', last_adx)
        print("sma_low_last = ", sma_low_last, "smahighlast =", sma_high_last, "maxlowprice = ", maxLowPrice, "minhighprice = ", minHighPrice)

        print("------------------------------------------")

    else:
        action = 'hold'
        print(df.index[-1], ht, color)
        print(action)
        print('plusdi = ', last_plus_di, 'minusdi = ', last_minus_di, 'adx = ',  last_adx)
        print("sma_low_last = ", sma_low_last, "smahighlast =", sma_high_last, "maxlowprice = ", maxLowPrice, "minhighprice = ", minHighPrice)

        print("------------------------------------------")

    time.sleep(900)
