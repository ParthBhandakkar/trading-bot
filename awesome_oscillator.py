from pandas.core.frame import DataFrame
import pandas as pd
import openpyxl
from datetime import datetime
import config
import os
import numpy as np
from binance.client import Client
import csv
import binance_api
from functools import wraps
import pandas as pd
import numpy as np
from pandas import DataFrame, Series

df = binance_api.df

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
class AWO:

    __version__ = "1.3"


    @classmethod
    def TP(cls, ohlc: DataFrame) -> Series:

        return pd.Series((ohlc["high"] + ohlc["low"] + ohlc["close"]) / 3, name="TP")
    
    @classmethod
    def AO(cls, ohlc: DataFrame, slow_period: int = 34, fast_period: int = 5) -> Series:
        while True:
            slow = pd.Series(
                ((ohlc["high"] + ohlc["low"]) / 2).rolling(window=slow_period).mean(),
                name="slow_AO",
            )
            fast = pd.Series(
                ((ohlc["high"] + ohlc["low"]) / 2).rolling(window=fast_period).mean(),
                name="fast_AO",
            )

            ao_series = pd.Series(fast - slow, name="AO")
            ao_list = ao_series.to_list()
            ao_last = ao_list[-1]
            ao_second_last = ao_list[-2]
            close_list = df['Close'].to_list()
            open_list = df['Open'].to_list() 
            last_close = close_list[-1]
            second_last_close = close_list[-2]
            last_open = open_list[-1]
            second_last_open = open_list[-2]

            if ao_last > 0 and ao_last > ao_second_last:
                return'buy'
                break
            elif ao_last < 0 and ao_last < ao_second_last:
                return'sell'
                break
            else:
                return'no'
                break

