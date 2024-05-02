from stock_ticker.helpers import ticker_json_parser
from stock_ticker.utils import fetch_alphavantage_ticker_file


def test_ticker_json_parser_valid():
    data = fetch_alphavantage_ticker_file()
    data = ticker_json_parser(data)

    assert data.get("symbol") == "IBM"
    assert data.get("last_date") == "2023-11-10"
    assert len(data.get("data", {}).get("timestamp")) == 100
    assert len(data.get("data", {}).get("value")) == 100


def test_ticker_json_parser_invalid():
    data = {"Meta Data": {"3. Last Refreshed": "2023-11-10"}}
    data = ticker_json_parser(data)
    assert data == {}

    data = {"Meta Data": {"2. Symbol": "IBM"}}
    data = ticker_json_parser(data)
    assert data == {}
