import time
import pandas_ta as ta
AppName="5P50985207"
AppSource=22072
UserID="Xr375mgFMNK"
Password="3lk8hnSOROg"
UserKey="gmRtyJT5iSs21juJA6Q6eSG4lekeIyjo"
EncryptionKey="BTOYpwClDHz1qydFoyYy88Oc7XZwyDCB"
Validupto="3/30/2050 12:00:00 PM"
Redirect_URL="Null"
totpstr="GUYDSOBVGIYDOXZVKBDUWRKZ"
from py5paisa import FivePaisaClient
import pyotp,datetime
from datetime import datetime,timedelta
import pandas as pd
client=None
def login():
    global client
    cred={
        "APP_NAME":AppName,
        "APP_SOURCE":AppSource,
        "USER_ID":UserID,
        "PASSWORD":Password,
        "USER_KEY":UserKey,
        "ENCRYPTION_KEY":EncryptionKey
        }

    twofa = pyotp.TOTP(totpstr)
    twofa = twofa.now()
    print(twofa)
    client = FivePaisaClient(cred=cred)
    client.get_totp_session(client_code=50985207,totp=twofa,pin=162916)
    client.get_oauth_session('Your Response Token')
    print(client.get_access_token())



def day_first_candle_avg(token,timeframe):
    global client
    from_time = datetime.now() - timedelta(days=50)
    to_time = datetime.now()
    df = client.historical_data('N', 'C', token, timeframe, from_time, to_time)
    df['Datetime'] = pd.to_datetime(df['Datetime'])
    df['Time'] = df['Datetime'].dt.time  # Extract the time from the datetime
    df = df[df['Time'] == datetime.strptime("09:15:00", "%H:%M:%S").time()]  # Filter rows for 09:15:00 time
    df.reset_index(drop=True, inplace=True)
    df['Candle Size'] = df['High'] - df['Low']
    num_days = len(df)
    candle_size_sum = df['Candle Size'].sum()
    average = candle_size_sum / num_days

    return average

def get_forty_five(token,timeframe):
    global client
    from_time = datetime.now() - timedelta(days=4)
    to_time = datetime.now()
    df = client.historical_data('N', 'C', token, timeframe, from_time, to_time)
    df['Datetime'] = pd.to_datetime(df['Datetime'])
    df.set_index('Datetime', inplace=True)
    df.reset_index(inplace=True)
    df['Datetime'] = df['Datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')
    last_three_rows = df.tail(3)
    highest_high = last_three_rows['High'].max()
    lowest_low = last_three_rows['Low'].min()
    return highest_high, lowest_low


def get_historical_data(token,timeframe):
    global client
    from_time = datetime.now() - timedelta(days=4)
    to_time = datetime.now()
    df = client.historical_data('N', 'C', token, timeframe, from_time, to_time)
    df['Datetime'] = pd.to_datetime(df['Datetime'])
    df.set_index('Datetime', inplace=True)
    df.reset_index(inplace=True)
    df['Datetime'] = df['Datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')
    last_row_values = df.iloc[-1].to_dict()

    return last_row_values
def determine_min(minstr):
    min = 0
    if minstr == "1m":
        min = 1
    if minstr == "2m":
        min = 2
    if minstr == "3m":
        min = 3
    if minstr == "5m":
        min = 5
    if minstr == "15m":
        min = 15
    if minstr == "30m":
        min = 30

    return min
def round_down_to_interval(dt, interval_minutes):
    remainder = dt.minute % interval_minutes
    minutes_to_current_boundary = remainder

    rounded_dt = dt - timedelta(minutes=minutes_to_current_boundary)

    rounded_dt = rounded_dt.replace(second=0, microsecond=0)

    return rounded_dt
