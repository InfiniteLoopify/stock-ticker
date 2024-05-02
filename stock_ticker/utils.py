import csv
import pytz
import json
import requests
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DATETIME_FORMAT = "%Y-%m-%d"
API_KEY = os.environ.get("API_KEY", "demo")
IFRAME_LINK = os.environ.get("IFRAME_LINK", "")
# API_KEY = "demo"


def to_dict(model, columns: list[str | tuple] | None = None) -> dict:
    d = {}
    try:
        for column in model.__table__.columns:
            columns_exist = isinstance(columns, list) or isinstance(columns, tuple)
            if columns is None or (columns_exist and column.name in columns):
                value = getattr(model, column.name)
                d[column.name] = value
    except Exception as e:
        return {}
    return d


def fetch_alphavantage_ticker_api(ticker: str = "IBM") -> dict:
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={ticker}&apikey={API_KEY}"

    response = requests.request("GET", url, timeout=60)
    return response.json()


def fetch_alphavantage_ticker_file(filepath: str = "files/test.json") -> dict:
    with open(filepath, "r") as f:
        return json.load(f)


def timezone_to_utc(datetime_string: str, timezone: str) -> str:
    local = pytz.timezone(timezone)
    naive = datetime.strptime(datetime_string, DATETIME_FORMAT)
    local_dt = local.localize(naive, is_dst=None)
    utc_dt = local_dt.astimezone(pytz.utc)
    utc_dt = utc_dt.strftime(DATETIME_FORMAT)
    return utc_dt


def csv_to_obj(
    path: str = "files/symbol_list.csv", columns: list[str] | tuple[str] | None = None
):
    obj: list[dict] = []
    try:
        with open(path) as f:
            reader = csv.DictReader(f)
            for row in reader:
                if columns is not None:
                    obj.append({col: row.get(col) for col in columns})
                else:
                    obj.append(row)
    except Exception as e:
        return []
    return obj
