from flask import Blueprint
import views

view_routes = Blueprint("view_routes", __name__)

view_routes.route("/tickers", methods=["GET"])(views.get_tickers)
view_routes.route("/symbols", methods=["GET"])(views.get_symbols_info)
