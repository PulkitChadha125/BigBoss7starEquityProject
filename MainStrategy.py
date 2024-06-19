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
        for index, row in df.iterrows():
            symbol_dict = {
                'Symbol': row['Symbol'],'HighFortyFive': int(row['HighFortyFive']),'LowFortyFive':float(row['LowFortyFive']),
                'AverageValue': float(row['AverageValue']),'ScripCode': float(row['ScripCode']),'high': float(row['high']),
                'low': float(row['low']),'Pivot': float(row['Pivot']),'Bottom Central': float(row['Bottom Central']),
                'Top Central': float(row['Top Central']),'Risk': float(row['Risk']),'TradingEnabled': row['TradingEnabled'],'TimeFrame': row['TimeFrame'],
                'USE_TWENTY_MA': (row['USE_TWENTY_MA']),'USE_TWO_HUNDRED_MA': (row['USE_TWO_HUNDRED_MA']),'CHECK_GAP_CONDITION': (row['CHECK_GAP_CONDITION']),
                'USE_CPR': (row['USE_CPR']),'USE_FORTYFIVE': (row['USE_FORTYFIVE']),'USE_PREVIOUSDAY_HIGH_LOW': (row['USE_PREVIOUSDAY_HIGH_LOW']),
                'USE_BOSS': (row['USE_BOSS']),'USE_MANAGER': (row['USE_MANAGER']),'USE_WORKER': (row['USE_WORKER']),
                'TargetBossPercentage': float(row['TargetBossPercentage']),'REWARD_MULTIPLIER_WORKER': float(row['REWARD_MULTIPLIER_WORKER']),
                'MANAGER_CANDLE_MUL_UP': float(row['MANAGER_CANDLE_MUL_UP']),'MANAGER_CANDLE_MUL_DOWN': float(row['MANAGER_CANDLE_MUL_DOWN']),'BOSS_CANDLE_MUL': float(row['BOSS_CANDLE_MUL']),
                'WORKER_CANDLE_MUL':float(row['WORKER_CANDLE_MUL']),'NoOfCounterTrade': float(row['NoOfCounterTrade']),'USE_PARTIAL_PROFIT': (row['USE_PARTIAL_PROFIT']),
                'PartialProfitPercentage_qty_size': float(row['PartialProfitPercentage_qty_size']),'USE_CLOSING_CRITERIA_BOSS': (row['USE_CLOSING_CRITERIA_BOSS']),
                'ClosePercentage_BOSS': float(row['ClosePercentage_BOSS']),'USE_TSL': (row['USE_TSL']),
                "StartTime": row['StartTime'],"StopTime": row['StopTime'],"open_value" : None,"high_value" :None,"low_value" : None,
                "close_value" :None,"volume_value": None,"NotTradingReason":None,"Rangeeee":None,"value_boss":None,
                "value_manager_UP": None,"value_manager_DOWN": None,"value_worker": None,"StoplossValue": None,"TargetValue": None,'candle_type':None,
                "MA20":None,"MA200":None,"buy200":None,"sell200":None,"buy20":None,"sell20":None,"buycrp":None,"sellcpr":None,"45buy":None,"45sell":None,
                "buyday":None,'sellday':None,"buygap":None,"sellgap":None,"count":0,"InitialTrade":None,"BUY":False,"SHORT":False,"ATR":None,
                "partialprofitval":None,"Quantity":None,"partial_qty":None,"Remain_qty":None,"bigbosstrade":False,"bigbosstradetype":None,"NextTslLevel":None,"RunOnceHistory":False,
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

            if isinstance(symbol_value, str):
                if params["RunOnceHistory"] == False and start_time <= current_time <= end_time:
                    params["RunOnceHistory"] = True
                    if latencyadd == False:
                        latencyadd = True
                        time.sleep(2)

                    print(f"{symbol_value}, {params['ScripCode']}")

                    data = FivePaisaIntegration.get_historical_data_tradeexecution(int(params['ScripCode']),
                                                                                   str(params['TimeFrame']))
                    print(f"Symbol data {symbol} : {data}")
                    open_value = float(data['Open'])
                    high_value = float(data['High'])
                    low_value = float(data['Low'])
                    close_value = float(data['Close'])
                    volume_value = float(data['Volume'])
                    Rangeeee = float(high_value - low_value)
                    params["Rangeeee"] = float(Rangeeee)
                    qty = params["Risk"] / Rangeeee
                    qty = int(qty)
                    print(f"{symbol} qty : {qty}")
                    params["partial_qty"]=qty*params["PartialProfitPercentage_qty_size"]*0.01
                    params["partial_qty"]=abs(qty-params["partial_qty"])
                    print(f"{symbol} partial qty: {params['partial_qty']}")
                    params["Remain_qty"]= abs(qty-params["partial_qty"])
                    params["Quantity"] = qty
                    params["open_value"] = open_value
                    params["high_value"] = high_value
                    params["low_value"] = low_value
                    params["close_value"] = close_value
                    params["volume_value"] = volume_value
                    params["MA20"] =float(data['MA20'])
                    params["MA200"] =float(data['MA200'])
                    params["ATR"] = float(data['ATR'])



                    params["value_boss"]=float(params["AverageValue"])*float(params["BOSS_CANDLE_MUL"])
                    params["value_manager_UP"]=float(params["AverageValue"])*float(params["MANAGER_CANDLE_MUL_UP"])
                    params["value_manager_DOWN"] = float(params["AverageValue"]) * float(params["MANAGER_CANDLE_MUL_DOWN"])
                    params["value_worker"]=float(params["AverageValue"])*float(params["WORKER_CANDLE_MUL"])

                    if  params['USE_PREVIOUSDAY_HIGH_LOW'] == True:
                        if params["high_value"] >= params["high"]:
                            params["buyday"]= True
                            orderlog = f"{timestamp} High {params['high_value']} of today 1st candle is greater than high of previous day {params['high']}, buy trade can happen {symbol}"
                            print(orderlog)
                            write_to_order_logs(orderlog)

                        if params["high_value"] < params["high"]:
                            params["buyday"]= False
                            params["NotTradingReason"] = f"{timestamp} High {params['high_value']} of today 1st candle is less than high of previous day {params['high']}, buy trade cannot happen   {symbol}"
                            orderlog = params["NotTradingReason"]
                            print(orderlog)
                            write_to_order_logs(orderlog)

                        if params["low_value"] <= params["low"]:
                            params["sellday"]= True
                            orderlog = f"{timestamp} low price {params['low_value']} is below low of previous day {params['low']},  sell trade can happen  {symbol}"
                            print(orderlog)
                            write_to_order_logs(orderlog)

                        if params["low_value"] > params["low"]:
                            params["sellday"]= False
                            orderlog = f"{timestamp} low price {params['low_value']} is above low of previous day {params['low']}, sell trade cannot happen    {symbol}"
                            print(orderlog)
                            write_to_order_logs(orderlog)

                    else:
                        params["sellday"] = True
                        params["buyday"] = True
                        params["NotTradingReason"] = f"{timestamp} Previous day high and low condition is disabled it will not be checked {symbol}"
                        orderlog = params["NotTradingReason"]
                        print(orderlog)
                        write_to_order_logs(orderlog)


                    if params['CHECK_GAP_CONDITION'] == True:
                        if params["low_value"] <= params["high"]:
                            params["buygap"]= True
                            params["sellgap"] = True
                            orderlog = f"{timestamp} Candle low is inside pdh trade condition satisfied {symbol},9:15 low={params['low_value']}, previous day high={params['high']}"
                            print(orderlog)
                            write_to_order_logs(orderlog)

                        if params["low_value"] > params["high"]:
                            params["buygap"]= False
                            params["sellgap"] = False
                            params["NotTradingReason"] = f"{timestamp} Candle low is outside pdh trade condition not active {symbol},9:15 low={params['low_value']}, previous day high={params['high']}"
                            orderlog = params["NotTradingReason"]
                            print(orderlog)
                            write_to_order_logs(orderlog)

                        if params["high_value"] >= params["low"]:
                            params["sellgap"]= True
                            params["buygap"] = True
                            orderlog = f"{timestamp}Candle high is inside pdl trade condition active{symbol},9:15 high={params['high_value']}, previous day low={params['low']}"
                            print(orderlog)
                            write_to_order_logs(orderlog)

                        if params["high_value"] < params["low"]:
                            params["sellgap"]= False
                            params["buygap"] = False
                            orderlog = f"{timestamp} Candle high is outside pdl trade condition  not active {symbol},9:15 high={params['high_value']}, previous day low={params['low']}"
                            print(orderlog)
                            write_to_order_logs(orderlog)
                    else:
                        params["sellgap"]= True
                        params["buygap"]= True
                        params["NotTradingReason"] = f"{timestamp} Gap condition is disabled it will not be checked {symbol}"
                        orderlog = params["NotTradingReason"]
                        print(orderlog)
                        write_to_order_logs(orderlog)

                    # 'Bottom Central': float(row['Bottom Central']),
                    #                 'Top Central': float(row['Top Central']),"buygap":None,"sellgap":None
                    if params['USE_CPR'] == True:
                        if params["high_value"] >= params["Top Central"]:
                            params["buycrp"]= True
                            orderlog = f"{timestamp} High {params['high_value']} is greater than top cpr {params['Top Central']}, {symbol} , buy condition satisfied"
                            print(orderlog)
                            write_to_order_logs(orderlog)

                        if params["high_value"] < params["Top Central"]:
                            params["buycrp"]= False
                            params["NotTradingReason"] = f"{timestamp} High {params['high_value']}  is less than top cpr {params['Top Central']}, {symbol}, buy condition not satisfied"
                            orderlog = params["NotTradingReason"]
                            print(orderlog)
                            write_to_order_logs(orderlog)

                        if params["low_value"] <= params["Bottom Central"]:
                            params["sellcpr"]= True
                            orderlog = f"{timestamp} low {params['low_value']} is less than bottom cpr {params['Bottom Central']} ,{symbol}, sell condition satisfied"
                            print(orderlog)
                            write_to_order_logs(orderlog)

                        if params["low_value"] > params["Bottom Central"]:
                            params["sellcpr"]= False
                            orderlog = f"{timestamp} low {params['low_value']} is greater than bottom cpr {params['Bottom Central']}, {symbol}, sell condition not satisfied"
                            print(orderlog)
                            write_to_order_logs(orderlog)
                    else:
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
                            params["NotTradingReason"]= f"{timestamp} Candle High {params['high_value']} is greater than high of previous day 45 min {params['HighFortyFive']}, {symbol} buy condition satisfied"
                            orderlog=params["NotTradingReason"]
                            print(orderlog)
                            write_to_order_logs(orderlog)

                        if params["high_value"] < params["HighFortyFive"]:
                            params["45buy"]= False
                            params["NotTradingReason"] = f"{timestamp} Candle High {params['high_value']} is less than high of previous day 45 min {params['HighFortyFive']} , {symbol} buy condition not satisfied"
                            orderlog = params["NotTradingReason"]
                            print(orderlog)
                            write_to_order_logs(orderlog)

                        if params["low_value"] <= params["LowFortyFive"]:
                            params["45sell"]= True
                            orderlog = f"{timestamp} Candle low price {params['low_value']} is below low of previous day 45 min {params['LowFortyFive']} {symbol}, sell condition satisfied"
                            print(orderlog)
                            write_to_order_logs(orderlog)

                        if params["low_value"] > params["LowFortyFive"]:
                            params["45sell"]= False
                            orderlog = f"{timestamp} Candle low price {params['low_value']} is above low of previous day 45 min {params['LowFortyFive']} {symbol}, sell condition not satisfied"
                            print(orderlog)
                            write_to_order_logs(orderlog)
                    else:
                        params["45sell"]= True
                        params["45buy"]= True
                        params["NotTradingReason"] = f"{timestamp} 45 min condition is disabled condition will not be checked {symbol}"
                        orderlog = params["NotTradingReason"]
                        print(orderlog)
                        write_to_order_logs(orderlog)

                    if params["USE_TWO_HUNDRED_MA"] == True:
                        if params["high_value"] >= params["MA200"]:
                            params["buy200"]= True
                            orderlog = f"{timestamp} 200 ma  {params['MA200']} is below candle high {params['high_value']} for  {symbol}, buy condition satisfied"
                            print(orderlog)
                            write_to_order_logs(orderlog)

                        if params["high_value"] < params["MA200"]:
                            params["buy200"]= False
                            params["NotTradingReason"] = f"{timestamp} 200 ma  {params['MA200']} is above candle high= {params['high_value']} for {symbol}, buy condition not satisfied"
                            orderlog = params["NotTradingReason"]
                            print(orderlog)
                            write_to_order_logs(orderlog)

                        if params["low_value"] <= params["MA200"]:
                            params["sell200"]= True
                            orderlog = f"{timestamp} Candle low  {params['low_value']} is below 200 ma {params['MA200']} ,{symbol}, sell condition satisfied"
                            print(orderlog)
                            write_to_order_logs(orderlog)

                        if params["low_value"] > params["MA200"]:
                            params["sell200"]= False
                            orderlog = f"{timestamp} Candle low  {params['low_value']} is above 200 ma {params['MA200']}, {symbol}, sell condition not satisfied"
                            print(orderlog)
                            write_to_order_logs(orderlog)
                    else:
                        params["sell200"]=True
                        params["buy200"] = True
                        params["NotTradingReason"] = f"{timestamp} 200 ma is disabled condition will not be checked {symbol}"
                        orderlog = params["NotTradingReason"]
                        print(orderlog)
                        write_to_order_logs(orderlog)

                    # params["sell200"]
                    if params["USE_TWENTY_MA"]==True:
                        if params["high_value"]>=params["MA20"]:
                            params["buy20"]= True
                            orderlog = f"{timestamp} 20 ma ={params['MA20']} is below candle high= {params['high_value']}  for {symbol}, buy condition satisfied"
                            print(orderlog)
                            write_to_order_logs(orderlog)

                        if params["high_value"]<params["MA20"]:
                            params["buy20"]= False
                            params["NotTradingReason"] = f"{timestamp} 20 ma={params['MA20']} is above candle high {params['high_value']} for {symbol}, buy condition not satisfied"
                            orderlog = params["NotTradingReason"]
                            print(orderlog)
                            write_to_order_logs(orderlog)

                        if params["low_value"]<=params["MA20"]:
                            params["sell20"]= True
                            orderlog = f"{timestamp} low price = {params['low_value']} is below 20 ma={params['MA20']} {symbol}, sell condition satisfied"
                            print(orderlog)
                            write_to_order_logs(orderlog)

                        if params["low_value"]>params["MA20"]:
                            params["sell20"]= False
                            orderlog = f"{timestamp} low price = {params['low_value']} is above 20 ma={params['MA20']}, {symbol},sell condition not satisfied"
                            print(orderlog)
                            write_to_order_logs(orderlog)

                    else:

                        params["sell20"] = True
                        params["buy20"] = True
                        params["NotTradingReason"] = f"{timestamp} 20 ma is disabled condition will not be checked {symbol}"
                        orderlog = params["NotTradingReason"]
                        print(orderlog)
                        write_to_order_logs(orderlog)



                    if params["Rangeeee"]<=params["value_worker"] and params['USE_WORKER']==True:
                        orderlog=f"{timestamp} Worker found in {symbol} , candlesize = {params['Rangeeee']},worker candle set value: {params['value_worker']}"
                        print(orderlog)
                        write_to_order_logs(orderlog)
                        params['candle_type']='WORKER'
                    else:
                        params['candle_type'] = None
                        params["NotTradingReason"] =  f"{timestamp} Worker Candle Usage is disabled {symbol}"
                        orderlog = params["NotTradingReason"]
                        print(orderlog)
                        write_to_order_logs(orderlog)


                    if params['candle_type'] is None and params["Rangeeee"] >= params["value_manager_DOWN"]and params["Rangeeee"] <= params["value_manager_UP"] and params['USE_MANAGER'] ==True:
                        orderlog = f"Manager candle size found in {symbol} , candlesize = {params['Rangeeee']},Manager candle set value: {params['value_manager']}"
                        print(orderlog)
                        write_to_order_logs(orderlog)
                        params['candle_type']='MANAGER'
                    else:
                        if params['candle_type'] is None:
                            params['candle_type'] = None
                            params["NotTradingReason"] =  f"{timestamp} Manager Candle Usage is disabled {symbol} "
                            orderlog = params["NotTradingReason"]
                            print(orderlog)
                            write_to_order_logs(orderlog)

                    if  params['candle_type'] is None and params["Rangeeee"] >= params["value_boss"] and params['USE_BOSS']==True:
                        orderlog = f"Boss candle size found in {symbol} , candlesize = {params['Rangeeee']},Boss candle set value: {params['value_boss']}"
                        print(orderlog)
                        write_to_order_logs(orderlog)
                        if params['USE_CLOSING_CRITERIA_BOSS']==False:
                            params['candle_type']='BOSS'
                        if params['USE_CLOSING_CRITERIA_BOSS'] == True:
                            if (close_value > open_value):
                                candlerange = high_value - low_value
                                perapproved = candlerange * params["ClosePercentage_BOSS"] * 0.01
                                closedist = abs(close_value - low_value)
                                if closedist>=params["value_boss"]:
                                    params['candle_type'] = 'BOSS'
                                else:
                                    params['candle_type'] = None
                                    orderlog = f"{timestamp} Order not taken in {symbol} closing percentage rule not met "
                                    print(orderlog)
                                    write_to_order_logs(orderlog)
                            if (close_value < open_value):
                                candlerange = high_value - low_value
                                perapproved = candlerange * params["ClosePercentage"] * 0.01
                                closedist = abs(high_value - close_value)
                                if closedist>=params["value_boss"]:
                                    params['candle_type'] = 'BOSS'
                                else:
                                    params['candle_type'] = None
                                    orderlog = f"{timestamp} Order not taken in {symbol} closing percentage rule not met "
                                    print(orderlog)
                                    write_to_order_logs(orderlog)

                    else:
                        if params['candle_type'] is None :
                            params["NotTradingReason"] =  f"{timestamp} BOSS Candle Usage is disabled {symbol} "
                            orderlog = params["NotTradingReason"]
                            print(orderlog)
                            write_to_order_logs(orderlog)



                # "buy200":None,"sell200":None,"buy20":None,"sell20":None,"buycrp":None,"sellcpr":None,"45buy":None,"45sell":None,
                #                 "buyday":None,'sellday':None,"buygap":None,"sellgap":None
                # "InitialTrade":None,"BUY":False,"SHORT":False
                if params["TradingEnabled"] == True and start_time <=current_time <= end_time:
                    ltp = float(FivePaisaIntegration.get_ltp(int(params['ScripCode'])))
                    print(f"Symbol: {symbol}, ltp: {ltp}, buy200:{params['buy200']},buy20:{params['buy20']}, "
                          f"buycrp:{params['buycrp']},45buy:{params['45buy']},buygap:{params['buygap']},buyday:{params['buyday']}"
                          f"BUY:{params['BUY']},count:{params['count']},candle_type:{params['candle_type']},high_value:{params['high_value']},")
                    if (
                            params["buy200"]== True and
                            params["buy20"]== True and
                            params["buycrp"]== True and
                            params["45buy"] == True and
                            params["buygap"] == True and
                            params["buyday"] == True and
                            params["BUY"] == False and
                            params["count"] <= params["NoOfCounterTrade"] and
                            (params['candle_type'] == 'MANAGER' or params['candle_type'] == 'WORKER') and
                            ltp >= params["high_value"]
                    ):
                        params["BUY"] = True
                        params["SHORT"] = False
                        params["EntryPrice"] = ltp
                        params["count"] = params["count"] + 1
                        params["InitialTrade"]="BUY"
                        if params["USE_TSL"] ==True:
                            params["NextTslLevel"] = params["high_value"]+params["ATR"]

                        if params['candle_type'] == 'WORKER':
                            stoploss = params["low_value"]
                            params["StoplossValue"] = stoploss
                            diff = params["high_value"] - stoploss
                            params["TargetValue"] = float(diff * params["REWARD_MULTIPLIER_WORKER"])
                            if params["USE_PARTIAL_PROFIT"]==True:
                                params['partialprofitval']= float(diff * params["PartProfitMultipler"])
                                params['partialprofitval'] = params["high_value"]+params["PartProfitMultipler"]
                        if params['candle_type']=='MANAGER':
                            stoploss = params["low_value"]
                            params["StoplossValue"] = stoploss
                            diff = params["high_value"] - stoploss
                            params["TargetValue"] = float(diff * params["REWARD_MULTIPLIER_MANAGER"])
                            if params["USE_PARTIAL_PROFIT"]==True:
                                params['partialprofitval']= float(diff * params["PartProfitMultipler"])
                                params['partialprofitval'] = params["high_value"]+params["PartProfitMultipler"]
                        orderlog = (
                            f"{timestamp} Buy order executed @ {symbol} @ {ltp} @ quantity: {params['Quantity']}, @ candle_type: {params['candle_type']},length={diff}, Target = {params['TargetValue']}"
                            f",Stoploss = {params['StoplossValue']}, partial profit = {params['partialprofitval']} ")
                        print(orderlog)
                        write_to_order_logs(orderlog)



                        # if params['candle_type'] == 'BOSS':
                        #     stoploss = params["low_value"]
                    print(f"Symbol: {symbol}, ltp: {ltp}, sell200:{params['sell200']},sell20:{params['sell20']}"
                          f"sellcpr:{params['sellcpr']},45sell:{params['45sell']},sellday:{params['sellday']},sellgap:{params['sellgap']}"
                          f"SHORT:{params['SHORT']},count:{params['count']},candle_type:{params['candle_type']},low_value:{params['low_value']},")

                    if (
                        params["sell200"] == True and
                        params["sell20"] == True and
                        params["sellcpr"] == True and
                        params["45sell"] == True and
                        params["sellday"] == True and
                        params["sellgap"] == True and
                        params["SHORT"] == False and
                        params["count"] <= params["NoOfCounterTrade"] and
                        (params['candle_type'] == 'MANAGER' or params['candle_type'] == 'WORKER') and
                        ltp <= params["low_value"]
                    ):
                        params["BUY"] =  False
                        params["SHORT"] = True
                        params["EntryPrice"] = ltp
                        params["count"] = params["count"] + 1
                        params["InitialTrade"] = "SHORT"
                        if params["USE_TSL"] ==True:
                            params["NextTslLevel"] = params["high_value"]+params["ATR"]

                        if params['candle_type'] == 'WORKER':
                            stoploss = params["high_value"]
                            params["StoplossValue"] = stoploss
                            diff = stoploss - params["low_value"]
                            params["TargetValue"] = float(diff * params["REWARD_MULTIPLIER_WORKER"])
                            params["TargetValue"] = params["low_value"]-params["TargetValue"]
                            if params["USE_PARTIAL_PROFIT"]==True:
                                params['partialprofitval']= float(diff * params["PartProfitMultipler"])
                                params['partialprofitval'] = params["low_value"]-params["PartProfitMultipler"]

                        if params['candle_type']=='MANAGER':
                            stoploss = params["high_value"]
                            params["StoplossValue"] = stoploss
                            diff = stoploss - params["low_value"]
                            params["TargetValue"] = float(diff * params["REWARD_MULTIPLIER_MANAGER"])
                            params["TargetValue"] = params["low_value"] - params["TargetValue"]
                            if params["USE_PARTIAL_PROFIT"]==True:
                                params['partialprofitval']= float(diff * params["PartProfitMultipler"])
                                params['partialprofitval'] = params["low_value"]-params["PartProfitMultipler"]

                        orderlog = (f"{timestamp} Sell order executed @ {symbol} @ {ltp} @ quantity: {params['Quantity']}, @ candle_type: {params['candle_type']},length={diff}, Target = {params['TargetValue']}"
                                    f",Stoploss = {params['StoplossValue']}, partial profit = {params['partialprofitval']} ")
                        print(orderlog)
                        write_to_order_logs(orderlog)

                    if params["BUY"] == True:
                        if params["USE_TSL"] ==True:
                            # params["NextTslLevel"] = params["high_value"]+params["ATR"]
                            if ltp >= params["NextTslLevel"] and params["NextTslLevel"]>0:
                                params["NextTslLevel"]=params["NextTslLevel"]+params["ATR"]
                                params["StoplossValue"]=params["StoplossValue"]+params["ATR"]
                                orderlog = (f"{timestamp} TSL executed for  buy trade @ {symbol} ,ltp ={ltp} , next tsl level ={params['NextTslLevel'] }, updated sl{params['StoplossValue']}")
                                print(orderlog)
                                write_to_order_logs(orderlog)

                        if(
                                ltp>=params["TargetValue"] and
                                params["TargetValue"]>0 and
                                (
                                 params['candle_type'] == 'MANAGER' or
                                 params['candle_type'] == 'WORKER'
                                )
                        ):
                            params["TargetValue"]=0
                            params["TradingEnabled"] = False
                            orderlog = (f"{timestamp} Target executed for buy trade @ {symbol}")
                            print(orderlog)
                            write_to_order_logs(orderlog)

                        if params["USE_PARTIAL_PROFIT"] == True:
                            if (
                                    ltp>=params['partialprofitval'] and
                                    params['partialprofitval']>0 and
                                (
                                 params['candle_type'] == 'MANAGER' or
                                 params['candle_type'] == 'WORKER'
                                )
                            ):
                                params['partialprofitval']=0
                                orderlog = (f"{timestamp} Partial profit executed for buy trade @ {symbol}")
                                print(orderlog)
                                write_to_order_logs(orderlog)

                        if (
                                ltp <= params["StoplossValue"] and
                                (
                                        params['candle_type'] == 'MANAGER' or
                                        params['candle_type'] == 'WORKER'
                                )and
                                params["StoplossValue"] > 0
                        ):
                            params["StoplossValue"]=0
                            orderlog = (
                                f"{timestamp} Stoploss executed for buy trade @ {symbol}")
                            print(orderlog)
                            write_to_order_logs(orderlog)

                    if params["SHORT"] == True:
                        if ltp <= params["NextTslLevel"] and params["NextTslLevel"] > 0 and params["USE_TSL"] ==True:
                            params["NextTslLevel"] = params["NextTslLevel"] - params["ATR"]
                            params["StoplossValue"] = params["StoplossValue"] - params["ATR"]
                            orderlog = (
                                f"{timestamp} TSL executed for  sell trade @ {symbol} ,ltp ={ltp} , next tsl level ={params['NextTslLevel']}, updated sl{params['StoplossValue']}")
                            print(orderlog)
                            write_to_order_logs(orderlog)

                        if ltp<=params["TargetValue"] and params["TargetValue"]>0:
                            params["TargetValue"]=0
                            params["TradingEnabled"] = False
                            orderlog = (
                                f"{timestamp} Target executed for SELL trade @ {symbol} @ {ltp}")
                            print(orderlog)
                            write_to_order_logs(orderlog)

                        if params["USE_PARTIAL_PROFIT"] == True:
                            if (
                                    ltp<=params['partialprofitval'] and
                                    params['partialprofitval']>0 and
                                (
                                 params['candle_type'] == 'MANAGER' or
                                 params['candle_type'] == 'WORKER'
                                )
                            ):
                                params['partialprofitval']=0
                                orderlog = (f"{timestamp} Partial profit executed for sell trade @ {symbol}")
                                print(orderlog)
                                write_to_order_logs(orderlog)

                        if ltp >= params["StoplossValue"] and params["StoplossValue"] > 0:
                            params["StoplossValue"]=0
                            orderlog = (f"{timestamp} Stoploss executed for SELL trade @ {symbol}")
                            print(orderlog)
                            write_to_order_logs(orderlog)


                    if (
                            params["close_value"] >params["open_value"] and
                            params['candle_type'] == 'BOSS' and
                            params["bigbosstrade"] == False
                    ):
                        params["bigbosstrade"] = True
                        params["bigbosstradetype"] = "SHORT"
                        params["StoplossValue"] = params["ATR"]+params["high_value"]
                        params["TargetValue"] = params['Rangeeee']*params["TargetBossPercentage"]*0.01
                        params["TargetValue"]=params["high_value"]-params["TargetValue"]
                        orderlog = (f"{timestamp} Sell trade executed  @ {symbol},candle_type: {params['candle_type']}, candle size : {params['Rangeeee']}, TP={params['TargetValue']}, SL={params['StoplossValue']}")
                        print(orderlog)
                        write_to_order_logs(orderlog)

                    if (
                            params["close_value"] <params["open_value"] and
                            params['candle_type'] == 'BOSS' and
                            params["bigbosstrade"] == False
                    ):
                        params["bigbosstrade"] = True
                        params["bigbosstradetype"] = "BUY"
                        params["StoplossValue"] =   params["low_value"]-params["ATR"]
                        params["TargetValue"] = params['Rangeeee'] * params["TargetBossPercentage"] * 0.01
                        params["TargetValue"] = params["low_value"] + params["TargetValue"]
                        orderlog = (f"{timestamp} Buy trade executed  @ {symbol},candle_type: {params['candle_type']}, candle size : {params['Rangeeee']}, TP={params['TargetValue']}, SL={params['StoplossValue']}")
                        print(orderlog)
                        write_to_order_logs(orderlog)

                    if params['candle_type'] == 'BOSS' and params["bigbosstrade"] == True:
                        if(
                                params["bigbosstradetype"] == "BUY" and
                                ltp >=params["TargetValue"] and params["TargetValue"]>0
                        ):
                            orderlog = (f"{timestamp} Target executed buy trade {symbol} @ {ltp}")
                            print(orderlog)
                            write_to_order_logs(orderlog)
                            params["TargetValue"] =0

                        if (
                                params["bigbosstradetype"] == "BUY" and
                                ltp <= params["StoplossValue"] and params["StoplossValue"] > 0
                        ):
                            orderlog = (f"{timestamp} Stoploss executed buy trade {symbol} @ {ltp}")
                            print(orderlog)
                            write_to_order_logs(orderlog)
                            params["StoplossValue"] = 0

                    if params['candle_type'] == 'BOSS' and params["bigbosstrade"] == True:
                        if(
                                params["bigbosstradetype"] == "SHORT" and
                                ltp <=params["TargetValue"] and params["TargetValue"]>0
                        ):
                            orderlog = (f"{timestamp} Target executed SHORT trade {symbol} @ {ltp}")
                            print(orderlog)
                            write_to_order_logs(orderlog)
                            params["TargetValue"] =0

                        if (
                                params["bigbosstradetype"] == "SHORT" and
                                ltp >= params["StoplossValue"] and params["StoplossValue"] > 0
                        ):
                            orderlog = (f"{timestamp} Stoploss executed SHORT trade {symbol} @ {ltp}")
                            print(orderlog)
                            write_to_order_logs(orderlog)
                            params["StoplossValue"] = 0

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