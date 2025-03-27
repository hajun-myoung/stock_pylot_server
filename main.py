from typing import Union

from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {
        "Server_info": "Stock Pylot Server Side",
        "status_code": 200
    }