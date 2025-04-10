from fastapi import FastAPI
from dotenv import load_dotenv
import os

from auth import Get_token
from query import GetValue_byDate
from dataProcessing import GetFiltered_clpr

from pydantic import BaseModel

class StockQuery(BaseModel):
    stock_code: str
    start_date: str
    end_date: str


app = FastAPI()

# 환경변수 불러오기
load_dotenv(override=True)
appkey = os.getenv("appkey")
appsecret = os.getenv("appsecret")
token_generation_time = os.getenv("token_generation_time")

# 토큰 가져오기
token = Get_token(appkey,appsecret)
# print(token)

@app.get("/")
def read_root():
    return {
        "Server_info": "Stock Pylot Server Side",
        "status_code": 200
    }

@app.post("/query_stock/")
def get_value(query: StockQuery):
    print("Request received")
    data = GetValue_byDate(appkey, appsecret, token, query.stock_code, query.start_date, query.end_date)
    result = GetFiltered_clpr(data)
    return result