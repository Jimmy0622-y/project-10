from app.watchlist import WATCHLIST
from app.services.models import StockAnalyzer
from app.services.scenario import StockScenario as Scenario
from dataclasses import asdict
import random

INITIAL_FUNDS = 1000000  # 初始資金


class TradeRecord:
    day: int
    action: str  # "buy" / "sell"
    price: float
    amount: int
    cash: float
    stock: int
    total_value: float


class StrategyEngine:
    def __init__(self, cash=INITIAL_FUNDS):
        self.reset(cash)

    def reset(self, cash=INITIAL_FUNDS):
        # 隨機股票
        self.symbol = random.choice(WATCHLIST)

        # 股票分析器
        self.analyzer = StockAnalyzer()

        # 抓資料
        self.df = self.analyzer.fetch_stock_data(self.symbol)

        if self.df is None or len(self.df) < 200:
            raise ValueError(f"{self.symbol} 資料不足")

        # 建立模擬視窗
        self.window = Scenario(self.df).rolling_windows()

        # 初始資金
        self.day = 1
        self.initial_cash = cash
        self.cash = self.initial_cash
        self.stock = 0

        # 產生圖表
        self.chart_path = self.analyzer.generate_candlestick_chart(self.df, self.symbol)

        self.macd_path = self.analyzer.generate_macd_chart(self.df, self.symbol)

        self.update_price()

        # 交易紀錄
        self.history = []

    def gameInit(self):
        self.reset()
        return self.get_init_state()

    # =========================
    # next day（核心）
    # =========================
    def next_day(self):
        result = self.window.next()

        if result is None:
            return {"success": False, "message": "遊戲結束"}

        self.day += 1
        self.update_price()

        print("DAY:", self.day)

        return self.get_next_day_state()

    # =========================
    # buy
    # =========================
    def buy(self, amount: int):

        cost = self.price * amount

        if cost > self.cash:
            return False

        self.cash -= cost
        self.stock += amount
        self.update_price()

        self._log("buy", self.price, amount)
        return self.get_trade_state()

    # =========================
    # sell
    # =========================
    def sell(self, amount: int):

        if self.stock <= 0:
            return False

        amount = min(amount, self.stock)

        self.update_price()

        self.cash += self.price * amount
        self.stock -= amount

        self._log("sell", self.price, amount)
        return self.get_trade_state()

    # =========================
    # log
    # =========================
    def _log(self, action, price, amount):
        self.history.append(
            {
                "day": self.day,
                "action": action,
                "price": price,
                "amount": amount,
                "cash": self.cash,
                "stock": self.stock,
            }
        )

    # ---------------------------
    # 資產計算
    # ---------------------------

    def get_pnl(self):
        portfolio = self.cash + self.stock * self.price
        return portfolio - self.initial_cash

    def update_price(self):
        state = self.window.current_state()
        self.price = float(state.iloc[-1]["Close"])
        return self.price

    # ---------------------------
    # 回傳格式
    # ---------------------------

    def base_state(self):
        return {
            "symbol": self.symbol,
            "price": self.price,
        }

    def portfolio_state(self):
        return {
            "cash": round(self.cash, 2),
            "stock": self.stock,
            "pnl": round(self.get_pnl(), 2),
        }

    def market_state(self):
        return {
            "day": self.day,
            "chart": self.chart_path,
            "macd": self.macd_path,
        }

    def get_init_state(self):
        return {
            "success": True,
            **self.base_state(),
            **self.portfolio_state(),
            **self.market_state(),
        }

    def get_next_day_state(self):
        return {
            "success": True,
            **self.market_state(),
            "price": self.price,
            "pnl": round(self.get_pnl(), 2),
        }

    def get_trade_state(self):
        return {
            "success": True,
            **self.portfolio_state(),
            "price": self.price,
        }

    # ---------------------------
    # 轉換給前端用
    # ---------------------------
    def history_dict(self):
        return self.history.to_dict(orient="records")
