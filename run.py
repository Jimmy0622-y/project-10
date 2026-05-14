from app import create_app
from app.services.strategy_engine import StrategyEngine

app = create_app()

game_engine = StrategyEngine()


if __name__ == "__main__":
    app.run(debug=True)