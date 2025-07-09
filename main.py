from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
import os

from auth import Get_token
from query import GetValue_byDate
from dataProcessing import GetFiltered_clpr
from trade import execute_trade

from pydantic import BaseModel
import pandas as pd

from datetime import datetime, timedelta

from middlewares.dates import get_weekdays_between
from middlewares.handle_array import split_into_chunks

import threading
import time


class StockQuery(BaseModel):
    stock_code: str
    start_date: str
    end_date: str


class TradeRequest(BaseModel):
    code: str
    quantity: int
    isBuy: bool


watchdog_flags = {}
watchdog_threads = {}
app = FastAPI()

# 환경변수 불러오기
load_dotenv(override=True)
appkey = os.getenv("appkey")
appsecret = os.getenv("appsecret")

# 토큰 가져오기
token = Get_token(appkey, appsecret)
# print(token)


@app.get("/")
def read_root():
    return {"Server_info": "Stock Pylot Server Side", "status_code": 200}


def get_data(query: StockQuery):
    try:
        data = GetValue_byDate(
            appkey, appsecret, token, query.stock_code, query.start_date, query.end_date
        )
        result = GetFiltered_clpr(data)
    except Exception as e:
        print(e)
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


@app.post("/trade")
def trade(req: TradeRequest):
    result = execute_trade(
        appkey=appkey,
        appsecret=appsecret,
        token=token,
        code=req.code,
        qty=req.quantity,
        isBuy=req.isBuy,
    )

    return {"status": "success", "result": result}


def check_ma_cross(prices: list[float], short: int, long: int):
    if len(prices) < long + 1:
        return None

    short_ma_prev = sum(prices[-1 - short : -1]) / short
    long_ma_prev = sum(prices[-1 - long : -1]) / long
    short_ma_now = sum(prices[-short - 1 :]) / short
    long_ma_now = sum(prices[-long - 1 :]) / long

    if (short_ma_prev < long_ma_prev) and (short_ma_now > long_ma_now):
        return "buy"
    elif (short_ma_prev > long_ma_prev) and (short_ma_now < long_ma_now):
        return "sell"
    return None


def watchdog_loop(code: str, qty: int, short: int = 15, long: int = 30):
    global watchdog_flags
    try:
        while watchdog_flags.get(code, False):
            print(f"{code} is watching now...")
            curQuery = StockQuery(
                stock_code=code,
                start_date=(datetime.now() - timedelta(days=long)).strftime("%Y%m%d"),
                end_date=datetime.now().strftime("%Y%m%d"),
            )
            prices_df = get_data(curQuery)

            decision = check_ma_cross(prices_df["values"], short, long)
            print(decision)

            if decision:
                execute_trade(appkey, appsecret, token, code, qty, decision == "buy")
            else:
                print(f"[INFO]{code} - No Decision")
            time.sleep(86400)
    except Exception as e:
        print(f"[Error]code: {code}\n {e}")
        time.sleep(86400)
    finally:
        watchdog_flags.pop(code, None)
    return True


class WatchDogStartQuery(BaseModel):
    stock_code: str
    quantity: int


@app.post("/watchdog/start")
def start_watchdog(query: WatchDogStartQuery):
    global watchdog_threads

    if query.stock_code in watchdog_threads:
        return {
            "status": "Failed",
            "message": f"code {query.stock_code} is already watching now",
        }

    watchdog_flags[query.stock_code] = True
    new_thread = threading.Thread(
        target=watchdog_loop, args=(query.stock_code, query.quantity)
    )
    watchdog_threads[query.stock_code] = new_thread
    new_thread.start()
    return {"status": "watching started"}


@app.post("/watchdog/stop/{code}")
def stop_watchdog(code: str):
    global watchdog_flags

    if code in watchdog_flags:
        watchdog_flags[code] = False
        return {"code": code, "status": "stopped"}

    return False
    # return {"watchdog_status": "stopped"}


@app.get("/watchdog/status")
def get_watchdog_status():
    return {
        "status": [
            {"code": code, "watching": flag} for code, flag in watchdog_flags.items()
        ]
    }
