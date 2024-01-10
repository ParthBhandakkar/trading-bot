
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


now = datetime.now()
df =_get_historical_data_('SOLUSDT', '15m', '1500')


high = df['High']
low = df['Low']
close = df['Close']
open = df['Open']


# VWap
df['Cum_Vol'] = df['Volume'].cumsum()
df['Cum_Vol_Price'] = (df['Volume'] * (df['High'] + df['Low'] + df['Close']) / 3).cumsum()
df['VWAP'] = df['Cum_Vol_Price'] / df['Cum_Vol']
del df['Cum_Vol']
del df['Cum_Vol_Price']
vwap_list = df['VWAP'].tolist()
vwap_last = vwap_list[-2]

# macd
exp1 = df['Close'].ewm(span=12, adjust=False).mean()
exp2 = df['Close'].ewm(span=26, adjust=False).mean()
macd = exp1 - exp2
exp3 = macd.ewm(span=9, adjust=False).mean()

df['macd'] = macd
df['signal'] = exp3
macd_list = df['macd'].tolist()
signal_list = df['signal'].tolist()
last_value_macd = macd_list[-2]
second_last_value_macd = macd_list[-3]
last_value_signal = signal_list[-2]
second_last_value_signal = signal_list[-3]

# supertrend
# def supertrend(high, low, close, length=None, multiplier=None, offset=None, **kwargs):
#     length = int(length) if length and length > 0 else 7
#     multiplier = float(multiplier) if multiplier and multiplier > 0 else 3.0
#     high = verify_series(high, length)
#     low = verify_series(low, length)
#     close = verify_series(close, length)
#     offset = get_offset(offset)
#
#     if high is None or low is None or close is None:
#         return
#
#     # Calculate Results
#     m = close.size
#     dir_, trend = [1] * m, [0] * m
#     long, short = [npNaN] * m, [npNaN] * m
#
#     hl2_ = hl2(high, low)
#     matr = multiplier * atr(high, low, close, length)
#     upperband = hl2_ + matr
#     lowerband = hl2_ - matr
#
#     for i in range(1, m):
#         if close.iloc[i] > upperband.iloc[i - 1]:
#             dir_[i] = 1
#         elif close.iloc[i] < lowerband.iloc[i - 1]:
#             dir_[i] = -1
#         else:
#             dir_[i] = dir_[i - 1]
#             if dir_[i] > 0 and lowerband.iloc[i] < lowerband.iloc[i - 1]:
#                 lowerband.iloc[i] = lowerband.iloc[i - 1]
#             if dir_[i] < 0 and upperband.iloc[i] > upperband.iloc[i - 1]:
#                 upperband.iloc[i] = upperband.iloc[i - 1]
#
#         if dir_[i] > 0:
#             trend[i] = long[i] = lowerband.iloc[i]
#         else:
#             trend[i] = short[i] = upperband.iloc[i]
#     global super_trend
#     super_trend = trend
#
# supertrend(high, low, close)
# df['st'] = super_trend
# last_value_st = super_trend[-2]
# second_last_value_st = super_trend[-3]


# adx
def get_adx(high, low, close, lookback):
    plus_dm = high.diff()
    minus_dm = low.diff()
    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm > 0] = 0

    tr1 = pd.DataFrame(high - low)
    tr2 = pd.DataFrame(abs(high - close.shift(1)))
    tr3 = pd.DataFrame(abs(low - close.shift(1)))
    frames = [tr1, tr2, tr3]
    tr = pd.concat(frames, axis=1, join='inner').max(axis=1)
    atr = tr.rolling(lookback).mean()

    plus_di = 100 * (plus_dm.ewm(alpha=1 / lookback).mean() / atr)
    minus_di = abs(100 * (minus_dm.ewm(alpha=1 / lookback).mean() / atr))
    dx = (abs(plus_di - minus_di) / abs(plus_di + minus_di)) * 100
    adx = ((dx.shift(1) * (lookback - 1)) + dx) / lookback
    adx_smooth = adx.ewm(alpha=1 / lookback).mean()
    return plus_di, minus_di, adx_smooth

df['plus_di'] = pd.DataFrame(get_adx(df['High'], df['Low'], df['Close'], 14)[0]).rename(columns={0: 'plus_di'})
df['minus_di'] = pd.DataFrame(get_adx(df['High'], df['Low'], df['Close'], 14)[1]).rename(columns={0: 'minus_di'})
df['adx'] = pd.DataFrame(get_adx(df['High'], df['Low'], df['Close'], 14)[2]).rename(columns={0: 'adx'})
df = df.dropna()
plus_di = df['plus_di'].tolist()
minus_di = df['minus_di'].tolist()
adx = df['adx'].tolist()
last_plus_di = plus_di[-2]
second_last_plus_di = plus_di[-3]
last_minus_di = minus_di[-2]
second_last_minus_di = minus_di[-3]
last_adx = adx[-2]

# bollinger bands
MA = df['Close'].rolling(window=2).mean()
SD = df['Close'].rolling(window=2).std()
df['MA'] = MA
upper_line = MA + 2 * SD
lower_line = MA - 2 * SD
df['ema_20'] = df.Close.ewm(span=20, adjust=False).mean()
df['upper'] = upper_line
df['lower'] = lower_line

