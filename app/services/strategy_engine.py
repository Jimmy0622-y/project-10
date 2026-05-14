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
        self.day = 0
        self.cash = cash
        self.stock = 0
        self.initial_cash = cash

        # 產生圖表
        self.chart_path = self.analyzer.generate_candlestick_chart(self.symbol)

        self.macd_path = self.analyzer.generate_macd_chart(self.symbol)

        # 交易紀錄
        self.history = []

    # =========================
    # next day（核心）
    # =========================
    def next_day(self):

        self.day += 1

        # 避免超界
        if self.day >= len(self.df):
            return {"done": True, "msg": "simulation finished"}

        row = self.df.iloc[self.day]
        price = float(row["Close"])

        portfolio_value = self.cash + self.stock * price
        pnl = portfolio_value - self.initial_cash
        pnl_pct = (pnl / self.initial_cash) * 100

        self.generate_candlestick_chart(self.symbol)
        self.generate_macd_chart(self.symbol)

        return {
            "day": self.day,
            "price": price,
            "cash": round(self.cash, 2),
            "stock": self.stock,
            "pnl": round(pnl, 2),
            "pnl_pct": round(pnl_pct, 2),
        }

    # =========================
    # buy
    # =========================
    def buy(self, price: float, amount: int):
        cost = price * amount

        if cost > self.cash:
            return False

        self.cash -= cost
        self.stock += amount

        self._log("buy", price, amount)
        return True

    # =========================
    # sell
    # =========================
    def sell(self, price: float, amount: int):
        if self.stock <= 0:
            return False

        amount = min(amount, self.stock)

        self.cash += price * amount
        self.stock -= amount

        self._log("sell", price, amount)
        return True

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
    def portfolio_value(self, current_price: float):
        return self.cash + self.stock * current_price

    def state(self):

        state_df = self.window.current_state()

        price = float(state_df.iloc[-1]["Close"])

        portfolio = self.cash + self.stock * price

        pnl = portfolio - self.initial_cash

        return {
            "day": self.window.cursor,
            "symbol": self.symbol,
            "price": price,
            "cash": round(self.cash, 2),
            "stock": self.stock,
            "pnl": round(pnl, 2),
            # 🔥 圖路徑
            "chart": self.chart_path,
            "macd": self.macd_path,
        }

    # ---------------------------
    # 轉換給前端用
    # ---------------------------
    def history_dict(self):
        return [asdict(h) for h in self.history]
