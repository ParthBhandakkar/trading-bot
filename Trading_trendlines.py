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
                "0ba00fab8eeb44fcccb7d0612e176422c258069ec4756ae5b0e778c77c639f07", {"verify": False, "timeout": 20}, testnet=True)

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

def sma(source, length):
    sma_out = source.rolling(length).mean()
    return sma_out

def rma(source, length):
    alpha = 1 / length
    rma_out = [NaN, 0]
    for i in range(length-1):
        rma_out.append(sma(source, length) if rma_out[-2] == float('nan') else (alpha * source[i]) + ((1 - alpha) * (0 if rma_out[-1] == float('nan') else rma_out[-1])))
    return rma_out

def atr(length, high, low, close):
    trueRange = [NaN, 0]
    for i in range(length-1):
        trueRange.append(
            high[i] - low[i] if high[i - 1] == float('nan') else max(max(high[i] - low[i], abs(high[i] - close[i - 1])),
                                                                     abs(low[i] - close[i - 1])))
    return rma(trueRange, length)
def pivothigh(src, length):
    pivothighs = []
    for i in range(length, len(df_eth.index)-14):
        bars = [src[i - 1], src[i - 2], src[i - 3], src[i - 4], src[i - 5], src[i - 6], src[i - 7], src[i - 8],src[i - 9], src[i - 10], src[i - 11], src[i - 12], src[i - 13], src[i - 14], src[i + 1], src[i + 2], src[i + 3], src[i + 4], src[i + 5], src[i + 6], src[i + 7], src[i + 8],src[i + 9], src[i + 10], src[i + 11], src[i + 12], src[i + 13], src[i + 14]]

        for items in bars :
            if src[i] > items:
                pivothighs.append(src[i])
    return pivothighs

def pivotlow(src, length):
    pivotlows = []
    for i in range(length, len(df_eth.index)-14):
        bars = [src[i - 1], src[i - 2], src[i - 3], src[i - 4], src[i - 5], src[i - 6], src[i - 7], src[i - 8],src[i - 9], src[i - 10], src[i - 11], src[i - 12], src[i - 13], src[i - 14], src[i + 1], src[i + 2], src[i + 3], src[i + 4], src[i + 5], src[i + 6], src[i + 7], src[i + 8],src[i + 9], src[i + 10], src[i + 11], src[i + 12], src[i + 13], src[i + 14]]

        for items in bars :
            if src[i] < items:
                pivotlows.append(src[i])
    return pivotlows

length = 14
k =1
upper = [0]
lower = [0]
slope_ph = [0]
slope_pl = [0]
single_upper = [0]
single_lower = [0]
def trendline(high_list, low_list, close_list):
    ph = pivothigh(high_list, length)
    pl = pivotlow(low_list, length)
    ATR = atr(length, high_list, low_list, close_list)[-1]/length*k
    slope_ph.append(ATR if ph else slope_ph[-2]) #check
    slope_pl.append(ATR if ph else slope_pl[-2]) #check

    upper.append(ph[-1] if ph else upper[-2] - slope_ph[-1])
    lower.append(pl[-1] if pl else lower[-2] + slope_pl[-1])

    single_upper.append(0 if close_list[-14] > upper[-1] else 1 if ph else single_upper[-2])
    single_lower.append(0 if close_list[-14] < lower[-1] else 1 if pl else single_lower[-2])

    upper_breakout = True if (single_upper[-1] and upper[-1] < close_list[-14] < close_list[-1]) else False
    lower_breakout = True if (single_lower[-1] and lower[-1] > close_list[-14] > close_list[-1]) else False
    if upper_breakout:
        return 'buy'
    elif lower_breakout:
        return 'sell'
    else:
        return 'notrade'

actions = ['hold']
orders = []

