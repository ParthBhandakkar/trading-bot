from pandas.core.frame import DataFrame
import pandas as pd
import datetime as dt
import config
import os
import numpy as np
import requests
import json
import csv
from functools import wraps
import pandas as pd
import numpy as np
from pandas import DataFrame, Series

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

_get_historical_data_('SOLUSDT', '1m', '210')
df = df1
open_ = df['Open']
high = df['High']
low = df['Low']
close = df['Close']
volume = df['Volume']
cls = df['Close']
close = df['Close']
def inputvalidator( input_="ohlc" ):
    def dfcheck(func):
        @wraps(func)
        def wrap(*args, **kwargs):

            args = list(args)
            i = 0 if isinstance(args[0], pd.DataFrame) else 1

            args[i] = args[i].rename(columns={c: c.lower() for c in args[i].columns})

            inputs = {
                "o": "open",
                "h": "high",
                "l": "low",
                "c": kwargs.get("column", "close").lower(),
                "v": "volume",
            }

            if inputs["c"] != "close":
                kwargs["column"] = inputs["c"]

            for l in input_:
                if inputs[l] not in args[i].columns:
                    raise LookupError(
                        'Must have a dataframe column named "{0}"'.format(inputs[l])
                    )

            return func(*args, **kwargs)

        return wrap

    return dfcheck


def apply(decorator):
    def decorate(cls):
        for attr in cls.__dict__:
            if callable(getattr(cls, attr)):
                setattr(cls, attr, decorator(getattr(cls, attr)))

        return cls

    return decorate

@apply(inputvalidator(input_="ohlc"))
class BBP:

    __version__ = "1.3"

    @classmethod
    def EMA(
        cls,
        ohlc: DataFrame,
        period: int = 9,
        column: str = "close",
        adjust: bool = True,
    ) -> Series:

        return pd.Series(
            ohlc[column].ewm(span=period, adjust=adjust).mean(),
            name="{0} period EMA".format(period),
        )

    """find trend using ema"""
    """if up -> bear power < 0 but rising"""
    """if down -> bull power > 0 but declining"""
    @classmethod
    def EBBP(cls, ohlc: DataFrame) -> DataFrame:
        while True:
            bull_power = pd.Series(ohlc["high"] - cls.EMA(ohlc, 13), name="Bull.")
            bear_power = pd.Series(ohlc["low"] - cls.EMA(ohlc, 13), name="Bear.")
            bbp_series = bull_power + bear_power

            bbp_list = bbp_series.to_list()
            bull_list = bull_power.to_list()
            bear_list = bear_power.to_list()
            close_list = df['Close'].to_list()
            open_list = df['Open'].to_list()
            last_close = close_list[-1]
            second_last_close = close_list[-2]
            last_open = open_list[-1]
            second_last_open = open_list[-2]
            last_value = bbp_list[-1]
            last_value_bull = bull_list[-1]
            last_value_bear = bear_list[-1]
            second_last_value = bbp_list[-2]
            second_last_value_bull = bull_list[-2]
            second_last_value_bear = bear_list[-2]


            ema_200 = df.Close.ewm(span=200, adjust=False).mean()
            df['200ema'] = ema_200

            ema200_list = df['ema200'].tolist()
            last_value_200 = ema200_list[-1]

            if last_close > last_value_200 and last_value_bear < 0 and last_value_bear > second_last_value_bear:
                return 'buy'
                break
            elif last_close < last_value_200 and last_value_bull > 0 and last_value_bull < second_last_value_bull:
                return 'sell'
                break
            else:
                return 'no'
                break

BBP.EBBP(df)



