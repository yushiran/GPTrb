from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
import json
from dotenv import load_dotenv
load_dotenv()
import os
import time
import robin_stocks
from robin_stocks import *
import robin_stocks.robinhood as r

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

def gpt_funtion(action:str,object:str):
    with open(f"{CURRENT_DIR}/../prompt.json", "r") as file:
        prompt = json.load(file)
    prompt = prompt[action]

    if object == "general":
        documents = SimpleDirectoryReader(f"{CURRENT_DIR}/../for_gpt_file/market").load_data()
    else:
        documents = SimpleDirectoryReader(f"{CURRENT_DIR}/../for_gpt_file/{object}").load_data()
    
    index = VectorStoreIndex.from_documents(documents)
    query_engine = index.as_query_engine()
    response = query_engine.query(prompt)
    print(response)
    return response

def gpt_main():
    while True:
        current_time = time.localtime()
        if current_time.tm_hour == 12 and current_time.tm_min == 0:
            gpt_advice = []
            folders = [f.name for f in os.scandir(f"{CURRENT_DIR}/../for_gpt_file") if f.is_dir() and f.name != "market"]
            for folder in folders:
                gpt_advice.append(gpt_funtion("stock_anlysis", folder))

            gpt_advice.append(gpt_funtion("general_recommendation", "general"))
            with open(f"{CURRENT_DIR}/../json/gpt_advice.txt", "w") as file:
                for advice in gpt_advice:
                    file.write(str(advice) + "\n")

            print(f"finish gpt, time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}")
            
        # time.sleep(60*60)  # Sleep for 60 seconds to avoid running multiple times within the same minute

if __name__=='__main__':
    gpt_main()
