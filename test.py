import numpy as np
import pandas as pd
import json
from numpy import NaN
import requests
import datetime as dt
from binance.client import Client
import warnings
from datetime import datetime

warnings.filterwarnings('ignore')

client = Client("1e1c2bf69302d1f442b606d2bb4792d84f14eab2f8c37b4c96db99f7aa82ba3c",
                "0ba00fab8eeb44fcccb7d0612e176422c258069ec4756ae5b0e778c77c639f07", {"verify": False, "timeout": 20},
                testnet=True)


def _get_historical_data_(symbol, interval, limit):
    root_url = "https://fapi.binance.com/fapi/v1/klines"
    url = root_url + '?symbol=' + symbol + '&interval=' + interval + '&limit=' + limit
    data = json.loads(requests.get(url).text)
    # global df1
    # pd.set_option('display.max_columns', None)
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

df_eth = _get_historical_data_('ETHUSDT', '1h', '1500')
ema = df_eth.Close.ewm(span=200, adjust=False).mean().to_list()
print(ema[-1])
# def sma(source, length):
#     sma_out = source.rolling(length).mean()
#     return sma_out
#
#
# def rma(source, length):
#     alpha = 1 / length
#     rma_out = [NaN, 0]
#     for i in range(length - 1):
#         rma_out.append(sma(source, length) if rma_out[-2] == float('nan') else (alpha * source[i]) + (
#                     (1 - alpha) * (0 if rma_out[-1] == float('nan') else rma_out[-1])))
#     return rma_out
#
#
# def atr(length, high, low, close):
#     trueRange = [NaN, 0]
#     for i in range(length - 1):
#         trueRange.append(
#             high[i] - low[i] if high[i - 1] == float('nan') else max(max(high[i] - low[i], abs(high[i] - close[i - 1])),
#                                                                      abs(low[i] - close[i - 1])))
#     return rma(trueRange, length)
#
#
# def pivot_high(df, len_right, len_left):
#     pivots = df['High'].shift(-len_right, fill_value=0).rolling(len_left).max()
#     return pivots[-2]
#
#
# def pivot_low(df, len_right, len_left):
#     pivots = df['Low'].shift(-len_right, fill_value=0).rolling(len_left).min()
#     return pivots[-2]
#
# prd = 2
# factor = 3
# pD = 10
# ph = []
# center = []
# pl = []
# lastpp = []
# tup = [NaN]
# tdown = [NaN]
# trend = [1]
# def PP_supertrend(df, close):
#
#     ph.append(pivot_high(df, prd, prd))
#     pl.append(pivot_low(df, prd, prd))
#     center.append(ph[-1])
#     lastpp.append(ph[-1] if ph else pl[-1] if pl else np.NaN)
#     if lastpp[-1]:
#         center.append(center[-1] * 2 + lastpp[-1] / 3)
#
#     up = center[-1] - (factor * (atr(pD, df["High"], df['Low'], df['Close'])[-1]))
#     dn = center[-1] + (factor * (atr(pD, df["High"], df['Low'], df['Close'])[-1]))
#
#     tup.append(max(up, tup[-1]) if close[-2] > tup[-1] else up)
#     tdown.append(min(dn, tdown[-1]) if close[-2] < tup[-1] else dn)
#     trend.append(1 if close[-1] > tdown[-1] else -1 if close[-1] < tup[-1] else trend[-1])
#
#     signal = 'none'
#     if trend[-1] == 1 and trend[-2] == -1:
#         signal = 'buy'
#     elif trend[-1] == -1 and trend[-2] == 1:
#         signal = 'sell'
#
#     return signal
#
#
# actions = ['hold']
# orders = []
#
# while True:
#     now = datetime.now()
#     df_eth = _get_historical_data_('ETHUSDT', '1h', '150')
#     df_sol = _get_historical_data_('SOLUSDT', '15m', '150')
#     df_avax = _get_historical_data_('AVAXUSDT', '15m', '150')
#     df_ltc = _get_historical_data_('LTCUSDT', '15m', '150')
#     df_xrp = _get_historical_data_('XRPUSDT', '15m', '150')
#
#     high = df_eth['High']
#     high_list = high.to_list()
#     low = df_eth['Low']
#     low_list = low.to_list()
#     close = df_eth['Close']
#     close_list = close.to_list()
#     if PP_supertrend(df_eth, close_list) == 'buy':
#         print(datetime.now(), PP_supertrend(df_eth, close_list))
#     elif PP_supertrend(df_eth, close_list) == 'sell':
#         print(datetime.now(), PP_supertrend(df_eth, close_list))
#     else:
#         print('none')
