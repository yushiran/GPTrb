import yfinance as yf
import json
import os
import time
import robin_stocks
from robin_stocks import *
import pandas as pd
import robin_stocks.robinhood as r
import finnhub
from datetime import datetime, timedelta

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# 获取单只股票的详细信息
def get_stock_info(symbol):
    stock = yf.Ticker(symbol)
    # 获取历史数据
    history = stock.history(period="3mo")  # 获取最近1个月的历史数据

    return history

def read_my_stocks(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def get_general_stock_news():
    finnhub_client = finnhub.Client(api_key=os.getenv("finnhub_api_key"))
    general_stock_news = finnhub_client.general_news('general', min_id=0)
    return general_stock_news

def get_company_stock_news(company):
    finnhub_client = finnhub.Client(api_key=os.getenv("finnhub_api_key"))
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')
    company_stock_news = finnhub_client.company_news(company, _from=start_date, to=end_date)
    company_stock_news = company_stock_news[:5]
    return company_stock_news

def analysis_main():
    while True:
        my_stock_file_path = f"{CURRENT_DIR}/../json/holdings.json"

        # 读取json文件
        json_data = read_my_stocks(my_stock_file_path)
        stock_names = [key for key in json_data.keys() if key != 'timestamp']
        for stock_name in stock_names:
            stock_info = json_data[stock_name]
            stock_info['timestamp'] = json_data['timestamp']
            # 保存stock info到本地json文件
            stock_info_path = f"{CURRENT_DIR}/../for_gpt_file/{stock_name}/{stock_name}_holding_info.json"
            os.makedirs(os.path.dirname(stock_info_path), exist_ok=True)
            with open(stock_info_path, 'w') as json_file:
                json.dump(stock_info, json_file, indent=4)

            # 保存stock history到本地csv
            history = get_stock_info(stock_name)
            csv_path = f"{CURRENT_DIR}/../for_gpt_file/{stock_name}/{stock_name}_history.csv"
            history.to_csv(csv_path)

            #获取公司新闻
            company_stock_news = get_company_stock_news(stock_name)
            company_news_path = f"{CURRENT_DIR}/../for_gpt_file/{stock_name}/{stock_name}_news.json"
            with open(company_news_path, 'w') as json_file:
                json.dump(company_stock_news, json_file, indent=4)

        general_stock_news = get_general_stock_news()
        general_news_path = f"{CURRENT_DIR}/../for_gpt_file/market/general_stock_news/general_stock_news.json"
        os.makedirs(os.path.dirname(general_news_path), exist_ok=True)
        with open(general_news_path, 'w') as json_file:
            json.dump(general_stock_news, json_file, indent=4)
        
        print(f"finish analysis action, time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}")

        time.sleep(1 * 60)

def analysis_main_pipeline():
    my_stock_file_path = f"{CURRENT_DIR}/../json/holdings.json"

    # 读取json文件
    json_data = read_my_stocks(my_stock_file_path)
    stock_names = [key for key in json_data.keys() if key != 'timestamp']
    for stock_name in stock_names:
        stock_info = json_data[stock_name]
        stock_info['timestamp'] = json_data['timestamp']
        # 保存stock info到本地json文件
        stock_info_path = f"{CURRENT_DIR}/../for_gpt_file/{stock_name}/{stock_name}_holding_info.json"
        os.makedirs(os.path.dirname(stock_info_path), exist_ok=True)
        with open(stock_info_path, 'w') as json_file:
            json.dump(stock_info, json_file, indent=4)

        # 保存stock history到本地csv
        history = get_stock_info(stock_name)
        csv_path = f"{CURRENT_DIR}/../for_gpt_file/{stock_name}/{stock_name}_history.csv"
        history.to_csv(csv_path)

        #获取公司新闻
        company_stock_news = get_company_stock_news(stock_name)
        company_news_path = f"{CURRENT_DIR}/../for_gpt_file/{stock_name}/{stock_name}_news.json"
        with open(company_news_path, 'w') as json_file:
            json.dump(company_stock_news, json_file, indent=4)

    general_stock_news = get_general_stock_news()
    general_news_path = f"{CURRENT_DIR}/../for_gpt_file/market/general_stock_news/general_stock_news.json"
    os.makedirs(os.path.dirname(general_news_path), exist_ok=True)
    with open(general_news_path, 'w') as json_file:
        json.dump(general_stock_news, json_file, indent=4)
    
    print(f"finish analysis action, time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}")

if __name__ == '__main__':
    analysis_main()