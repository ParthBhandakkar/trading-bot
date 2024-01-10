import pandas as pd
import json
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


def ichi_moku(df):
    tenkan_max = df['High'].rolling(window = 9, min_periods = 0).max()
    tenkan_min = df['Low'].rolling(window = 9, min_periods = 0).min()
    df['tenkan_avg'] = (tenkan_max + tenkan_min) / 2

    kijun_max = df['High'].rolling(window = 26, min_periods = 0).max()
    kijun_min = df['Low'].rolling(window = 26, min_periods = 0).min()
    df['kijun_avg'] = (kijun_max + kijun_min) / 2

    df['senkou_a'] = ((df['kijun_avg'] + df['tenkan_avg']) / 2) #yellow

    senkou_b_max = df['High'].rolling(window = 52, min_periods = 0).max()
    senkou_b_min = df['Low'].rolling(window = 52, min_periods = 0).min()
    df['senkou_b'] = ((senkou_b_max + senkou_b_min) / 2) #pink

    df['chikou'] = (df['Close'].tail(26)) #dark green

    blue_list = df['tenkan_avg'].tolist()
    blue_last = blue_list[-1]
    blue_second_last = blue_list[-2]
    red_list = df['kijun_avg'].tolist()
    red_last = red_list[-1]
    red_second_last = red_list[-2]
    green_list = df['chikou'].tolist()
    green_last = green_list[-1]
    yellow_list = df['senkou_a'].tolist()
    yellow_last = yellow_list[-1]
    pink_list = df['senkou_b'].tolist()
    pink_last = pink_list[-1]
    close_list = df['Close'].tolist()
    close_last = close_list[-1]

    if close_last > yellow_last and close_last > pink_last and blue_last > red_last and blue_second_last <= red_second_last :
        return'buy'
    elif close_last < yellow_last and close_last < pink_last and blue_last < red_last and blue_second_last >= red_second_last:
        return'sell'
    else :
        return'no'

actions = ['hold']
orders = []

while True:
    now = datetime.now()
    df_eth = _get_historical_data_('ETHUSDT', '15m', '150')
    df_sol = _get_historical_data_('SOLUSDT', '15m', '150')
    df_avax = _get_historical_data_('AVAXUSDT', '15m', '150')
    df_ltc = _get_historical_data_('LTCUSDT', '15m', '150')
    df_xrp = _get_historical_data_('XRPUSDT', '15m', '150')

    if ichi_moku(df_eth) == 'buy':
        action = 'buy'
        actions.append(action)
        print(now)
        print(action)
        print(actions[-1])
        print("------------------------------------------")
    elif ichi_moku(df_eth) == 'sell':
        action = 'sell'
        actions.append(action)
        print(actions[-1])
        print(now)
        print(action)
        print("------------------------------------------")

    else:
        action = 'hold'
        actions.append(action)
        # print(ichi_moku(df_eth))

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

                if orders[-1] == 'buy' and ichi_moku(df_eth) == 'sell' and len(open_orders)!=0:
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


                elif orders[-1] == 'sell' and ichi_moku(df_eth) == 'buy' and len(open_orders) != 0:
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