ema20_list = df['ema_20'].tolist()
last_value_mid = ema20_list[-2]
lower_list = df['lower'].tolist()
upper_list = df['upper'].tolist()
lower_last = lower_list[-2]
upper_last = upper_list[-2]


# aroon
def aroon(df):
    global df_aroon
    df_aroon = df.copy()
    df_aroon['aroon_up'] = 100 * df.High.rolling(14 + 1).apply(lambda x: x.argmax()) / 14
    df_aroon['aroon_down'] = 100 * df.Low.rolling(14 + 1).apply(lambda x: x.argmin()) / 14
    df_aroon['aroon_osc'] = df_aroon['aroon_up'] - df_aroon['aroon_down']
aroon(df)
aroon_up_lst = df_aroon['aroon_up'].to_list()
aroon_down_lst = df_aroon['aroon_down'].to_list()
last_value_up = aroon_up_lst[-2]
last_value_down = aroon_down_lst[-2]


# ema crossovers

def ema_crossovers():
    ema_5 = df.Close.ewm(span=5, adjust=False).mean()
    ema_8 = df.Close.ewm(span=8, adjust=False).mean()
    ema_13 = df.Close.ewm(span=13, adjust=False).mean()
    df['5ema'] = ema_5
    df['8ema'] = ema_8
    df['13ema'] = ema_13
    ema_5_list = df['5ema'].to_list()
    ema_8_list = df['8ema'].to_list()
    ema_13_list = df['13ema'].to_list()
    ema_crossovers.ema_5_last = ema_5_list[-2]
    ema_crossovers.ema_5_second_last = ema_5_list[-3]
    ema_crossovers.ema_8_last = ema_8_list[-2]
    ema_crossovers.ema_8_second_last = ema_8_list[-3]
    ema_crossovers.ema_13_last = ema_13_list[-2]
    ema_crossovers.ema_13_second_last = ema_13_list[-3]

ema_crossovers()

# atr

high_low = df['High'] - df['Low']
high_close = np.abs(df['High'] - df['Close'].shift())
low_close = np.abs(df['Low'] - df['Close'].shift())
ranges = pd.concat([high_low, high_close, low_close], axis=1)
true_range = np.max(ranges, axis=1)
atr_series = true_range.rolling(14).sum() / 14
ema_14 = df.Close.ewm(span=13, adjust=False).mean()
upper_band = atr_series + ema_14
lower_band = ema_14 - atr_series
df['upper_band'] = upper_band
df['lower_band'] = lower_band
upper_band_list = upper_band.to_list()
lower_band_list = lower_band.to_list()
upper_band_last = upper_band_list[-2]
lower_band_last = lower_band_list[-2]

# Stochastic RSI
def stochastic_rsi():
    periods = 14
    close_delta = df['Close'].diff()

    ema = True
    up = close_delta.clip(lower=0)
    down = -1 * close_delta.clip(upper=0)

    if ema == True:
        ma_up = up.ewm(com=periods - 1, adjust=True, min_periods=periods).mean()
        ma_down = down.ewm(com=periods - 1, adjust=True, min_periods=periods).mean()
    else:
        ma_up = up.rolling(window=periods, adjust=False).mean()
        ma_down = down.rolling(window=periods, adjust=False).mean()

    rsi = ma_up / ma_down
    rsi = 100 - (100 / (1 + rsi))
    df['rsi'] = rsi
    stochrsi = (rsi - rsi.rolling(14).min()) / (rsi.rolling(14).max() - rsi.rolling(14).min()) * 100
    df['stochrsi_K'] = stochrsi.rolling(3).mean()
    df['stochrsi_D'] = df['stochrsi_K'].rolling(3).mean()
stochastic_rsi()
# stoch_k_list = df['stochrsi_K'].tolist()
# stoch_d_list = df['stochrsi_D'].tolist()
# last_value_k = stoch_k_list[-2]
# second_last_value_k = stoch_k_list[-3]
# last_value_d = stoch_d_list[-2]
# second_last_value_d = stoch_d_list[-3]


ema_crossovers()


length = len(df)

bodydiff = [0] * length

highdiff = [0] * length
lowdiff = [0] * length
ratio1 = [0] * length
ratio2 = [0] * length


