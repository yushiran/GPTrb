from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, KeywordTableIndex
from llama_index.llms.openai import OpenAI
import json
from dotenv import load_dotenv
load_dotenv()
import os
import time
import robin_stocks
from robin_stocks import *
import robin_stocks.robinhood as r

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
import sys
sys.path.append(os.path.join(CURRENT_DIR, '..'))
from src.analysis import get_stock_info, get_company_stock_news
from src.redbook_sender import string_to_vertical_image
prompt_file = f"{CURRENT_DIR}/../json/prompt.json"

def gpt_funtion(object:str):
    with open(prompt_file, "r") as file:
        prompt = json.load(file)
    prompt = prompt["stock_anlysis"]
    llm = OpenAI(temperature=0.1, model="gpt-4o")
    documents = SimpleDirectoryReader(f"{CURRENT_DIR}/../for_gpt_file/{object}").load_data()
    index = VectorStoreIndex.from_documents(documents,llm=llm)
    query_engine = index.as_query_engine()
    response = query_engine.query(prompt)
    # print(response)
    return response

def anysis_market():
    with open(prompt_file, "r") as file:
        prompt_list = json.load(file)
    prompt = prompt_list["general_recommendation"]
    llm = OpenAI(temperature=0.1, model="gpt-4o")
    documents = SimpleDirectoryReader(f"{CURRENT_DIR}/../for_gpt_file/market/general_stock_news").load_data()
    index = VectorStoreIndex.from_documents(documents,llm=llm)
    query_engine = index.as_query_engine()
    response = query_engine.query(prompt)
    stock_list = [stock.strip() for stock in str(response).split(',')]

    response = "today's recommendation: \n" + str(response) + "\n"

    for stock in stock_list:
        news = get_company_stock_news(stock)
        history = get_stock_info(stock)
        news_path = f"{CURRENT_DIR}/../for_gpt_file/market/{stock}/{stock}_news.json"
        history_path = f"{CURRENT_DIR}/../for_gpt_file/market/{stock}/{stock}_stock_history.csv"
        os.makedirs(os.path.dirname(news_path), exist_ok=True)
        os.makedirs(os.path.dirname(history_path), exist_ok=True)
        with open(news_path, 'w') as json_file:
            json.dump(news, json_file, indent=4)
        history.to_csv(history_path)

        potential_stock_file_path  = f"{CURRENT_DIR}/../for_gpt_file/market/{stock}"
        doucments = SimpleDirectoryReader(potential_stock_file_path).load_data()
        index = VectorStoreIndex.from_documents(doucments, llm=llm)
        query_engine = index.as_query_engine()
        prompt = prompt_list["forecast_stock"]
        stock_forecast = query_engine.query(prompt)

        response = response + stock+": " + str(stock_forecast) + "\n"

    # print(response)
    return response

def find_opportunity():
    with open(prompt_file, "r") as file:
        prompt = json.load(file)
    prompt = prompt["opportunity"]
    llm = OpenAI(temperature=0.1, model="gpt-4o")
    documents = []
    base_path = f"{CURRENT_DIR}/../for_gpt_file/market/dig_oppo"
    for folder in os.listdir(base_path):
        folder_path = os.path.join(base_path, folder)
        if os.path.isdir(folder_path):
            documents.extend(SimpleDirectoryReader(folder_path).load_data())
    index = VectorStoreIndex.from_documents(documents,llm=llm)
    query_engine = index.as_query_engine()
    response = query_engine.query(prompt)
    response = "高风险opportunity: \n" + str(response)
    return response
    
def gpt_main():
    while True:
        current_time = time.localtime()
        if (current_time.tm_hour == 15 and current_time.tm_min == 30) or ( current_time.tm_hour == 18 and current_time.tm_min == 30):
            gpt_advice = []

            gpt_advice.append(time.strftime('%Y-%m-%d %H:%M:%S', current_time))

            folders = [f.name for f in os.scandir(f"{CURRENT_DIR}/../for_gpt_file") if f.is_dir() and f.name != "market"]
            for folder in folders:
                gpt_advice.append(gpt_funtion(folder))

            gpt_advice.append(anysis_market())

            gpt_advice.append(find_opportunity())

            with open(f"{CURRENT_DIR}/../json/today_recommadation.txt", "w") as file:
                for advice in gpt_advice[-2:]:
                    file.write(str(advice) + "\n")

            # 转换为图片
            txt_file_path = f"{CURRENT_DIR}/../json/today_recommadation.txt"
            with open(txt_file_path, 'r', encoding='utf-8') as file:
                text = file.read().strip()
            output_image_path = f"{CURRENT_DIR}/../json/today_recommedation.png"
            imgae_path = string_to_vertical_image(text=text, output_path=output_image_path)

            with open(f"{CURRENT_DIR}/../json/gpt_advice.txt", "w") as file:
                for advice in gpt_advice:
                    file.write(str(advice) + "\n")

            print(f"finish gpt, time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}")
            
            time.sleep(5)

def gpt_main_pipeline():
    print("start gpt main")

    current_time = time.localtime()
    gpt_advice = []

    gpt_advice.append(time.strftime('%Y-%m-%d %H:%M:%S', current_time))

    folders = [f.name for f in os.scandir(f"{CURRENT_DIR}/../for_gpt_file") if f.is_dir() and f.name != "market"]
    for folder in folders:
        gpt_advice.append(gpt_funtion(folder))

    gpt_advice.append(anysis_market())

    gpt_advice.append(find_opportunity())

    with open(f"{CURRENT_DIR}/../json/today_recommadation.txt", "w") as file:
        for advice in gpt_advice[-2:]:
            file.write(str(advice) + "\n")

    # 转换为图片
    txt_file_path = f"{CURRENT_DIR}/../json/today_recommadation.txt"
    with open(txt_file_path, 'r', encoding='utf-8') as file:
        text = file.read().strip()
    output_image_path = f"{CURRENT_DIR}/../json/today_recommedation.png"
    imgae_path = string_to_vertical_image(text=text, output_path=output_image_path)

    with open(f"{CURRENT_DIR}/../json/gpt_advice.txt", "w") as file:
        for advice in gpt_advice:
            file.write(str(advice) + "\n")

    print(f"finish gpt, time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}")
    

if __name__=='__main__':
    gpt_main()
