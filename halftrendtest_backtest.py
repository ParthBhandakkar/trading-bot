import numpy as np
import pandas as pd
import json
import requests
import datetime as dt
from datetime import datetime
from binance.client import Client
import warnings

warnings.filterwarnings('ignore')

client = Client("ZOwAm0l1XLQxvDaHGwnsVyUSGuhNqKMAJwqyXmJdCbWmpPFKfwxltuOIJK5UZY3X",
                "Q07zJXytFZMPiTrt5D2oKlvqmyEsn5deizijvwGqto1P8RzAXguD2go05fqWlzmA", {"verify": False, "timeout": 20})

def get_adx(High, Low, Close, lookback):
    plus_dm = High.diff()
    minus_dm = Low.diff()
    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm > 0] = 0

    tr1 = pd.DataFrame(High - Low)
    tr2 = pd.DataFrame(abs(High - Close.shift(1)))
    tr3 = pd.DataFrame(abs(Low - Close.shift(1)))
    frames = [tr1, tr2, tr3]
    tr = pd.concat(frames, axis=1, join='inner').max(axis=1)
    atr = tr.rolling(lookback).mean()

    plus_di = 100 * (plus_dm.ewm(alpha=1 / lookback).mean() / atr)
    minus_di = abs(100 * (minus_dm.ewm(alpha=1 / lookback).mean() / atr))
    dx = (abs(plus_di - minus_di) / abs(plus_di + minus_di)) * 100
    adx = ((dx.shift(1) * (lookback - 1)) + dx) / lookback
    adx_smooth = adx.ewm(alpha=1 / lookback).mean()
    return plus_di, minus_di, adx_smooth


def sma(source, length):
    sma_out = source.rolling(length).mean()
    return sma_out

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

    df1['closetime'] = [dt.datetime.fromtimestamp(x / 1000.0) for x in df1.close_time]
    df1.reset_index(inplace=True)
    return df1

now = datetime.now()
_get_historical_data_('SOLUSDT', '15m', '1500')
df = df1
df = df.iloc[:-1,:]


df['highma'] = sma(df['High'], 2)
df['lowma'] = sma(df['Low'], 2)
df['nextTrend'] = 0
df['trend'] = 0
df['up'] = 0
df['down'] = 0

df['maxLowPrice'] = df['Low'].shift(1)
df['minHighPrice'] = df['High'].shift(1)

df['plus_di'] = get_adx(df['High'], df['Low'], df['Close'], 14)[0]
df['minus_di'] = get_adx(df['High'], df['Low'], df['Close'], 14)[1]
df['adx'] = get_adx(df['High'], df['Low'], df['Close'], 14)[2]
df = df.dropna()

# last_plus_di = plus_di[-2]
# second_last_plus_di = plus_di[-3]
# last_minus_di = minus_di[-2]
# second_last_minus_di = minus_di[-3]
# last_adx = adx[-2]

df['color'] = 1
df['action'] = 0 # 0 = do nothing, 1 = buy, 2 = sell

for i in df.index:

    if i > 14:

        # if df['nextTrend'][i-1] == 1:
        #     print('inside 1st if loop')
        #     df['maxLowPrice'][i] = max(df['low'][i-2], df['low'][i-1], df['low'][i])
        #
        #     if df['highma'][i] < df['maxLowPrice'][i] and df['close'][i] < df['low'][i-1]:
        #         print('inside 1st if loop then if subloop')
        #         df['trend'][i] = 1
        #         df['nextTrend'][i] = 0
        #         df['minHighPrice'][i] = max(df['high'][i-2], df['high'][i-1], df['high'][i])
        #
        # else:
        #     print('inside 1st else loop')
        #     df['minHighPrice'][i] = min(df['high'][i-2], df['high'][i-1], df['high'][i])
        #
        #     if df['lowma'][i] > df['minHighPrice'][i] and df['close'][i] > df['high'][i-1]:
        #         print('inside 1st else loop then if subloop')
        #         df['trend'][i] = 0
        #         df['nextTrend'][i] = 1
        #         df['maxLowPrice'][i] = min(df['low'][i-2], df['low'][i-1], df['low'][i])

        # if df['trend'][i] == 0:
        #     print('inside 2nd if loop')
        #     if df['trend'][i-1] and df['trend'][i-1] != 0:
        #         print('inside 2nd if loop then if subloop')
        #         df['up'][i] = df['down'][i-1] if df['down'][i-1] else df['down'][i-1]
        #     else:
        #         print('inside 2nd if loop then else subloop')
        #         df['up'][i] = max(df['low'][i], df['up'][i-1]) if df['up'][i-1] else df['low'][i]
        #
        # else:
        #     print('inside 2nd else loop')
        #     if df['trend'][i-1] and df['trend'][i-1] != 1:
        #         print('inside 2nd else loop then if subloop')
        #         df['down'][i] = df['up'][i-1] if df['up'][i-1] else df['up'][i]
        #     else:
        #         print('inside 2nd else loop then else subloop')
        #         df['down'][i] = min(df['high'][i], df['down'][i-1]) if df['down'][i-1] else df['high'][i]

        if df['color'][i-1] == 2:
            if df['Close'][i] > df['highma'][i]:
                df['color'][i] = 1
            else:
                df['color'][i] = 2
        elif df['color'][i-1] == 1:
            if df['Close'][i] < df['lowma'][i]:
                df['color'][i] = 2
            else:
                df['color'][i] = 1
        # ht = df['up'][i] if df['trend'][i] == 0 else df['down'][i]
        # print(df.index[i], df['color'][i])
        if df['color'][i] == 1 and df['adx'][i] > 23.5 and df['plus_di'][i] > df['minus_di'][i]:
            df['action'][i] = 1
            # print(df['action'][i])
        elif df['color'][i] == 2 and df['adx'][i] > 23.5 and df['minus_di'][i] > df['plus_di'][i]:
            df['action'][i] = 2
            # print(df['action'][i])
        else:
            df['action'][i] = 0
            # print(df['action'][i])

    else:
        pass

# print(df['action'])
# print((type(df.action)))
indicol = [None] # 1 = buy, 2 = sell

def ACT():
    return df.action

def ACT2():
    return df.color


from backtesting import Strategy

class MyCandlesStrat(Strategy):
    def init(self):
        super().init()
        self.signal1 = self.I(ACT)
        self.color1 = self.I(ACT2)


    def next(self):
        super().next()

        if self.color1 == 2 and indicol[-1] == 'buy':
            self.position.close()

        elif self.color1 == 1 and indicol[-1] == 'sell':
            self.position.close()

        if self.signal1 == 1:
            indicol.append('buy')
            self.buy()

        elif self.signal1 == 2:
            indicol.append('sell')
            self.sell()

from backtesting import Backtest



bt = Backtest(df, MyCandlesStrat, cash=100, commission=.004)
stat = bt.run()
print(stat)

bt.plot(plot_volume=False, plot_pl=False)
