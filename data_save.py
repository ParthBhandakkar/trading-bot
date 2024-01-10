import pandas as pd
from datetime import date, datetime, timedelta
from binance.client import Client
from binance.enums import *
import warnings
import os

warnings.filterwarnings('ignore')

client = Client("Wbb4LLfiqE8Ol4b7QEtb8TDhMNgnZSzrfg9Gv9bfJ5A0e6WWubFomE7GQVAuXK2W",
                "8NYzopp8hXPuCj5MPvlu0MpiTkPUPGpdbUTy84ce16iXWti3FnjGT1KiUrlqfFsm", {"verify": False, "timeout": 20})


today = date.isoformat(date.today())

start_date = datetime(int(today[0:4]), int(today[5:7]) - 2, 10)
end_date = datetime(int(today[0:4]), int(today[5:7]), int(today[8:10]))

timeinterval = [client.KLINE_INTERVAL_1MINUTE, client.KLINE_INTERVAL_3MINUTE, client.KLINE_INTERVAL_5MINUTE,
                client.KLINE_INTERVAL_15MINUTE, client.KLINE_INTERVAL_30MINUTE, client.KLINE_INTERVAL_1HOUR,
                client.KLINE_INTERVAL_2HOUR, client.KLINE_INTERVAL_4HOUR, client.KLINE_INTERVAL_6HOUR,
                client.KLINE_INTERVAL_8HOUR, client.KLINE_INTERVAL_12HOUR, client.KLINE_INTERVAL_1DAY,
                client.KLINE_INTERVAL_3DAY, client.KLINE_INTERVAL_1WEEK, client.KLINE_INTERVAL_1MONTH]

df_pair = pd.read_csv('D:\\VirtualEnvPy\\tradebot\\historical_data\\FuturesPairNames.csv', names=['PairName'])
symb_list = df_pair['PairName'].tolist()

print(len(symb_list))
print(symb_list)
print(len(timeinterval))
print(timeinterval)



for i in symb_list:

    for j in timeinterval:
        j = str(j)
        # Check whether the specified
        # path exists or not
        path = f'D:\\VirtualEnvPy\\tradebot\\historical_data\\FuturesData\\{i}_{j}_10{int(today[5:7]) - 2}{today[0:4]}_{today[8:10]}{today[5:7]}{today[0:4]}.csv' # 231219_201122
        isExist = os.path.exists(path)
        # print(isExist)

        if isExist == False:

            try:
                lst = []

                def get_dates(open_date, close_date):
                    delta = close_date - open_date  # as timedelta
                    days = [open_date + timedelta(days=i) for i in range(delta.days + 1)]
                    for i in days:
                        d = i.strftime("%d %B, %Y")
                        lst.append(d)
                    # print(lst)
                get_dates(start_date, end_date)
                length = len(lst)
                # print(length)
                n = 0
                df = pd.DataFrame()

                while n < length-1:
                    date_initial = lst[n]
                    date_final = lst[n+1]
                    klines = client.get_historical_klines(i, j, date_initial, date_final)
                    if klines == []:
                        n += 1
                        continue
                    else:
                        df1 = pd.DataFrame(klines, columns=['open_time',
                                                           'Open', 'High', 'Low', 'Close', 'Volume',
                                                           'close_time', 'qav', 'num_trades',
                                                           'taker_base_vol', 'taker_quote_vol', 'ignore'])

                        df = df.append(df1)
                        # print(n)
                        n += 1

                # print(df)
                df.to_csv(f'D:\\VirtualEnvPy\\tradebot\\historical_data\\FuturesData\\{i}_{j}_10{int(today[5:7]) - 2}{today[0:4]}_{today[8:10]}{today[5:7]}{today[0:4]}.csv')
                del df
                if j == '1w':
                    print(f'{i} data downloaded')


            except:
                print(f'-------------------{i}---invalid-------------------')
                if os.path.exists(f'D:\\VirtualEnvPy\\tradebot\\historical_data\\FuturesData\\{i}_{j}_10{int(today[5:7]) - 2}{today[0:4]}_{today[8:10]}{today[5:7]}{today[0:4]}.csv') == False:
                    break

        else:
            continue
print('Done')