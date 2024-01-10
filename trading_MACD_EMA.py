import pandas as pd
import json
import requests
import datetime as dt
from binance.client import Client
import warnings
import smtplib
from datetime import datetime

warnings.filterwarnings('ignore')

client = Client("bCsWxIe0jq0hOfxGFA1PdoyKVIKSeVFT5SaBsJLrgzeye1BqkZLtBcD5G1eFZ3go",
                "PaFCwdgnvhohwllwzoCr1iZQqLdrUDmgD1FDOvM2gMSVbrOKQ8I7FLcgSjtV668d", {"verify": False, "timeout": 20})

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


def heikin_ashi(df):
    heikin_ashi_df = df.copy()
    # heikin_ashi_df = pd.DataFrame(index=df.index.values, columns=['open', 'high', 'low', 'close'])
    heikin_ashi_df['Close'] = (df['Open'] + df['High'] + df['Low'] + df['Close']) / 4

    for i in range(len(df)):
        if i == 0:
            heikin_ashi_df.iat[0, 0] = df['Open'].iloc[0]
        else:
            heikin_ashi_df.iat[i, 0] = (heikin_ashi_df.iat[i - 1, 0] + heikin_ashi_df.iat[i - 1, 3]) / 2

    heikin_ashi_df['High'] = heikin_ashi_df.loc[:, ['Open', 'Close']].join(df['High']).max(axis=1)

    heikin_ashi_df['Low'] = heikin_ashi_df.loc[:, ['Open', 'Close']].join(df['Low']).min(axis=1)

    return heikin_ashi_df


def ma_cd(df):
    exp1 = df['Close'].ewm(span=55, adjust=False).mean()
    exp2 = df['Close'].ewm(span=100, adjust=False).mean()
    macd = exp1 - exp2
    exp3 = macd.ewm(span=9, adjust=False).mean()
    hist = macd - exp3
    return hist

def ema_200(df):
    exp_200 = df['Close'].ewm(span=200, adjust=False).mean()
    return exp_200[-1]

def ema_cross(df):
    exp_12 = df['Close'].ewm(span=12, adjust=False).mean()
    exp_25 = df['Close'].ewm(span=25, adjust=False).mean()
    if exp_12[-1] > exp_25[-1]:
        return 'buy'
    elif exp_25[-1] > exp_12[-1]:
        return 'sell'
    else:
        return 'none'


def strategy(df, close_last, high, low, close):
    if close_last > ema_200(df) and ema_cross(df) == 'buy' and ma_cd(df)[-1] > 0:
        return'buy'
    elif close_last < ema_200(df) and ema_cross(df) == 'sell' and ma_cd(df)[-1] < 0:
        return'sell'
    else:
        return'no'

actions = ['hold']
orders = []

while True:
    now = datetime.now()
    df_eth = _get_historical_data_('ETHUSDT', '1h', '150')
    df_ha_eth = heikin_ashi(df_eth)
    close_ = df_ha_eth['Close']
    close_list = df_ha_eth['Close'].to_list()
    high_ = df_ha_eth["High"].to_list()
    low_ = df_ha_eth['Low'].to_list()
    close_last = close_list[-1]

    if strategy(df_ha_eth, close_last, high_, low_, close_) == 'buy':
        action = 'buy'
        actions.append(action)

        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login("bhandakkarparth@gmail.com", "Sayonaria2$")
        message = "BUY"
        s.sendmail("bhandakkarparth@gmail.com", "bhandakkarparth@gmail.com", message)

        # terminating the session
        s.quit()
        print(now)
        print(action)
        print(actions[-1])
        print("------------------------------------------")
        print(ma_cd(df_ha_eth)[-1], ema_cross(df_ha_eth), close_last)
    elif strategy(df_ha_eth, close_last, high_, low_, close_) == 'sell':
        action = 'sell'
        actions.append(action)
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login("bhandakkarparth@gmail.com", "Sayonaria2$")
        message = "SELL"
        s.sendmail("bhandakkarparth@gmail.com", "bhandakkarparth@gmail.com", message)
        print(actions[-1])
        print(now)
        print(action)
        print("------------------------------------------")
        print(ma_cd(df_ha_eth)[-1], ema_cross(df_ha_eth), close_last)


    else:
        action = 'hold'
        actions.append(action)
        print(ma_cd(df_ha_eth)[-1], ema_cross(df_ha_eth), close_last, ema_200(df_eth))

    account = client.futures_account_balance()
    for i in range(len(account)):
        if account[i].get('asset') == 'USDT':
            usdtbal = float(account[i].get('balance'))

    prices = client.get_all_tickers()
    for i in prices:
        for j in i:
            if j == "symbol":
                if i.get('symbol') == 'ETHUSDT':
                    ETH_price = float(i.get('price'))

    quantity_taken = int(usdtbal * 30 / ETH_price)
    leverage_taken = client.futures_change_leverage(symbol="ETHUSDT", leverage=30)

    if action == 'buy' and actions[-2] != 'buy':
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

    elif action == 'sell' and actions[-2] != 'sell':
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
                close_l = df_eth['Close'][-1]

                open_orders = client.futures_get_open_orders(symbol='ETHUSDT')

                if orders[-1] == 'buy' and strategy(df_ha_eth, close_last, high_, low_, close_) == 'sell' and len(open_orders)!=0:
                    print('stoploss triggered')
                    place_new_order = client.futures_create_order(
                        symbol='ETHUSDT',
                        side='SELL',
                        type='STOP_MARKET',
                        timeInForce='GTC',
                        closePosition='true',
                        stopPrice=round(close_l)-2,
                        quantity=qty)
                    break


                elif orders[-1] == 'sell' and strategy(df_ha_eth, close_last, high_, low_, close_) == 'buy' and len(open_orders) != 0:
                    print('stoploss triggered')
                    place_new_order = client.futures_create_order(
                        symbol='ETHUSDT',
                        side='BUY',
                        type='STOP_MARKET',
                        timeInForce='GTC',
                        closePosition='true',
                        stopPrice=round(close_l)+2,
                        quantity=qty)
                    break

            while True:
                open_orders = client.futures_get_open_orders(symbol='ETHUSDT')
                if len(open_orders) < 3:
                    cancel_open_orders = client.futures_cancel_all_open_orders(symbol='ETHUSDT')
                    break

        else:
            break