# -*- coding: utf-8 -*-
from pandas_ta.overlap import ma
from pandas_ta.utils import get_offset, verify_series
import binance_api

df = binance_api.df
close = df['Close']

def bias(close, length=None, mamode=None, offset=None, **kwargs):
    while True:
        # Validate Arguments
        length = int(length) if length and length > 0 else 26
        mamode = mamode if isinstance(mamode, str) else "sma"
        close = verify_series(close, length)
        offset = get_offset(offset)

        if close is None: return

        # Calculate Result
        bma = ma(mamode, close, length=length, **kwargs)
        bias = (close / bma) - 1

        # Offset
        if offset != 0:
            bias = bias.shift(offset)

        # Handle fills
        if "fillna" in kwargs:
            bias.fillna(kwargs["fillna"], inplace=True)
        if "fill_method" in kwargs:
            bias.fillna(method=kwargs["fill_method"], inplace=True)

        # Name and Categorize it
        bias.name = f"BIAS_{bma.name}"
        bias.category = "momentum"

        bias_list = bias.to_list()
        close_list = df['Close'].to_list()
        open_list = df['Open'].to_list() 
        last_close = close_list[-1]
        second_last_close = close_list[-2]
        last_open = open_list[-1]
        second_last_open = open_list[-2]
        last_value = bias_list[-1]
        second_last_value = bias_list[-2]

        if last_value > 0 and last_value > second_last_value:
            return'buy'
            break
        elif last_value < 0 and last_value < second_last_value:
            return'sell'
            break
        else :
            return'no'
            break


