import pandas as pd
import numpy as np
import monitor_market
import requests
import time
import hmac
import os
from dotenv import load_dotenv 

load_dotenv()

# API Credentials

API_KEY = os.getenv("Your API Key")
API_SECRET = os.getenv("Your API Secret")
BASE_URL = "https://api.binance.com"

# Settings

SYMBOL = "BTCUSDT"
INTERVAL = "5m"
ATR_PERIOD = 14
LIMIT = 100

# Inflow of Market Data

def get_market_data():
    
    endpoint = "/api/v3/klines"

    parameters = {"symbol":SYMBOL, "interval":INTERVAL, "limit":LIMIT}
    headers = {"X-MBX-APIKEY":API_KEY}

    response = requests.get(BASE_URL + endpoint, params = parameters, headers = headers)
    data = response.json()

    print("data")

    df = pd.DataFrame(data, columns = ["open_time", "open", "high", "low", "close", "volume", "close_time", "quote_asset_value", "number_of_trades", "taker_buy_base", "taker_buy_quote", "ignore"])
    df["high"] = df["high"].astype(float)
    df["low"] = df["low"].astype(float)
    df["close"] = df["close"].astype(float)
    
    return df

def calculate_true_range(df):

    df["prev_close"] = df["close"].shift(1)

    tr1 = df["high"] - df["low"]
    tr2 = (df["high"] - df["prev_close"])
    tr3 = (df["low"] - df["prev_close"])
    tr = pd.concat([tr1, tr2, tr3], axis = 1)
    df["true_range"] = tr.max(axis = 1)

    return df

def calculate_atr(df):

    df["ATR"] = df["true_range"].rolling(ATR_PERIOD).mean()
    return df


# Monitoring

def monitor_market():

    while True:
        
        df = get_market_data()
        df = calculate_true_range(df)
        df = calculate_atr(df)

        latest_price = df["close"].iloc[-1]
        latest_atr = df["ATR"].iloc[-1]

        print("----------------------")
        print(f"Symbol:{SYMBOL}")
        print(f"Price:{latest_price}")
        print(f"ATR(14):{latest_atr:.2f}")

        if latest_atr > df["ATR"].mean():
            print("Volatility is High")
        else:
            print("Volatility is Normal")

        time.sleep(30)

        
if __name__ == "__main__":
    print("Starting ATR(14) Live monitoring tool")
    monitor_market()



