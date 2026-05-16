from flask import Blueprint, render_template
from flask import request, jsonify
from app.services.scenario import StockScenario as Scenario
from app.services.strategy_engine import StrategyEngine as Engine
from app.extensions import game_engine

strategy = Blueprint("strategy", __name__, url_prefix="/strategy")

game_engine = Engine()

@strategy.route("/")
def strategy_page():
    return render_template("strategy.html")


@strategy.route("/gameInit")
def game_init():
    global game_engine

    return jsonify(game_engine.gameInit())


@strategy.route("/nextDay")
def nextDay():
    global game_engine

    return jsonify(game_engine.next_day())


@strategy.route("/buy", methods=["POST"])
def buy():
    global game_engine

    data = request.get_json() or {}
    amount = data.get("amount")

    return jsonify(game_engine.buy(amount))


@strategy.route("/sell", methods=["POST"])
def sell():
    global game_engine
    data = request.get_json() or {}
    amount = data.get("amount")

    return jsonify(game_engine.sell(amount))
