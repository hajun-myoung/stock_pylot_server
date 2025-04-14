import requests
import os
from dotenv import load_dotenv


def Get_token(appkey: str, appsecret: str):
    url = "https://openapi.koreainvestment.com:9443/oauth2/tokenP"

    headers = {"Content-Type": "application/json"}

    data = {
        "grant_type": "client_credentials",
        "appkey": appkey,
        "appsecret": appsecret,
    }
    res = requests.post(url, headers=headers, json=data)

    try:
        access_token = f"{res.json()['token_type']} {res.json()['access_token']}"
    except Exception as error:
        if res.json()["error_code"] == "EGW00133":
            print("Too fast to get new Token. Use saved one.")
            load_dotenv(override=True)
            access_token = os.getenv("token")
        else:
            print(error)
            print(res.json())

    return access_token
