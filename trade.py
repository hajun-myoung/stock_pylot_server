import requests
import os
import json
from datetime import datetime
from dotenv import load_dotenv

# Some constants
TRADE_LOG_FILE = "./Data/trade_log.json"
ORDER_DOMAIN = "https://openapivts.koreainvestment.com:29443/"
ORDER_URL = "/uapi/domestic-stock/v1/trading/order-cash"

SELL_CODE = "VTTC0011U"
BUY_CODE = "VTTC0012U"


trade_log = None


def log_trade(trade_data):
    """Logs trade data to a JSON file."""
    if not os.path.exists(TRADE_LOG_FILE):
        with open(TRADE_LOG_FILE, "w") as f:
            json.dump([], f)

    with open(TRADE_LOG_FILE, "r+") as f:
        trades = json.load(f)
        trades.append(trade_data)
        f.seek(0)
        json.dump(trades, f, indent=4)

    return trades


def record_trade(code, isBuy, quantity, api_result):
    trade = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "code": code,
        "isBuy": isBuy,
        "quantity": quantity,
        "result": api_result,
    }

    if os.path.exists(TRADE_LOG_FILE):
        with open(TRADE_LOG_FILE, "r") as f:
            trades = json.load(f)
    else:
        trades = []

    trades.append(trade)

    with open(TRADE_LOG_FILE, "w") as f:
        json.dump(trades, f, indent=2)

    return True


def execute_trade(
    appkey: str, appsecret: str, token: str, code: str, qty: int, isBuy: bool
):
    tr_id = BUY_CODE if isBuy else SELL_CODE

    headers = {
        "authorization": token,
        "content-type": "application/json; charset=utf-8",
        "appkey": appkey,
        "appsecret": appsecret,
        "tr_id": tr_id,
        "custtype": "P",
    }

    body = {
        "CANO": "50139072",
        "ACNT_PRDT_CD": "01",
        "PDNO": code,
        "ORD_DVSN": "01",
        "ORD_QTY": f"{qty}",
        "ORD_UNPR": "0",
    }

    print(ORDER_DOMAIN + ORDER_URL)
    print(headers)
    print(body)

    res = requests.post(ORDER_DOMAIN + ORDER_URL, headers=headers, json=body)
    result = res.json()

    record_trade(code, isBuy, qty, result)
    print("Logged!")

    return result
