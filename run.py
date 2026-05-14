from app import create_app
from app.extensions import game_engine
from app.services.strategy_engine import StrategyEngine

app = create_app()

game_engine = StrategyEngine()

# print(app.url_map) # Blueprint API測試

if __name__ == "__main__":
    app.run(debug=True)
