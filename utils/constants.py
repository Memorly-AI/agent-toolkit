import time
from datetime import datetime
import pytz
from dotenv import load_dotenv
import os

load_dotenv()


def get_current_time_in_milliseconds():
    return int(time.time() * 1000)


def get_current_date_and_time_in_utc() -> str:
    utc = pytz.timezone('UTC')
    utc_time = datetime.now(utc)  
    formatted_time = utc_time.strftime('%Y-%m-%d %H:%M') 
    print("UTC Time: ", formatted_time)   
    return formatted_time


def get_current_date_and_time_in_ist() -> str:
    ist = pytz.timezone('Asia/Kolkata')
    ist_time = datetime.now(ist)  
    formatted_time = ist_time.strftime('%Y-%m-%d %H:%M')  
    return formatted_time


def get_env_variable(var_name: str):
    return os.getenv(var_name, None)