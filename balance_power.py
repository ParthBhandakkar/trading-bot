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
class BP:

    __version__ = "1.3"


    @classmethod
    def TP(cls, ohlc: DataFrame) -> Series:

        return pd.Series((ohlc["high"] + ohlc["low"] + ohlc["close"]) / 3, name="TP")

    @classmethod
    def BOP(cls, ohlc: DataFrame) -> Series:
        while True:
            bop_series = pd.Series(
                (ohlc.close - ohlc.open) / (ohlc.high - ohlc.low), name="Balance Of Power"
            )
            bop_list = bop_series.tolist()
            last_value = bop_list[-1]
            second_last_value = bop_list[-2]
            close_list = df['Close'].tolist()
            close_last_value = close_list[-1]
            if last_value > 0 and last_value > second_last_value:
                return'buy'
                break
            elif last_value < 0 and last_value < second_last_value:
                return'sell'
                break
            else :
                return'no'
                break
    