n1=2
n2=2
backCandles=30
signal = [0] * length
ema_200 = df.Close.ewm(span=200, adjust=False).mean()
df['ema_200'] = ema_200
for i in range(backCandles, len(df)-n2):
    color = 'green'
    open_last = df['Open'][i]
    open_second_last = df['Open'][i - 1]
    open_third_last = df['Open'][i - 2]
    open_fourth_last = df['Open'][i - 3]
    open_fifth_last = df['Open'][i - 4]

    close_last = df['Close'][i]
    close_second_last = df['Close'][i - 1]
    close_third_last = df['Close'][i - 2]
    close_fourth_last = df['Close'][i - 3]
    close_fifth_last = df['Close'][i - 4]

    ema_200_last = df['ema_200'][i]

    ema_5_last = df['5ema'][i]
    ema_5_second_last = df['5ema'][i - 1]
    ema_8_last = df['8ema'][i]
    ema_8_second_last = df['8ema'][i - 1]
    ema_13_last = df['13ema'][i]
    ema_13_second_last = df['13ema'][i - 1]

    vwap_last = df['VWAP'][i]

    last_value_mid = df['ema_20'][i]
    upper_last = df['upper'][i]
    lower_last = df['lower'][i]

    last_adx = df['adx'][i]

    # last_value_st = df['st'][i]
    # second_last_value_st = df['st'][i-1]

    last_value_d = df['stochrsi_D'][i]
    last_value_k = df['stochrsi_K'][i]
    second_last_value_d = df['stochrsi_D'][i - 1]
    second_last_value_k = df['stochrsi_K'][i - 1]

    last_value_macd = df['macd'][i]
    last_value_signal = df['signal'][i]
    second_last_value_macd = df['macd'][i - 1]
    second_last_value_signal = df['signal'][i - 1]

    atr2 = atr(100)[-1] / 2
    dev = channelDeviation * atr2
    sma_low = sma(low, 2).to_list()
    sma_high = sma(high, 2).to_list()

    sma_low_last = sma_low[i]
    sma_high_last = sma_high[i]

    highPrice = high[-1 + highestbars(high, amplitude)]
    lowPrice = low[-1 + lowestbars(low, amplitude)]

    highma = sma(high, amplitude)
    lowma = sma(low, amplitude)

    maxLowPrice = float(low[i])  # float(low[-1]) if low[-2] == float('nan') else float(low[-2]))
    minHighPrice = float(high[i])  # float(high[-1]) if high[-2] == float('nan') else float(high[-2])
    #
    # if nextTrend[i-30] == 1:
    #     maxLowPrice = max(low[i-2], low[i-1], low[i])  # (lowPrice, maxLowPrice)
    #
    #     if highma[-1] < maxLowPrice and close[-1] < low[-1]:  # low[-2] if low[-1] == float('nan') else low[-1]:
    #         trend.append(1)
    #         nextTrend.append(0)
    #         minHighPrice = max(high[-3], high[-2], high[-1])  # highPrice
    #
    # else:
    #     minHighPrice = min(high[i-2], high[i-1], high[i])  # (highPrice, minHighPrice)
    #
    #     if lowma[i] > minHighPrice and close[i] > high[i]:  # high[-2] if high[-1] == float('nan') else high[-1]:
    #         trend.append(0)
    #         nextTrend.append(1)
    #         maxLowPrice = min(low[i-2], low[i-1], low[i])  # lowPrice
    # if trend[-1] == 0:  # if not True if trend[-2] == float('nan') else False and trend[-2] != 0:
    #     if len(trend) > 1:
    #         if trend[i-1] == 0:
    #             up.append(down[-2] if down[-2] else down[-1])  # down[-1] if down[-2] == float('nan') else down[-2]
    #     else:
    #         up.append(max(low[-1], up[-2]) if len(up) > 1 else low[
    #             -1])  # maxLowPrice if up[-2] == float('nan') else max(maxLowPrice, up[-2])
    #
    # else:
    #     if trend[-2] == 1:  # if not True if trend[-2] == float('nan') else False and trend[-2] != 1:
    #         down.append(up[-2] if up[-2] else up[-1])  # up[-1] if up[-2] == float('nan') else up[-2]
    #     else:
    #         down.append(
    #             min(high[-1], down[-2]))  # minHighPrice if down[-2] == float('nan') else min(minHighPrice, down[-2])

    if color == 'red':
        if close_last > sma_high_last:
            color = 'green'
        else:
            color = 'red'
    elif color == 'green':
        if close_last < sma_low_last:
            color = 'red'
        else:
            color = 'green'
    ht = up[-1] if trend[-1] == 0 else down[-1]
    #!!!! parameters
    if (color == 'green' and last_plus_di > last_minus_di and last_adx > 23.5):
        signal[i] = 1

    elif (color == 'red' and last_minus_di > last_plus_di and last_adx > 23.5):
        signal[i] = -1
    else:
        signal[i] = 0


df['signal']=signal


print(df[df['signal']==1].count())



def SIGNAL():
    return df.signal



class MyCandlesStrat(Strategy):  
    def init(self):
        super().init()
        self.signal1 = self.I(SIGNAL)

    def next(self):
        super().next() 
        if self.signal1==1:
            sl1 = self.data.Close[-1] - (0.01*self.data.Close[-1])
            tp1 = self.data.Close[-1] + (0.015*self.data.Close[-1])
            self.buy(sl=sl1, tp=tp1)
        elif self.signal1==-1:
            sl1 = self.data.Close[-1] + (0.01*self.data.Close[-1])
            tp1 = self.data.Close[-1] - (0.015*self.data.Close[-1])
            self.sell(sl=sl1, tp=tp1)



bt = Backtest(df, MyCandlesStrat, cash=15_000, commission=.002)
stat = bt.run()
print(stat)




