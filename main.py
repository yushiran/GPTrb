import robin_stocks
from robin_stocks import *
import robin_stocks.robinhood as r
import pyotp
from dotenv import load_dotenv
load_dotenv()
import os
import json
import threading
# Simple credential specifications - a better method is mentioned
# in the docs.
USERNAME = os.getenv("RH_USERNAME")
PASSWORD = os.getenv("RH_PASSWORD")
alphanumeric_code = os.getenv("alphanumeric_code")

from src import *
from src.follow_MyStock import save_holdings,dig_oppoturnity,save_holdings_pipeline,dig_oppoturnity_pipeline
from src.analysis import analysis_main,analysis_main_pipeline
from src.gpt import gpt_main,gpt_main_pipeline
from src.mail import mail_main,mail_main_pipeline
from src.redbook_sender import rb_main_pipeline,rb_main

def main():
    totp  = pyotp.TOTP(alphanumeric_code).now()
    print(totp)
    login = r.login(USERNAME, PASSWORD, mfa_code=totp)

    threading_list = []
    threading_list.append(threading.Thread(target=save_holdings))
    threading_list.append(threading.Thread(target=dig_oppoturnity))
    threading_list.append(threading.Thread(target=analysis_main))
    threading_list.append(threading.Thread(target=gpt_main))
    threading_list.append(threading.Thread(target=mail_main))

    for thread in threading_list:
        thread.start()

    # Keep the main thread running to allow the save_holdings thread to run indefinitely
    try:
        while True:
            pass
    except KeyboardInterrupt:
        r.logout()
        print("Exiting...")

def pipeline_main():
    totp  = pyotp.TOTP(alphanumeric_code).now()
    print(totp)
    login = r.login(USERNAME, PASSWORD, mfa_code=totp) 

    save_holdings_pipeline()
    dig_oppoturnity_pipeline()
    analysis_main_pipeline()
    gpt_main_pipeline()
    mail_main_pipeline()
    rb_main_pipeline()

    r.logout()
    print("Exiting...")

if __name__ == '__main__':
    # main() 
    pipeline_main()