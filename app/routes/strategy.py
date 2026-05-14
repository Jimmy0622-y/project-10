from flask import Blueprint, render_template
from flask import request, jsonify
from app.services.scenario import StockScenario as Scenario
from app.services.strategy_engine import StrategyEngine as Engine

strategy = Blueprint("strategy", __name__, url_prefix="/strategy")


@strategy.route("/")
def strategy_page():
    return render_template("strategy.html")


@strategy.route("/gameInit")
def game_init():
    global game_engine

    game_engine = Engine()

    return jsonify(game_engine.state())


@strategy.route("/nextDay")
def nextDay():
    global game_engine

    game_engine.nextDay()
    return {"day": game_engine.day}


@strategy.route("/buy", methods=["POST"])
def buy():
    data = request.get_json() or {}
    price = data.get("price")
    amount = data.get("amount")
    if price is None or amount is None:
        return {"error": "invalid input"}, 400

    global game_engine
    game_engine.buy(data["price"], data["amount"])
    return jsonify({"status": "ok"})


@strategy.route("/sell", methods=["POST"])
def sell():
    data = request.get_json() or {}
    price = data.get("price")
    amount = data.get("amount")
    if price is None or amount is None:
        return {"error": "invalid input"}, 400

    global game_engine
    game_engine.sell(data["price"], data["amount"])
    return jsonify({"status": "ok"})
