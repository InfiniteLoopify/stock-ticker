from flask import render_template, jsonify
from flask import request as flask_request
from flask import Response


from stock_ticker import utils
from stock_ticker.helpers import fetch_and_get_selected_tickers, get_stored_tickers


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
