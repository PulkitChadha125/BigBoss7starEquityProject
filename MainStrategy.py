import traceback
import pyotp
import FivePaisaIntegration,Zerodha_Integration
import time as sleep_time
import pandas as pd
from datetime import datetime
import threading
lock = threading.Lock()
import time
FivePaisaIntegration.login()

total_pnl=[]

def get_zerodha_credentials():
    credentials = {}
    try:
        df = pd.read_csv('MainSettings.csv')
        for index, row in df.iterrows():
            title = row['Title']
            value = row['Value']
            credentials[title] = value
    except pd.errors.EmptyDataError:
        print("The CSV file is empty or has no data.")
    except FileNotFoundError:
        print("The CSV file was not found.")
    except Exception as e:
        print("An error occurred while reading the CSV file:", str(e))

    return credentials


def write_to_order_logs(message):
    with open('OrderLog.txt', 'a') as file:  # Open the file in append mode
        file.write(message + '\n')



def delete_file_contents(file_name):
    try:
        # Open the file in write mode, which truncates it (deletes contents)
        with open(file_name, 'w') as file:
            file.truncate(0)
        print(f"Contents of {file_name} have been deleted.")
    except FileNotFoundError:
        print(f"File {file_name} not found.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

credentials_dict = get_zerodha_credentials()
symbol_dict={}
result_dict={}
def get_user_settings():
    global result_dict
    try:
        csv_path = 'TradeSettings.csv'
        df = pd.read_csv(csv_path)
        df.columns = df.columns.str.strip()
        result_dict = {}
        # Symbol,HighFortyFive,LowFortyFive,AverageValue,ScripCode,high,low,Pivot,Bottom Central,Top Central,Quantity,USE_TWENTY_MA,USE_TWO_HUNDRED_MA,
        # CHECK_GAP_CONDITION,USE_CPR,USE_FORTYFIVE,USE_PREVIOUSDAY_HIGH_LOW,USE_BOSS,USE_MANAGER,USE_WORKER,REWARD_MULTIPLIER_BOSS,
        # REWARD_MULTIPLIER_WORKER,REWARD_MULTIPLIER_MANAGER,WORKER_CANDLE_MUL,BOSS_CANDLE_MUL,
        # MANAGER_CANDLE_MUL,CounterDecision,NumBerOfCounterTrade,USE_PARTIAL_PROFIT,
        # PartialProfitPercentage_qty_size,
        # PartProfitMultipler,USE_CANDLE_CLOSING,CANDLE_CLOSEING_PERCENTAGE,USE_TSL,TSL_POINTS
        for index, row in df.iterrows():
            symbol_dict = {
                'Symbol': row['Symbol'],'HighFortyFive': int(row['HighFortyFive']),'LowFortyFive':float(row['LowFortyFive']),
                'AverageValue': float(row['AverageValue']),'ScripCode': float(row['ScripCode']),'high': float(row['high']),
                'low': float(row['low']),'Pivot': float(row['Pivot']),'Bottom Central': float(row['Bottom Central']),
                'Top Central': float(row['Top Central']),'Quantity': float(row['Quantity']),'TradingEnabled': row['TradingEnabled'],'TimeFrame': row['TimeFrame'],
                'USE_TWENTY_MA': (row['USE_TWENTY_MA']),'USE_TWO_HUNDRED_MA': (row['USE_TWO_HUNDRED_MA']),'CHECK_GAP_CONDITION': (row['CHECK_GAP_CONDITION']),
                'USE_CPR': (row['USE_CPR']),'USE_FORTYFIVE': (row['USE_FORTYFIVE']),'USE_PREVIOUSDAY_HIGH_LOW': (row['USE_PREVIOUSDAY_HIGH_LOW']),
                'USE_BOSS': (row['USE_BOSS']),'USE_MANAGER': (row['USE_MANAGER']),'USE_WORKER': (row['USE_WORKER']),
                'REWARD_MULTIPLIER_BOSS': float(row['REWARD_MULTIPLIER_BOSS']),'REWARD_MULTIPLIER_WORKER': float(row['REWARD_MULTIPLIER_WORKER']),
                'REWARD_MULTIPLIER_MANAGER': float(row['REWARD_MULTIPLIER_MANAGER']),'BOSS_CANDLE_MUL': float(row['BOSS_CANDLE_MUL']),
                'MANAGER_CANDLE_MUL': float(row['MANAGER_CANDLE_MUL']),'WORKER_CANDLE_MUL':float(row['WORKER_CANDLE_MUL']),'CounterDecision': float(row['CounterDecision']),
                'NumBerOfCounterTrade': float(row['NumBerOfCounterTrade']),'USE_PARTIAL_PROFIT': float(row['USE_PARTIAL_PROFIT']),
                'PartialProfitPercentage_qty_size': float(row['PartialProfitPercentage_qty_size']),'USE_CANDLE_CLOSING': float(row['USE_CANDLE_CLOSING']),
                'CANDLE_CLOSEING_PERCENTAGE': float(row['CANDLE_CLOSEING_PERCENTAGE']),'USE_TSL': float(row['TSL_POINTS']),
                "StartTime": row['StartTime'],"StopTime": row['StopTime'],"open_value" : None,"high_value" :None,"low_value" : None,
                "close_value" :None,"volume_value": None,"NotTradingReason":None,"Rangeeee":None,"value_boss":None,
                "value_manager": None,"value_worker": None,"StoplossValue": None,"TargetValue": None,'candle_type':None,
                "MA20":None,"MA200":None,"buy200":None,"sell200":None,"buy20":None,"sell20":None,"buycrp":None,"sellcpr":None,"45buy":None,"45sell":None,
                "buyday":None,'sellday':None,"buygap":None,"sellgap":None,
            }
            result_dict[row['Symbol']] = symbol_dict
        print("result_dict: ",result_dict)
    except Exception as e:
        print("Error happened in fetching symbol", str(e))

get_user_settings()
latencyadd=False


def main_strategy():
    global latencyadd, result_dict, next_specific_part_time, total_pnl, runningpnl, niftypnl, bankniftypnl

    try:
        for symbol, params in result_dict.items():
            symbol_value = params['Symbol']
            timestamp = datetime.now()
            timestamp = timestamp.strftime("%d/%m/%Y %H:%M:%S")
            start_time_str = params['StartTime']
            start_time = datetime.strptime(start_time_str, '%H:%M').time()
            end_time_str = params['StopTime']
            end_time = datetime.strptime(end_time_str, '%H:%M').time()
            # Get the current time as a datetime object
            current_time = datetime.now().time()
            g = start_time <= current_time <= end_time
            print(f"{symbol}: {g}")
            if isinstance(symbol_value, str):
                if params["RunOnceHistory"] == False and start_time <= current_time <= end_time:
                    params["RunOnceHistory"] = True
                    if latencyadd == False:
                        latencyadd = True
                        time.sleep(2)

                    data = FivePaisaIntegration.get_historical_data_tradeexecution(int(params['ScripCode']),
                                                                                   str(params['TimeFrame']))
                    print(f"Symbol data {symbol} : {data}")
                    open_value = float(data['Open'])
                    high_value = float(data['High'])
                    low_value = float(data['Low'])
                    close_value = float(data['Close'])
                    volume_value = float(data['Volume'])
                    params["open_value"] = open_value
                    params["high_value"] = high_value
                    params["low_value"] = low_value
                    params["close_value"] = close_value
                    params["volume_value"] = volume_value
                    params["MA20"] =float(data['MA20'])
                    params["MA200"] =float(data['MA200'])
                    Rangeeee = float(high_value - low_value)
                    params["Rangeeee"] = float(Rangeeee)

                    params["value_boss"]=float(params["AverageValue"])*float(params["BOSS_CANDLE_MUL"])
                    params["value_manager"]=float(params["AverageValue"])*float(params["MANAGER_CANDLE_MUL"])
                    params["value_worker"]=float(params["AverageValue"])*float(params["WORKER_CANDLE_MUL"])
                    # "buygap":None,"sellgap":None,

                    if params['CHECK_GAP_CONDITION'] == True:
                        if params["high_value"] <= params["high"]:
                            params["buygap"]= True
                            orderlog = f"{timestamp} Candle is inside previous day range buy condition {symbol}"
                            print(orderlog)
                            write_to_order_logs(orderlog)

                        if params["low_value"] > params["high"]:
                            params["buygap"]= False
                            params["NotTradingReason"] = f"{timestamp} Candle is outside previous day range buy condition {symbol}"
                            orderlog = params["NotTradingReason"]
                            print(orderlog)
                            write_to_order_logs(orderlog)

                        if params["low_value"] >= params["low"]:
                            params["sellgap"]= True
                            orderlog = f"{timestamp}Candle is inside previous day range sell condition {symbol}"
                            print(orderlog)
                            write_to_order_logs(orderlog)

                        if params["low_value"] < params["low"]:
                            params["sellgap"]= False
                            orderlog = f"{timestamp} Candle is outside previous day range sell condition {symbol}"
                            print(orderlog)
                            write_to_order_logs(orderlog)
                    else:
                        params["TradingEnabled"] = True
                        params["sellgap"]= True
                        params["buygap"]= False
                        params["NotTradingReason"] = f"{timestamp} Gap condition is disabled it will not be checked {symbol}"
                        orderlog = params["NotTradingReason"]
                        print(orderlog)
                        write_to_order_logs(orderlog)

                    # 'Bottom Central': float(row['Bottom Central']),
                    #                 'Top Central': float(row['Top Central']),"buygap":None,"sellgap":None
                    if params['USE_CPR'] == True:
                        if params["high_value"] >= params["Top Central"]:
                            params["buycrp"]= True
                            orderlog = f"{timestamp} High is greater than top cpr {symbol}"
                            print(orderlog)
                            write_to_order_logs(orderlog)

                        if params["high_value"] < params["Top Central"]:
                            params["buycrp"]= False
                            params["NotTradingReason"] = f"{timestamp} High is less than top cpr{symbol}"
                            orderlog = params["NotTradingReason"]
                            print(orderlog)
                            write_to_order_logs(orderlog)

                        if params["low_value"] <= params["Bottom Central"]:
                            params["sellcpr"]= True
                            orderlog = f"{timestamp} low is less than bottom cpr{symbol}"
                            print(orderlog)
                            write_to_order_logs(orderlog)

                        if params["low_value"] > params["Bottom Central"]:
                            params["sellcpr"]= False
                            orderlog = f"{timestamp} low is greater than bottom cpr {symbol}"
                            print(orderlog)
                            write_to_order_logs(orderlog)
                    else:
                        params["TradingEnabled"] = True
                        params["sellcpr"]= True
                        params["buycrp"]= True
                        params["NotTradingReason"] = f"{timestamp} CPR condition is disabled condition will not be checked {symbol}"
                        orderlog = params["NotTradingReason"]
                        print(orderlog)
                        write_to_order_logs(orderlog)

                    # 'USE_CPR': float(row['USE_CPR']),'USE_FORTYFIVE': float(row['USE_FORTYFIVE'])
                    # "45buy": None, "45sell": None 'HighFortyFive': int(row['HighFortyFive']),'LowFortyFive':float(row['LowFortyFive'])
                    if params["USE_FORTYFIVE"] == True:
                        if params["high_value"] >= params["HighFortyFive"]:
                            params["45buy"]= True
                            orderlog = f"{timestamp} High is greater than high of previous day 45 min {symbol}"
                            print(orderlog)
                            write_to_order_logs(orderlog)

                        if params["high_value"] < params["HighFortyFive"]:
                            params["45buy"]= False
                            params["NotTradingReason"] = f"{timestamp} High is less than high of previous day 45 min {symbol}"
                            orderlog = params["NotTradingReason"]
                            print(orderlog)
                            write_to_order_logs(orderlog)

                        if params["low_value"] <= params["LowFortyFive"]:
                            params["45sell"]= True
                            orderlog = f"{timestamp} low price is below low of previous day 45 min {symbol}"
                            print(orderlog)
                            write_to_order_logs(orderlog)

                        if params["low_value"] > params["LowFortyFive"]:
                            params["45sell"]= False
                            orderlog = f"{timestamp} low price is above low of previous day 45 min {symbol}"
                            print(orderlog)
                            write_to_order_logs(orderlog)
                    else:
                        params["TradingEnabled"] = True
                        params["45sell"]= True
                        params["45buy"]= True
                        params["NotTradingReason"] = f"{timestamp} 45 min condition is disabled condition will not be checked {symbol}"
                        orderlog = params["NotTradingReason"]
                        print(orderlog)
                        write_to_order_logs(orderlog)

                    if params["USE_TWO_HUNDRED_MA"] == True:
                        if params["high_value"] >= params["MA200"]:
                            params["buy200"]= True
                            orderlog = f"{timestamp} 20 ma is below high of trigger candle for {symbol}"
                            print(orderlog)
                            write_to_order_logs(orderlog)

                        if params["high_value"] < params["MA200"]:
                            params["buy200"]= False
                            params["NotTradingReason"] = f"{timestamp} 20 ma is above high of trigger candle for {symbol}"
                            orderlog = params["NotTradingReason"]
                            print(orderlog)
                            write_to_order_logs(orderlog)

                        if params["low_value"] <= params["MA200"]:
                            params["sell200"]= True
                            orderlog = f"{timestamp} low price is below 200 ema {symbol}"
                            print(orderlog)
                            write_to_order_logs(orderlog)

                        if params["low_value"] > params["MA200"]:
                            params["sell200"]= False
                            orderlog = f"{timestamp} low price is above 200 ema {symbol}"
                            print(orderlog)
                            write_to_order_logs(orderlog)
                    else:
                        params["TradingEnabled"] = True
                        params["sell200"]=True
                        params["buy200"] = True
                        params["NotTradingReason"] = f"{timestamp} 200 ma is disabled condition will not be checked {symbol}"
                        orderlog = params["NotTradingReason"]
                        print(orderlog)
                        write_to_order_logs(orderlog)

                    # params["sell200"]
                    if params["USE_TWENTY_MA"]==True:
                        if params["high_value"]>=params["MA20"]:
                            params["buy20"]: True
                            orderlog = f"{timestamp} 20 ma is below high of trigger candle for {symbol}"
                            print(orderlog)
                            write_to_order_logs(orderlog)

                        if params["high_value"]<params["MA20"]:
                            params["buy20"]: False
                            params["NotTradingReason"] = f"{timestamp} 20 ma is above high of trigger candle for {symbol}"
                            orderlog = params["NotTradingReason"]
                            print(orderlog)
                            write_to_order_logs(orderlog)

                        if params["low_value"]<=params["MA20"]:
                            params["sell20"]: True
                            orderlog = f"{timestamp} low price is below 20 ema {symbol}"
                            print(orderlog)
                            write_to_order_logs(orderlog)

                        if params["low_value"]>params["MA20"]:
                            params["sell20"]: False
                            orderlog = f"{timestamp} low price is above 20 ema {symbol}"
                            print(orderlog)
                            write_to_order_logs(orderlog)

                    else:
                        params["TradingEnabled"] = True
                        params["sell20"] = True
                        params["buy20"] = True
                        params["NotTradingReason"] = f"{timestamp} 20 ma is disabled condition will not be checked {symbol}"
                        orderlog = params["NotTradingReason"]
                        print(orderlog)
                        write_to_order_logs(orderlog)



                    if params["Rangeeee"]<=params["value_worker"]:
                        orderlog=f"{timestamp} Worker candle size found in {symbol} , candlesize = {params['Rangeeee']},worker candle set value: {params['value_worker']}"
                        print(orderlog)
                        write_to_order_logs(orderlog)
                        if params['USE_WORKER']==True:
                            params['candle_type']='WORKER'
                        else:
                            params["TradingEnabled"] = False
                            params["NotTradingReason"] =  f"{timestamp} Worker Candle Usage is disabled {symbol}"
                            orderlog = params["NotTradingReason"]
                            print(orderlog)
                            write_to_order_logs(orderlog)


                    if params["Rangeeee"] >= params["value_worker"] and params["Rangeeee"] <= params["value_manager"]:
                        orderlog = f"Manager candle size found in {symbol} , candlesize = {params['Rangeeee']},worker candle set value: {params['value_manager']}"
                        print(orderlog)
                        write_to_order_logs(orderlog)
                        if params['USE_MANAGER'] ==True:
                            params['candle_type']='MANAGER'
                        else:
                            params["TradingEnabled"] = False
                            params["NotTradingReason"] =  f"{timestamp} Manager Candle Usage is disabled {symbol} "
                            orderlog = params["NotTradingReason"]
                            print(orderlog)
                            write_to_order_logs(orderlog)

                    if  params["Rangeeee"] >= params["value_manager"]:
                        orderlog = f"Boss candle size found in {symbol} , candlesize = {params['Rangeeee']},worker candle set value: {params['value_boss']}"
                        print(orderlog)
                        write_to_order_logs(orderlog)
                        if params['USE_BOSS']==True:
                            params['candle_type']='BOSS'

                        else:
                            params["TradingEnabled"] = False
                            params["NotTradingReason"] =  f"{timestamp} BOSS Candle Usage is disabled {symbol} "
                            orderlog = params["NotTradingReason"]
                            print(orderlog)
                            write_to_order_logs(orderlog)

    except Exception as e:
        print("Error happened in Main strategy loop: ", str(e))
        traceback.print_exc()



while True:

    Stoptime = credentials_dict.get('Stoptime')

    stop_time = datetime.strptime(Stoptime, '%H:%M').time()

    now = datetime.now().time()
    if now < stop_time:
        main_strategy()
        time.sleep(1)


