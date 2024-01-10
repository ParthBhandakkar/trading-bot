import pandas as pd
import json
import numpy as np
import requests
from pandas_ta import linreg
import datetime as dt
from numpy import NaN
from binance.client import Client
import warnings
from datetime import datetime

warnings.filterwarnings('ignore')

client = Client("65f762d96597cbc34d09cd1f206772b70531fd0deb62d374456dfaaafbf2befa",
                "199333bf2a9a8326633f103162418e9b8ee7e8a5f9df921ab3b0e08051cbd142", {"verify": False, "timeout": 20}, testnet=True)

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
df_eth = _get_historical_data_('ETHUSDT', '15m', '150')
df_sol =_get_historical_data_('SOLUSDT', '15m', '150')
df_avax = _get_historical_data_('AVAXUSDT', '15m', '150')
df_ltc = _get_historical_data_('LTCUSDT', '15m', '150')
df_xrp = _get_historical_data_('XRPUSDT', '15m', '150')
print(df_eth)
#
# def heikin_ashi(df):
#     heikin_ashi_df = df.copy()
#     # heikin_ashi_df = pd.DataFrame(index=df.index.values, columns=['open', 'high', 'low', 'close'])
#     heikin_ashi_df['Close'] = (df['Open'] + df['High'] + df['Low'] + df['Close']) / 4
#
#     for i in range(len(df)):
#         if i == 0:
#             heikin_ashi_df.iat[0, 0] = df['Open'].iloc[0]
#         else:
#             heikin_ashi_df.iat[i, 0] = (heikin_ashi_df.iat[i - 1, 0] + heikin_ashi_df.iat[i - 1, 3]) / 2
#
#     heikin_ashi_df['High'] = heikin_ashi_df.loc[:, ['Open', 'Close']].join(df['High']).max(axis=1)
#
#     heikin_ashi_df['Low'] = heikin_ashi_df.loc[:, ['Open', 'Close']].join(df['Low']).min(axis=1)
#
#     return heikin_ashi_df
#
#
#
#
#
# def sma(source, length):
#     sma_out = source.rolling(length).mean()
#     return sma_out
#
# def rma(source, length):
#     alpha = 1 / length
#     rma_out = [NaN, 0]
#     for i in range(length-1):
#         rma_out.append(sma(source, length) if rma_out[-2] == float('nan') else (alpha * source[i]) + ((1 - alpha) * (0 if rma_out[-1] == float('nan') else rma_out[-1])))
#     return rma_out
#
# def atr(length, high, low, close):
#     trueRange = [NaN, 0]
#     for i in range(length-1):
#         trueRange.append(
#             high[i] - low[i] if high[i - 1] == float('nan') else max(max(high[i] - low[i], abs(high[i] - close[i - 1])),
#                                                                      abs(low[i] - close[i - 1])))
#     return rma(trueRange, length)
#
# def highest(source, length):
#     return -2 + np.argmax(source[-(length + 1):])
#
# def lowest(source, length):
#     return -2 + np.argmin(source[-(length + 1):])
#
# dir = [1]
# length = 22
# mult = 3.0
# showLabels = True
# useClose = True
# longStop = [NaN]
# shortStop = [NaN]
#
# def CE(df, high, low, close, longStop=longStop, shortStop=shortStop):
#     atr_val = mult * (atr(length, high, low, close)[-1])
#     longStop.append((highest(close, length)) - atr_val)  # if useClose == True else highest(high, length)
#     longStopPrev = longStop[-1] if longStop[-2] == NaN else longStop[-2]
#     longStop = max(longStop, longStopPrev) if close[-2] > longStopPrev else longStop
#
#     shortStop.append((lowest(close, length)) + atr_val)  # if useClose else lowest(low, length)
#     shortStopPrev = shortStop[-1] if shortStop[-2] == NaN else shortStop[-2]
#     shortStop = min(shortStop, shortStopPrev) if close[-2] < shortStopPrev else shortStop
#
#     dir.append(1 if close[-1] > shortStopPrev else -1 if close[-1] < longStopPrev else 1)
#
#     signal = 'buy' if dir[-1] == 1 and dir[-2] == -1 else 'sell' if dir[-1] == -1 and dir[-2] == 1 else 'NoTrade'
#     return signal
#
# def zlsma(df):
#     close_ = df['Close']
#     lsma = linreg(close_, length=32)
#     lsma2 = linreg(lsma, length=32)
#     eq = lsma - lsma2
#     zlma = (lsma + eq).to_list()
#     return zlma[-1]
#
#
# def strategy(df, close_last, high, low, close):
#     if close_last > zlsma(df) and CE(df, high, low, close, longStop=longStop, shortStop=shortStop ) == 'buy':
#         return'buy'
#     elif close_last < zlsma(df) and CE(df, high, low, close, longStop=longStop, shortStop=shortStop ) == 'sell':
#         return'sell'
#     else :
#         return'no'
#
# actions = ['hold']
# orders = []
#
# while True:
#     now = datetime.now()
#     df_eth = _get_historical_data_('ETHUSDT', '15m', '150')
#     df_ha_eth = heikin_ashi(df_eth)
#     close = df_ha_eth['Close']
#     close_list = df_ha_eth['Close'].to_list()
#     high = df_ha_eth["High"].to_list()
#     low = df_ha_eth['Low'].to_list()
#     close_last = close_list[-1]
#
#     if strategy(df_ha_eth, close_last, high, low, close) == 'buy':
#         action = 'buy'
#         actions.append(action)
#         print(now)
#         print(action)
#         print(actions[-1])
#         print("------------------------------------------")
#         print(zlsma(df_ha_eth), CE(df_ha_eth, high, low, close, longStop=longStop, shortStop=shortStop ), close_last)
#     elif strategy(df_ha_eth, close_last, high, low, close) == 'sell':
#         action = 'sell'
#         actions.append(action)
#         print(actions[-1])
#         print(now)
#         print(action)
#         print("------------------------------------------")
#         print(zlsma(df_ha_eth), CE(df_ha_eth, high, low, close, longStop=longStop, shortStop=shortStop ), close_last)
#
#
#     else:
#         action = 'hold'
#         actions.append(action)
#     account = client.futures_account_balance()
#
#     for i in range(len(account)):
#         if account[i].get('asset') == 'USDT':
#             usdtbal = account[i].get('balance')
#
#     prices = client.get_all_tickers()
#     for i in prices:
#         for j in i:
#             if j == "symbol":
#                 if i.get('symbol') == 'ETHUSDT':
#                     ETH_price = float(i.get('price'))
#
#     quantity_taken = int(100 * 20 / ETH_price)
#     leverage_taken = client.futures_change_leverage(symbol="ETHUSDT", leverage=20)
#
#     if action == 'buy':
#         orders.append('buy')
#         print(orders[-1])
#
#         place_new_order = client.futures_create_order(
#             symbol='ETHUSDT',
#             side='BUY',
#             type='MARKET',
#             quantity=quantity_taken)
#
#         active_order = client.futures_get_all_orders(symbol='ETHUSDT')
#
#         for i in active_order:
#             for j in i:
#                 if i.get('reduceOnly') == False and i.get('status') == 'FILLED':
#                     order_id = str(i.get('orderId'))
#
#         current_order = client.futures_get_order(symbol='ETHUSDT', orderId=order_id)
#
#         for i in current_order:
#             qty = float(current_order['origQty'])
#             buying_price = float(current_order['avgPrice'])
#
#         profit_price = round(buying_price * 1.01, 2)
#         stop_price = round(buying_price * 0.990, 2)
#
#         exit_order = client.futures_create_order(
#             symbol='ETHUSDT',
#             side='SELL',
#             closePosition=True,
#             type='TAKE_PROFIT_MARKET',
#             timeInForce='GTC',
#             stopPrice=profit_price,
#             quantity=qty)
#
#         place_new_order = client.futures_create_order(
#             symbol='ETHUSDT',
#             side='SELL',
#             type='STOP_MARKET',
#             timeInForce='GTC',
#             closePosition='true',
#             stopPrice=stop_price,
#             quantity=qty)
#
#     elif action == 'sell':
#         orders.append('sell')
#         print(orders[-1])
#
#         place_new_order = client.futures_create_order(
#             symbol='ETHUSDT',
#             side='SELL',
#             type='MARKET',
#             quantity=quantity_taken)
#
#
#         active_order = client.futures_get_all_orders(symbol='ETHUSDT')
#
#         for i in active_order:
#             for j in i:
#                 if i.get('reduceOnly') == False and i.get('status') == 'FILLED':
#                     order_id = str(i.get('orderId'))
#
#         current_order = client.futures_get_order(symbol='ETHUSDT', orderId=order_id)
#
#         for i in current_order:
#             qty = float(current_order['origQty'])
#             buying_price = float(current_order['avgPrice'])
#
#         profit_price = round(buying_price * 0.99, 2)
#         stop_price = round(buying_price * 1.01, 2)
#
#         exit_order = client.futures_create_order(
#             symbol='ETHUSDT',
#             side='BUY',
#             closePosition=True,
#             type='TAKE_PROFIT_MARKET',
#             timeInForce='GTC',
#             stopPrice=profit_price,
#             quantity=qty)
#
#         place_new_order = client.futures_create_order(
#             symbol='ETHUSDT',
#             side='BUY',
#             type='STOP_MARKET',
#             timeInForce='GTC',
#             closePosition='true',
#             stopPrice=stop_price,
#             quantity=qty)
#
#     else:
#         orders.append('none')
#
#     while True:
#         if orders[-1] != 'none':
#             while True:
#                 close_l = df_eth['Close'][-1]
#
#                 open_orders = client.futures_get_open_orders(symbol='ETHUSDT')
#
#                 if orders[-1] == 'buy' and strategy(df_ha_eth, close_last, high, low, close) == 'sell' and len(open_orders)!=0:
#                     print('stoploss triggered')
#                     place_new_order = client.futures_create_order(
#                         symbol='ETHUSDT',
#                         side='SELL',
#                         type='STOP_MARKET',
#                         timeInForce='GTC',
#                         closePosition='true',
#                         stopPrice=round(close_l)-2,
#                         quantity=qty)
#                     break
#
#
#                 elif orders[-1] == 'sell' and strategy(df_ha_eth, close_last, high, low, close) == 'buy' and len(open_orders) != 0:
#                     print('stoploss triggered')
#                     place_new_order = client.futures_create_order(
#                         symbol='ETHUSDT',
#                         side='BUY',
#                         type='STOP_MARKET',
#                         timeInForce='GTC',
#                         closePosition='true',
#                         stopPrice=round(close_l)+2,
#                         quantity=qty)
#                     break
#
#             while True:
#                 open_orders = client.futures_get_open_orders(symbol='ETHUSDT')
#                 if len(open_orders) < 3:
#                     cancel_open_orders = client.futures_cancel_all_open_orders(symbol='ETHUSDT')
#                     break
#
#         else:
#             break