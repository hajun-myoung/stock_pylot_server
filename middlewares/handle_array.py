import pandas as pd


def split_into_chunks(dates, chunk_size: int = 99):
    for i in range(0, len(dates), chunk_size):
        print("GENERATING CHUNK")
        print(dates[i : i + chunk_size])
        yield dates[i : i + chunk_size]
