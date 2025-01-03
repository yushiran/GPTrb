import robin_stocks
from robin_stocks import *
import robin_stocks.robinhood as r
import os
import json
import time
import requests
from bs4 import BeautifulSoup
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

import sys
sys.path.append(os.path.join(CURRENT_DIR, '..'))
from src.analysis import get_stock_info, get_company_stock_news

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



def request_get(url, type):
    if type == 'regular':
        response = requests.get(url)
    elif type == 'soup':
        response = requests.get(url)
        response = BeautifulSoup(response.text, 'html.parser')
    return response

def movers_sp500_url():
    return('https://api.robinhood.com/midlands/movers/sp500/')

def get_100_most_popular_url():
    return('https://api.robinhood.com/midlands/tags/tag/100-most-popular/')

def movers_top_url():
    return('https://api.robinhood.com/midlands/tags/tag/top-movers/')

def dig_oppoturnity():
    while True:
        url = movers_top_url()
        data = request_get(url, 'regular')
        data = data.json()
        movers_top_instruments_list = data.get('instruments', [])

        # url = get_100_most_popular_url()
        # data = request_get(url, 'regular')
        # data = data.json()
        # most_popular_instruments_list = data.get('instruments', [])

        # combined_instruments = list(set(movers_top_instruments_list + most_popular_instruments_list))
        combined_instruments = movers_top_instruments_list

        # Clear the dig_oppo directory
        dig_oppo_dir = f"{CURRENT_DIR}/../for_gpt_file/market/dig_oppo/"
        if os.path.exists(dig_oppo_dir):
            for root, dirs, files in os.walk(dig_oppo_dir, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))

        symbol_list = []
        for instrument_url in combined_instruments:
            instrument_data = request_get(instrument_url, 'regular').json()
            symbol = instrument_data.get('symbol')
            if symbol:
                symbol_list.append(symbol)
                # Save the stock history and news to a CSV and JSON file respectively
                history = get_stock_info(symbol)
                history_path = f"{CURRENT_DIR}/../for_gpt_file/market/dig_oppo/{symbol}/{symbol}_stock_history.csv"
                os.makedirs(os.path.dirname(history_path), exist_ok=True)
                history.to_csv(history_path)
                # Get the news for the stock
                news = get_company_stock_news(symbol)
                news_path = f"{CURRENT_DIR}/../for_gpt_file/market/dig_oppo/{symbol}/{symbol}_news.json"
                os.makedirs(os.path.dirname(news_path), exist_ok=True)
                with open(news_path, 'w') as json_file:
                    json.dump(news, json_file, indent=4)
                time.sleep(1.5)
        
        time.sleep(2 * 60 * 60)

if __name__ == '__main__':
    dig_oppoturnity()