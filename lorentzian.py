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

def lorentzian_transform(close, window_size):
    # Calculate the Lorentzian transform
    return np.exp(-(close - np.mean(close)) ** 2 / (2 * window_size ** 2))

def buy_signal(close, lorentzian_transform):
    # Check if the Lorentzian transform is greater than a certain threshold
    if lorentzian_transform > 0.5:
        return True
    else:
        return False

def sell_signal(close, lorentzian_transform):
    # Check if the Lorentzian transform is less than a certain threshold
    if lorentzian_transform < 0.5:
        return True
    else:
        return False

def main():
    df = _get_historical_data_('ETHUSDT', '1h', '1500')

    # Calculate the Lorentzian transform
    transform = lorentzian_transform(df['Close'], 20)

    # Create a list of buy signals
    buy_signals = []

    # Create a list of sell signals
    sell_signals = []

    # Loop through the data
    for i in range(len(df)):
        # Check for a buy signal
        if buy_signal(df['Close'][i], transform[i]):
            buy_signals.append(i)

        # Check for a sell signal
        if sell_signal(df['Close'][i], transform[i]):
            sell_signals.append(i)

    # Create a DataFrame of the signals
    # signals = pd.DataFrame({
    #     'buy': buy_signals,
    #     'sell': sell_signals
    # })

    # Print the results
    # print('Buy signals:', signals['buy'])
    # print('Sell signals:', signals['sell'])
    print(sell_signals)
    print(buy_signals)
if __name__ == '__main__':
    main()
