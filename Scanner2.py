import FivePaisaIntegration
import time as sleep_time
import pandas as pd
from datetime import datetime
import threading

lock = threading.Lock()
FivePaisaIntegration.login()
symbol_dict={}

def get_user_settings():
    global result_dict
    try:
        df = pd.read_csv('Scanner2.csv')
        pf = pd.read_csv('ScripMaster.csv')
        cashdf = pf[(pf['Exch'] == "N") & (pf['ExchType'] == "C") & (pf['Series'] == "EQ")]
        cashdf['Name'] = cashdf['Name'].str.strip()
        cashdf = cashdf[['ScripCode', 'Name']]
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        for symbol in df['Symbol']:
            try:

                matching_row = cashdf[cashdf['Name'].str.strip() == symbol.strip()]
                if not matching_row.empty:
                    corresponding_timeframe = df[df['Symbol'] == symbol]['timeframe'].iloc[0]
                    spcode = matching_row.iloc[0]['ScripCode']
                    data = FivePaisaIntegration.get_forty_five(spcode,'15m')
                    highest_high_value, lowest_low_value = FivePaisaIntegration.get_forty_five(spcode,'15m')

                    data = FivePaisaIntegration.day_first_candle_avg(spcode, corresponding_timeframe)


                else:
                    print(f"No matching row found for symbol {symbol}")

                symbol_dict[symbol] = {
                    "HighFortyFive":highest_high_value,
                    "LowFortyFive":lowest_low_value,
                    "AverageValue":data
                }

            except Exception as e:
                print("Error happened in fetching symbol", str(e))

    except Exception as e:
        print("Error happened in fetching symbol", str(e))

def savetocsv(symbol_dict):
    df = pd.DataFrame.from_dict(symbol_dict, orient='index')
    df.to_csv('45MinHighLow.csv', index_label='Symbol')

get_user_settings()
savetocsv(symbol_dict)