def get_historical_data_tradeexecution(token, timeframe):
    global client
    current_time = datetime.now()
    if timeframe == "1m":
        delta_minutes = 1
        delta_minutes2 = 2
    elif timeframe == "2m":
        delta_minutes = 2
        delta_minutes2 = 4
    elif timeframe == "3m":
        delta_minutes = 3
        delta_minutes2 = 6
    elif timeframe == "5m":
        delta_minutes = 5
        delta_minutes2 = 10

    next_specific_part_time = datetime.now() - timedelta(
        seconds=determine_min(timeframe) * 60)
    desired_time_str1 = round_down_to_interval(next_specific_part_time,
                                               determine_min(timeframe))
    desired_time_str2 = desired_time_str1 - timedelta(
        seconds=determine_min(timeframe) * 60)

    print("desired time:", desired_time_str1)

    from_time = datetime.now() - timedelta(days=7)
    to_time = datetime.now()
    df = client.historical_data('N', 'C', token, timeframe, from_time, to_time)
    df["MA20"] = ta.ema(close=df["Close"], length=20)
    df["MA200"] = ta.ema(close=df["Close"], length=200)
    df["ATR"] = ta.atr(high=df["High"],low=df["Low"],close=df["Close"], length=14)
    df['Datetime'] = pd.to_datetime(df['Datetime'])
    last_two_rows = df.iloc[-2:]
    desired_row = last_two_rows[last_two_rows['Datetime'] == desired_time_str1]

    if not desired_row.empty:
        desired_row_values = desired_row.iloc[0].to_dict()
        return desired_row_values
    else:
        return None



def get_live_market_feed():
    global client
    req_list_ = [{"Exch": "N", "ExchType": "C", "ScripData": "ITC"},
    {"Exch": "N", "ExchType": "C", "ScripCode": "2885"}]

    print(client.fetch_market_feed_scrip(req_list_))

def previousdayclose(code):
    global client
    req_list_ = [{"Exch": "N", "ExchType": "C", "ScripCode": code}]
    responce=client.fetch_market_feed_scrip(req_list_)
    pclose_value = float(responce['Data'][0]['PClose'])
    return pclose_value


def get_ltp(code):
    global client
    try:
        req_list_ = [{"Exch": "N", "ExchType": "C", "ScripCode": code}]
        responce=client.fetch_market_feed_scrip(req_list_)
        last_rate = float(responce['Data'][0].get('LastRate', 0))
        print(last_rate)
    except Exception as e:
        time.sleep(1)
        req_list_ = [{"Exch": "N", "ExchType": "C", "ScripCode": code}]
        responce = client.fetch_market_feed_scrip(req_list_)
        last_rate = float(responce['Data'][0].get('LastRate', 0))
        print(last_rate)

    return last_rate

def buy( ScripCode , Qty, Price,OrderType='B',Exchange='N',ExchangeType='C'):
    global client
    client.place_order(OrderType=OrderType,
                       Exchange=Exchange,
                       ExchangeType=ExchangeType,
                       ScripCode = ScripCode,
                       Qty=Qty,
                       Price=Price)

def sell( ScripCode , Qty, Price,OrderType='S',Exchange='N',ExchangeType='C'):
    global client
    client.place_order(OrderType=OrderType,
                       Exchange=Exchange,
                       ExchangeType=ExchangeType,
                       ScripCode = ScripCode,
                       Qty=Qty,
                       Price=Price)
def short( ScripCode , Qty, Price,OrderType='S',Exchange='N',ExchangeType='C'):
    global client
    client.place_order(OrderType=OrderType,
                       Exchange=Exchange,
                       ExchangeType=ExchangeType,
                       ScripCode = ScripCode,
                       Qty=Qty,
                       Price=Price)

def cover( ScripCode , Qty, Price,OrderType='B',Exchange='N',ExchangeType='C'):
    global client
    client.place_order(OrderType=OrderType,
                       Exchange=Exchange,
                       ExchangeType=ExchangeType,
                       ScripCode = ScripCode,
                       Qty=Qty,
                       Price=Price)

def get_position():
    global client
    responce = client.positions()

    return responce

def get_margin():
    global client
    responce= client.margin()
    if responce:
        net_available_margin =float (responce[0]['NetAvailableMargin'])
        return net_available_margin
    else:
        print("Error: Unable to get NetAvailableMargin")
        return None

def orderbook():


    global client
    client.get_tradebook()























