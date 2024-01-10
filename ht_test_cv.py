import requests
import pandas as pd
import json
import datetime as dt
from datetime import datetime
from binance.client import Client
# from binance.enums import *
import warnings
warnings.filterwarnings('ignore')

client = Client("65f762d96597cbc34d09cd1f206772b70531fd0deb62d374456dfaaafbf2befa",
                "199333bf2a9a8326633f103162418e9b8ee7e8a5f9df921ab3b0e08051cbd142", {"verify": False, "timeout": 20})
# import time
# import cv2
# import numpy as np
# import pytesseract
# from PIL import Image
# import mss.tools
# pytesseract.pytesseract.tesseract_cmd = r'D:\AIMakesPossible\tesseract.exe'
# import pyautogui
# time.sleep(3)
# res = pyautogui.locateOnScreen("D:\\AIMakesPossible\Trading Bot\images\\value.png")
# print(res)

# ashutosh's pc -> Box(left=149, top=202, width=55, height=24)
# parth's pc -> Box(left=233, top=206, width=60, height=20)



# to capture speciiic area of the screen

ht_colors = []
actions = ['hold']
orders = []

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


print(_get_historical_data_('ETHUSDT', '1h', '1500'))
output = "D:\AIMakesPossible\Trading Bot\images"

# Path of working folder on Disk
src_path = output

def get_string(img_path):
    # Read image with opencv
    img = cv2.imread(img_path)

    # Convert to gray
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply dilation and erosion to remove some noise
    kernel = np.ones((1, 1), np.uint8)
    img = cv2.dilate(img, kernel, iterations=1)
    img = cv2.erode(img, kernel, iterations=1)

    # Write image after removed noise
    cv2.imwrite(src_path + "removed_noise.png", img)

    #  Apply threshold to get image with only black and white
    #img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2)

    # Write the image after apply opencv to do some ...
    cv2.imwrite(src_path + "thres.png", img)

    # Recognize text with tesseract for python
    result = pytesseract.image_to_string(Image.open(src_path + "thres.png"))
    # global color
    if result == '':
        color = 'white'
    else:
        color = 'black'
    return color

while True:
    now = datetime.now()
    time.sleep(3)

    with mss.mss() as sct:

        # the screen part to capture
        monitor = {"top": 206, "left": 233, "width": 60, "height": 20}
        output = "D:\AIMakesPossible\Trading Bot\images\\"

        # grab the data
        sct_image = sct.grab(monitor)

        # save to the picture file
        mss.tools.to_png(sct_image.rgb, sct_image.size, output=output + 'pps.png')

    ht_color = get_string("D:\AIMakesPossible\Trading Bot\images\pps.png")
    ht_colors.append(ht_color)
    print(ht_color)
    df_eth = _get_historical_data_('ETHUSDT', '1H', '1500')
    ema = df_eth.Close.ewm(span=200, adjust=False).mean().to_list()
    close = df_eth['Close'].to_list()
    close_last = close[-1]

    if ht_color == 'white' and ht_colors[-2] != 'white' and close_last > df_eth.ema[-1]:
        action = 'buy'
        actions.append(action)
        print(now, ht_color)
        print(action)
        print(actions[-1])
        print("------------------------------------------")
    elif ht_color == 'black' and ht_colors[-2] != 'black' and close_last < df_eth.ema[-1]:
        action = 'sell'
        actions.append(action)
        print(actions[-1])
        print(now, ht_color)
        print(action)
        print("------------------------------------------")

    else:
        action = 'hold'
        actions.append(action)

    account = client.futures_account_balance()

    for i in range(len(account)):
        if account[i].get('asset') == 'USDT':
            usdtbal = account[i].get('balance')

    prices = client.get_all_tickers()
    for i in prices:
        for j in i:
            if j == "symbol":
                if i.get('symbol') == 'ETHUSDT':
                    ETH_price = float(i.get('price'))

    quantity_taken = int(100 * 20 / ETH_price)
    leverage_taken = client.futures_change_leverage(symbol="ETHUSDT", leverage=20)

    if action == 'buy' and actions[-2] != 'buy':
        orders.append('buy')
        print(orders[-1])

        place_new_order = client.futures_create_order(
            symbol='ETHUSDT',
            side='BUY',
            type='MARKET',
            quantity=quantity_taken)

        active_order = client.futures_get_all_orders(symbol='ETHUSDT')

        for i in active_order:
            for j in i:
                if i.get('reduceOnly') == False and i.get('status') == 'FILLED':
                    order_id = str(i.get('orderId'))

        current_order = client.futures_get_order(symbol='ETHUSDT', orderId=order_id)

        for i in current_order:
            qty = float(current_order['origQty'])
            buying_price = float(current_order['avgPrice'])

        profit_price = round(buying_price * 1.0153, 2)
        stop_price = round(buying_price * 0.990, 2)

        exit_order = client.futures_create_order(
            symbol='ETHUSDT',
            side='SELL',
            closePosition=True,
            type='TAKE_PROFIT_MARKET',
            timeInForce='GTC',
            stopPrice=profit_price,
            quantity=qty)

        place_new_order = client.futures_create_order(
            symbol='ETHUSDT',
            side='SELL',
            type='STOP_MARKET',
            timeInForce='GTC',
            closePosition='true',
            stopPrice=stop_price,
            quantity=qty)

    elif action == 'sell' and actions[-2] != 'sell':
        orders.append('sell')
        print(orders[-1])

        place_new_order = client.futures_create_order(
            symbol='ETHUSDT',
            side='SELL',
            type='MARKET',
            quantity=quantity_taken)


        active_order = client.futures_get_all_orders(symbol='ETHUSDT')

        for i in active_order:
            for j in i:
                if i.get('reduceOnly') == False and i.get('status') == 'FILLED':
                    order_id = str(i.get('orderId'))

        current_order = client.futures_get_order(symbol='ETHUSDT', orderId=order_id)

        for i in current_order:
            qty = float(current_order['origQty'])
            buying_price = float(current_order['avgPrice'])

        profit_price = round(buying_price * 0.9847, 2)
        stop_price = round(buying_price * 1.01, 2)

        exit_order = client.futures_create_order(
            symbol='ETHUSDT',
            side='BUY',
            closePosition=True,
            type='TAKE_PROFIT_MARKET',
            timeInForce='GTC',
            stopPrice=profit_price,
            quantity=qty)

        place_new_order = client.futures_create_order(
            symbol='ETHUSDT',
            side='BUY',
            type='STOP_MARKET',
            timeInForce='GTC',
            closePosition='true',
            stopPrice=stop_price,
            quantity=qty)

    else:
        orders.append('none')
    while True:
        open_orders = client.futures_get_open_orders(symbol='ETHUSDT')
        if len(open_orders) < 3:
            cancel_open_orders = client.futures_cancel_all_open_orders(symbol='ETHUSDT')
            break