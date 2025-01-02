import robin_stocks
from robin_stocks import *
import robin_stocks.robinhood as r
import os
import json
import time
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

def save_holdings():
    while True:
        my_stocks = r.build_holdings()
        # for key, value in my_stocks.items():
        #     print(key, value)
        # Save the holdings to a JSON file with the current timestamp
        my_stocks['timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S')
        with open(f'{CURRENT_DIR}/../json/holdings.json', 'w') as json_file:
            json.dump(my_stocks, json_file, indent=4)
        
        print(f"finish follow stock action, time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}")

        time.sleep(5)