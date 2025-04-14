from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
import os

from auth import Get_token
from query import GetValue_byDate
from dataProcessing import GetFiltered_clpr

from pydantic import BaseModel
import pandas as pd

from middlewares.dates import get_weekdays_between
from middlewares.handle_array import split_into_chunks


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
token = Get_token(appkey, appsecret)
# print(token)


@app.get("/")
def read_root():
    return {"Server_info": "Stock Pylot Server Side", "status_code": 200}


def get_data(query: StockQuery):
    data = GetValue_byDate(
        appkey, appsecret, token, query.stock_code, query.start_date, query.end_date
    )
    result = GetFiltered_clpr(data)
    return result


@app.post("/query_stock/")
def get_value(query: StockQuery):
    if query.start_date > query.end_date:
        raise HTTPException(
            status_code=400, detail="start_date must be before end_date"
        )
    if query.start_date == query.end_date:
        raise HTTPException(
            status_code=400, detail="start_date and end_date must be different"
        )
    if query.start_date == "" or query.end_date == "":
        raise HTTPException(
            status_code=400, detail="start_date and end_date cannot be empty"
        )
    if query.stock_code == "":
        raise HTTPException(status_code=400, detail="stock_code cannot be empty")
    if len(query.stock_code) != 6:
        raise HTTPException(
            status_code=400, detail="stock_code must be 6 characters long"
        )

    # print("Query received:", query)

    weekdays = get_weekdays_between(query.start_date, query.end_date)
    if len(weekdays) <= 99:
        result = get_data(query)
        if result.empty:
            raise HTTPException(status_code=404, detail="No data found")
        return result
    else:
        print("Length: ", len(weekdays))
        results = pd.DataFrame()
        for chunk in split_into_chunks(weekdays, 99):
            print("\n\nNEW CHUNK\n\n")
            print(chunk)
            start_date = chunk[0]
            end_date = chunk[-1]
            query.start_date = start_date
            query.end_date = end_date
            chunk_result = get_data(query)
            results = pd.concat([results, chunk_result], ignore_index=True)

            print("RESULTS")
            print(results)
        if results.empty:
            raise HTTPException(status_code=404, detail="No data found")
        return results
