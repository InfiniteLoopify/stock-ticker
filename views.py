from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from typing import Any, Union
from flask import make_response, url_for, render_template, jsonify
from flask import request as flask_request
from flask import Response
from models import db, Ticker
import utils


def display_template() -> str:
    link = utils.IFRAME_LINK
    return render_template("index.html", link=link)


def get_symbols_info() -> tuple[Response, int]:
    columns = flask_request.args.get("columns", "Symbol,Name,Country")
    columns = list(set(columns.split(",")))
    response = utils.csv_to_obj(columns=columns)
    return jsonify(response), 200


def get_tickers() -> tuple[Response, int]:
    tickers = flask_request.args.get("symbols", "")
    tickers = list(set(tickers.upper().split()))

    show_all = flask_request.args.get("all", "")
    show_all = True if show_all.lower() == "true" else False

    if show_all:
        return get_stored_tickers(list_all=show_all)
    return fetch_and_get_selected_tickers(tickers)


def get_stored_tickers(
    tickers: list[str] | None = None, list_all: bool = False
) -> tuple[Response, int]:
    if not list_all and not tickers:
        return (
            jsonify(
                {"Error": "Ticker(s) not found. Check if `symbols` query is correct."}
            ),
            404,
        )

    users = db.session.query(Ticker)
    if not list_all and tickers:
        users = users.filter(Ticker.name.in_(tickers))
    users = users.all()
    users = [utils.to_dict(user, ["name", "data"]) for user in users]
    return jsonify(users), 200


def fetch_and_get_selected_tickers(tickers: list[str]) -> tuple[Response, int]:
    tickers_found = []
    tickers_not_found = []

    for ticker in tickers:
        ticker_search = db.session.query(Ticker).filter_by(name=ticker).first()
        ticker_outdated = None if not ticker_search else ticker_search.last_updated

        if ticker_outdated:
            ticker_outdated = datetime.strptime(ticker_outdated, utils.DATETIME_FORMAT)
            ticker_outdated = ticker_outdated < datetime.now() - timedelta(hours=48)

        if ticker_search and not ticker_outdated:
            tickers_found.append(ticker)
        else:
            tickers_not_found.append(ticker)

    tickers_json = fetch_tickers_json(tickers_not_found)
    tickers_json = [ticker_json_parser(ticker) for ticker in tickers_json]
    tickers_json = [ticker for ticker in tickers_json if ticker]
    tickers_updated = [ticker.get("symbol") for ticker in tickers_json]

    for ticker in tickers_json:
        ticker_insert_or_update(ticker)

    tickers = tickers_found + tickers_updated
    return get_stored_tickers(tickers)


def ticker_insert_or_update(ticker_json: dict) -> None:
    symbol = ticker_json.get("symbol", "")
    last_date = ticker_json.get("last_date", "")
    data = ticker_json.get("data", {})

    ticker_obj = db.session.query(Ticker).filter_by(name=symbol).first()
    if ticker_obj:
        ticker_obj.last_updated = last_date
        ticker_obj.data = data
    else:
        ticker_obj = Ticker(name=symbol, last_updated=last_date, data=data)  # type: ignore
        db.session.add(ticker_obj)
    db.session.commit()


def fetch_tickers_json(tickers: list[str]) -> list[dict]:
    results = None

    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(
            executor.map(utils.fetch_alphavantage_ticker_api, tickers, timeout=20)
        )
        # results = list(executor.map(utils.fetch_alphavantage_ticker_file, tickers, timeout=20))

    return results


def ticker_json_parser(data: dict) -> dict:
    meta_data = data.get("Meta Data", {})
    symbol = meta_data.get("2. Symbol", "").upper()
    # timezone = meta_data.get("5. Time Zone")

    last_date = meta_data.get("3. Last Refreshed")
    # last_date = timezone_to_utc(datetime=last_date, timezone=timezone)

    points = data.get("Time Series (Daily)", {})
    # data = {timezone_to_utc(key, timezone): data[key]["4. close"] for key in data}
    points = {key: float(points[key].get("4. close", "0.0")) for key in points}
    # points
    points = sorted(
        points.items(), key=lambda x: datetime.strptime(x[0], utils.DATETIME_FORMAT)
    )
    points = dict(points)
    points_x = list(points.keys())
    points_y = list(points.values())
    points = {"timestamp": points_x, "value": points_y}

    if symbol and last_date and points:
        return {"symbol": symbol, "last_date": last_date, "data": points}
    return {}
