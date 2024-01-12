from numpy import dtype
import numpy as np
import os
from binance.client import Client
import pandas as pd
import binance_api
import requests
import matplotlib.pyplot as plt
from math import floor

def aroon_indicator():
    while True:
        df = binance_api.df

        def aroon(df):
            df1 = df.copy()
            df1['aroon_up'] = 100 * df1.High.rolling(14 + 1).apply(lambda x: x.argmax()) / 14
            df1['aroon_down'] = 100 * df1.Low.rolling(14 + 1).apply(lambda x: x.argmin()) / 14
            df1['aroon_osc'] = df1['aroon_up'] - df1['aroon_down']
            return df1

        df = aroon(df)

        # aroon trading strategy
        def implement_aroon_strategy(prices, up, down):
            buy_price = []
            sell_price = []
            aroon_signal = []
            signal = 0
        
            for i in range(len(prices)):
                if up[i] >= 70 and down[i] <= 30:
                    if signal != 1:
                        buy_price.append(prices[i])
                        sell_price.append(np.nan)
                        signal = 1
                        aroon_signal.append(signal)
                    else:
                        buy_price.append(np.nan)
                        sell_price.append(np.nan)
                        aroon_signal.append(0)
                elif up[i] <= 30 and down[i] >= 70:
                    if signal != -1:
                        buy_price.append(np.nan)
                        sell_price.append(prices[i])
                        signal = -1
                        aroon_signal.append(signal)
                    else:
                        buy_price.append(np.nan)
                        sell_price.append(np.nan)
                        aroon_signal.append(0)
                else:
                    buy_price.append(np.nan)
                    sell_price.append(np.nan)
                    aroon_signal.append(0)
                
            return buy_price, sell_price, aroon_signal

        buy_price, sell_price, aroon_signal = implement_aroon_strategy(df['Close'], df['aroon_up'], df['aroon_down'])

        position = []
        for i in range(len(aroon_signal)):
            if aroon_signal[i] > 1:
                position.append(0)
            else:
                position.append(1)
            
        for i in range(len(df['Close'])):
            if aroon_signal[i] == 1:
                position[i] = 1
            elif aroon_signal[i] == -1:
                position[i] = 0
            else:
                position[i] = position[i-1]
            
        aroon_up = df['aroon_up']
        aroon_down = df['aroon_down']
        close_price = df['Close']
        aroon_signal = pd.DataFrame(aroon_signal).rename(columns = {0:'aroon_signal'}).set_index(df.index)
        position = pd.DataFrame(position).rename(columns = {0:'aroon_position'}).set_index(df.index)

        frames = [close_price, aroon_up, aroon_down, aroon_signal, position]
        strategy = pd.concat(frames, join = 'inner', axis = 1)

        aroon_up_lst = df['aroon_up'].to_list()
        aroon_down_lst = df['aroon_down'].to_list()
        last_value_up = aroon_up_lst[-1]
        last_value_down = aroon_down_lst[-1]
        close_list = df['Close'].to_list()
        open_list = df['Open'].to_list() 
        last_close = close_list[-1]
        second_last_close = close_list[-2]
        last_open = open_list[-1]
        second_last_open = open_list[-2]
        if last_value_up> 70 and last_value_down < 30 :
            return'buy'
            break
        elif last_value_down > 70 :
            return'sell'
            break
        else:
            return'no'
            break

