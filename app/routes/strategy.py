from flask import Blueprint, render_template

strategy = Blueprint("strategy", __name__)


@strategy.route("/strategy")
def strategy_page():
    return render_template("strategy.html")
