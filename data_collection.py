import pandas as pd
from datetime import date, datetime, timedelta
from binance.client import Client
import warnings
warnings.filterwarnings('ignore')
# ZOwAm0l1XLQxvDaHGwnsVyUSGuhNqKMAJwqyXmJdCbWmpPFKfwxltuOIJK5UZY3X
# Q07zJXytFZMPiTrt5D2oKlvqmyEsn5deizijvwGqto1P8RzAXguD2go05fqWlzmA
client = Client("ZAngNhJLz6LgWDKF7ScESANv7QHv75yw08hflTAXRiZsri8G55Kgxt8F9B6zAVfd",
                '2nOHml8qdiZQ6Iy8d88bWCS837Pwc9Kr0q6COvTfAAjg5WC6z5IUDIUtoqtzIpzK', {"verify": False, "timeout": 20})

start_date = datetime(2021,5,14)
end_date = datetime(2022,11,24)
lst = []

def get_dates(open_date, close_date):
    delta = close_date - open_date  # as timedelta
    days = [open_date + timedelta(days=i) for i in range(delta.days + 1)]
    for i in days:
        d = i.strftime("%d %B, %Y")
        lst.append(d)
    print(lst)
get_dates(start_date, end_date)
length = len(lst)
print(length)
n=0
df = pd.DataFrame()

while n < length-1:
    date_initial = lst[n]
    date_final = lst[n+1]
    klines = client.get_historical_klines("ETHUSDT", Client.KLINE_INTERVAL_30MINUTE, date_initial, date_final)
    print(klines)
    df1 = pd.DataFrame(klines, columns=['open_time',
                                       'Open', 'High', 'Low', 'Close', 'Volume',
                                       'close_time', 'qav', 'num_trades',
                                       'taker_base_vol', 'taker_quote_vol', 'ignore'])

    df = df.append(df1)
    print(n)
    n=n+1

print(df)
df.to_csv('data_eth_30min.csv')