while True:
    now = datetime.now()
    df_eth = _get_historical_data_('ETHUSDT', '15m', '150')
    df_sol = _get_historical_data_('SOLUSDT', '15m', '150')
    df_avax = _get_historical_data_('AVAXUSDT', '15m', '150')
    df_ltc = _get_historical_data_('LTCUSDT', '15m', '150')
    df_xrp = _get_historical_data_('XRPUSDT', '15m', '150')

    high = df_eth['High']
    high_list = high.to_list()
    low = df_eth['Low']
    low_list = low.to_list()
    close = df_eth['Close']
    close_list = close.to_list()

    if trendline(high_list, low_list, close_list) == 'buy':
        action = 'buy'
        actions.append(action)
        print(now)
        print(action)
        print(actions[-1])
        print("------------------------------------------")
    elif trendline(high_list, low_list, close_list) == 'sell':
        action = 'sell'
        actions.append(action)
        print(actions[-1])
        print(now)
        print(action)
        print("------------------------------------------")

    else:
        action = 'hold'
        actions.append(action)


    account = client.futures_account_balance()

    for i in range(len(account)):
        if account[i].get('asset') == 'USDT':
            usdtbal = account[i].get('balance')

    prices = client.get_all_tickers()
    for i in prices:
        for j in i:
            if j == "symbol":
                if i.get('symbol') == 'ETHUSDT':
                    ETH_price = float(i.get('price'))

    quantity_taken = int(100 * 20 / ETH_price)
    leverage_taken = client.futures_change_leverage(symbol="ETHUSDT", leverage=20)

    if action == 'buy':
        orders.append('buy')
        print(orders[-1])

        place_new_order = client.futures_create_order(
            symbol='ETHUSDT',
            side='BUY',
            type='MARKET',
            quantity=quantity_taken)

        active_order = client.futures_get_all_orders(symbol='ETHUSDT')

        for i in active_order:
            for j in i:
                if i.get('reduceOnly') == False and i.get('status') == 'FILLED':
                    order_id = str(i.get('orderId'))

        current_order = client.futures_get_order(symbol='ETHUSDT', orderId=order_id)

        for i in current_order:
            qty = float(current_order['origQty'])
            buying_price = float(current_order['avgPrice'])

        profit_price = round(buying_price * 1.01, 2)
        stop_price = round(buying_price * 0.990, 2)

        exit_order = client.futures_create_order(
            symbol='ETHUSDT',
            side='SELL',
            closePosition=True,
            type='TAKE_PROFIT_MARKET',
            timeInForce='GTC',
            stopPrice=profit_price,
            quantity=qty)

        place_new_order = client.futures_create_order(
            symbol='ETHUSDT',
            side='SELL',
            type='STOP_MARKET',
            timeInForce='GTC',
            closePosition='true',
            stopPrice=stop_price,
            quantity=qty)

    elif action == 'sell':
        orders.append('sell')
        print(orders[-1])

        place_new_order = client.futures_create_order(
            symbol='ETHUSDT',
            side='SELL',
            type='MARKET',
            quantity=quantity_taken)


        active_order = client.futures_get_all_orders(symbol='ETHUSDT')

        for i in active_order:
            for j in i:
                if i.get('reduceOnly') == False and i.get('status') == 'FILLED':
                    order_id = str(i.get('orderId'))

        current_order = client.futures_get_order(symbol='ETHUSDT', orderId=order_id)

        for i in current_order:
            qty = float(current_order['origQty'])
            buying_price = float(current_order['avgPrice'])

        profit_price = round(buying_price * 0.99, 2)
        stop_price = round(buying_price * 1.01, 2)

        exit_order = client.futures_create_order(
            symbol='ETHUSDT',
            side='BUY',
            closePosition=True,
            type='TAKE_PROFIT_MARKET',
            timeInForce='GTC',
            stopPrice=profit_price,
            quantity=qty)

        place_new_order = client.futures_create_order(
            symbol='ETHUSDT',
            side='BUY',
            type='STOP_MARKET',
            timeInForce='GTC',
            closePosition='true',
            stopPrice=stop_price,
            quantity=qty)

    else:
        orders.append('none')

    while True:
        if orders[-1] != 'none':
            while True:
                close = df_eth['Close'][-1]

                open_orders = client.futures_get_open_orders(symbol='ETHUSDT')

                if orders[-1] == 'buy' and trendline(high_list, low_list, close_list) == 'sell' and len(open_orders)!=0:
                    print('stoploss triggered')
                    place_new_order = client.futures_create_order(
                        symbol='ETHUSDT',
                        side='SELL',
                        type='STOP_MARKET',
                        timeInForce='GTC',
                        closePosition='true',
                        stopPrice=round(close)-2,
                        quantity=qty)
                    break


                elif orders[-1] == 'sell' and trendline(high_list, low_list, close_list) == 'buy' and len(open_orders) != 0:
                    print('stoploss triggered')
                    place_new_order = client.futures_create_order(
                        symbol='ETHUSDT',
                        side='BUY',
                        type='STOP_MARKET',
                        timeInForce='GTC',
                        closePosition='true',
                        stopPrice=round(close)+2,
                        quantity=qty)
                    break

            while True:
                open_orders = client.futures_get_open_orders(symbol='ETHUSDT')
                if len(open_orders) < 3:
                    cancel_open_orders = client.futures_cancel_all_open_orders(symbol='ETHUSDT')
                    break

        else:
            break