import numpy as np
import pandas as pd
import json
import requests
import datetime as dt
from binance.client import Client
import warnings

warnings.filterwarnings('ignore')

client = Client("5696d835034796a2037af3cea642db784a5f3bf615c80e9f939438b648bca41c",
                "bb13daeb74730c7f5691e73fcb114b0a0fee98d9c9f62ca374a514133a364234", {"verify": False, "timeout": 20})

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
    df1['taker_base_vol'] = df1['taker_base_vol'].astype(float)

    df1['date'] = [dt.datetime.fromtimestamp(x / 1000.0) for x in df1.close_time]
    df1.reset_index(drop=True, inplace=True)
    return df1

_get_historical_data_('ETHUSDT', '1h', '1500')
df = df1
# df = df.iloc[:,:]



df['volsign'] = np.where(df['Close'] > df['Close'].shift(1), 1, -1)
df['highlow'] = (df['High'] - df['Low'])
df['pricerate'] = np.where(df['volsign'] > 0, df['highlow'] / df['Volume'] * 100, df['highlow'] / df['Volume'] * -100)# rate of change should be equal

df['O-H'] = (df['High'] - df['Open']) / df['Open'] * 100
df['O-L'] = (df['Open'] - df['Low']) / df['Open'] * 100

df['PerfCand'] = 0
_tp, _sl = 1.5, 1.0

for i in df.index:
    _profitB, _slB = _tp, _sl
    _open = df['Open'][i]
    j = 0
    while _profitB > 0 or _slB > 0:
        _profitB -= abs((df['High'][i+j] - _open) / _open * 100)
        _slB -= abs((_open - df['Low'][i+j]) / _open * 100)

        if i == len(df.index) - 1:
            break
        elif j >= 12 or i >= len(df.index) - 10:
            break
        elif _profitB <= 0 and _slB > 0:
            df['PerfCand'][i] = 1
            break
        elif _profitB > 0 and _slB <= 0:
            df['PerfCand'][i] = 0.5
            break
        _profitB, _slB = _tp, _sl
        j += 1
print(f"1 : {len(df[df['PerfCand'] == 1])} | 0.5 : {len(df[df['PerfCand'] == 0.5])}")

for i in df.index:
    if df['PerfCand'][i] == 0.5:
        _profitS, _slS = _tp, _sl
        _open = df['Open'][i]
        j = 0
        while _profitS > 0 or _slS > 0:
            _profitS -= abs((_open - df['Low'][i+j]) / _open * 100)
            _slS -= abs((df['High'][i+j] - _open) / _open * 100)

            if i == len(df.index) - 1:
                break
            elif j >= 12 or i >= len(df.index) - 10:
                break
            elif _profitS <= 0 and _slS > 0:
                df['PerfCand'][i] = -1
                break
            elif _profitS > 0 and _slS <= 0:
                df['PerfCand'][i] = -0.5
                break
            _profitS, _slS = _tp, _sl
            j += 1
    else:
        pass


print(f"-0.5 : {len(df[df['PerfCand'] == -0.5])} | 0.5 : {len(df[df['PerfCand'] == 0.5])} | 1 : {len(df[df['PerfCand'] == 1])} | -1 : {len(df[df['PerfCand'] == -1])} | \
0 : {len(df[df['PerfCand'] == 0])}")