import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests
import pandas as pd
import json
import datetime as dt
from datetime import datetime
from binance.client import Client
# from binance.enums import *
import warnings
warnings.filterwarnings('ignore')

client = Client("65f762d96597cbc34d09cd1f206772b70531fd0deb62d374456dfaaafbf2befa",
                "199333bf2a9a8326633f103162418e9b8ee7e8a5f9df921ab3b0e08051cbd142", {"verify": False, "timeout": 20})

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


def smart_money_strategy(crypto, timeframe):
    """
    This function implements a smart money trading strategy for the given cryptocurrency and timeframe.

    Args:
        crypto (str): The name of the cryptocurrency.
        timeframe (str): The timeframe of the data to use.

    Returns:
        pd.DataFrame: A DataFrame containing the results of the trading strategy.
    """

    # Load the historical data for the cryptocurrency.
    prices = pd.read_csv(f"data/{crypto}.csv", index_col=0)

    # Calculate the moving average of the closing prices.
    moving_average = prices["close"].rolling(timeframe).mean()

    # Calculate the Bollinger Bands.
    bollinger_bands = prices["close"].rolling(timeframe).bollinger_bands(20, 2)

    # Identify the smart money signals.
    smart_money_signals = []
    for i in range(len(prices)):
        if bollinger_bands["upper"].iloc[i] < prices["close"].iloc[i] and bollinger_bands["lower"].iloc[i] > prices["close"].iloc[i]:
            smart_money_signals.append((prices["close"].iloc[i], prices["close"].iloc[i]))

    # Calculate the returns of the strategy.
    returns = pd.DataFrame(np.zeros((len(smart_money_signals), 2)), columns=["Entry", "Exit"])
    for i in range(len(smart_money_signals)):
        returns.iloc[i, 0] = smart_money_signals[i][0]
        returns.iloc[i, 1] = smart_money_signals[i][1]

    # Plot the results of the strategy.
    plt.plot(prices["close"])
    plt.plot(smart_money_signals)
    plt.show()

    return returns

if __name__ == "__main__":
    # Choose the cryptocurrency and timeframe.
    crypto = "ETH"
    timeframe = "1h"

    # Run the trading strategy.
    results = smart_money_strategy(crypto, timeframe)

    # Print the results.
    print(results)
