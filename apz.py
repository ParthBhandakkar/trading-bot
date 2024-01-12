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
class TA:
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
    __version__ = "1.3"
    @classmethod
    def DEMA(
        cls,
        ohlc: DataFrame,
        period: int = 9,
        column: str = "close",
        adjust: bool = True,
    ) -> Series:

        DEMA = (
            2 * cls.EMA(ohlc, period)
            - cls.EMA(ohlc, period).ewm(span=period, adjust=adjust).mean()
        )

        return pd.Series(DEMA, name="{0} period DEMA".format(period))
    @classmethod
    def APZ(
        cls,
        ohlc: DataFrame,
        period: int = 21,
        dev_factor: int = 2,
        MA: Series = None,
        adjust: bool = True,
    ) -> DataFrame:
        while True:
            if not isinstance(MA, pd.Series):
                MA = cls.DEMA(ohlc, period)
            price_range = pd.Series(
                (ohlc["high"] - ohlc["low"]).ewm(span=period, adjust=adjust).mean()
            )
            volatility_value = pd.Series(
                price_range.ewm(span=period, adjust=adjust).mean(), name="vol_val"
            )

            # upper_band = dev_factor * volatility_value + dema
            upper_band = pd.Series((volatility_value * dev_factor) + MA, name="UPPER")
            lower_band = pd.Series(MA - (volatility_value * dev_factor), name="LOWER")
            middle_band = (upper_band + lower_band)/2

            upper_list = upper_band.to_list()
            lower_list = lower_band.to_list()
            middle_list = middle_band.to_list()
            close_list = df['Close'].to_list()
            open_list = df['Open'].to_list() 
            last_close = close_list[-1]
            second_last_close = close_list[-2]
            last_open = open_list[-1]
            second_last_open = open_list[-2]
            last_value_upper = upper_list[-1]
            last_value_lower = lower_list[-1]
            last_value_middle = middle_list[-1]

            if last_close > last_value_middle and last_close > second_last_close :
                return'buy'
                break
            elif last_close < last_value_middle and last_close < second_last_close:
                return'sell'
                break
            else :
                return'no'
                break
