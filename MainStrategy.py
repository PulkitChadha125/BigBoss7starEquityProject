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