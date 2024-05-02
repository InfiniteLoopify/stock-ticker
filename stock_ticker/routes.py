from flask import Blueprint
from stock_ticker import views

view_routes = Blueprint("view_routes", __name__)


view_routes.route("/", methods=["GET"])(views.display_template)
view_routes.route("/symbols", methods=["GET"])(views.get_symbols_info)
view_routes.route("/tickers", methods=["GET"])(views.get_tickers)
