from app.watchlist import WATCHLIST
from app.services.models import StockAnalyzer
from app.services.scenario import StockScenario as Scenario
from dataclasses import asdict
import random

INITIAL_FUNDS = 1000000  # 初始資金
SIMULATION_DAYS = 30


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
        self.window = Scenario(self.df).rolling_windows(test_days=SIMULATION_DAYS - 1)

        # 初始資金
        self.day = 1
        self.initial_cash = cash
        self.cash = self.initial_cash
        self.stock = 0

        # 產生圖表
        self.update_price()
        self._update_charts()

        # 交易紀錄
        self.history = []
        self.daily_history = []
        self._record_daily_state()

    def gameInit(self):
        self.reset()
        return self.get_init_state()

    # =========================
    # next day（核心）
    # =========================
    def next_day(self):
        if self.is_completed():
            return self.get_next_day_state()

        result = self.window.next()

        if result is None:
            return {"success": False, "message": "遊戲結束"}

        self.day += 1
        self.update_price()
        self._update_charts()
        self._record_daily_state()

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
        self._record_daily_state()
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
        self._record_daily_state()
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

    def _update_charts(self):
        state = self.window.current_state()
        self.chart_path = self.analyzer.generate_candlestick_chart(state, self.symbol)
        self.macd_path = self.analyzer.generate_macd_chart(state, self.symbol)

    def _current_market_row(self):
        return self.window.current_state().iloc[-1]

    def _rounded_value(self, row, name):
        value = row.get(name)
        if value is None or value != value:
            return None
        return round(float(value), 2)

    def _record_daily_state(self):
        latest = self._current_market_row()
        date = latest.get("Date")
        if hasattr(date, "strftime"):
            date = date.strftime("%Y-%m-%d")

        trades = [trade for trade in self.history if trade["day"] == self.day]
        total_value = self.cash + self.stock * self.price
        record = {
            "day": self.day,
            "date": date,
            "price": round(self.price, 2),
            "sma5": self._rounded_value(latest, "SMA5"),
            "sma20": self._rounded_value(latest, "SMA20"),
            "rsi": self._rounded_value(latest, "RSI"),
            "macd": self._rounded_value(latest, "MACD"),
            "macd_signal": self._rounded_value(latest, "MACD_SIGNAL"),
            "macd_hist": self._rounded_value(latest, "MACD_HIST"),
            "cash": round(self.cash, 2),
            "stock": self.stock,
            "total_value": round(total_value, 2),
            "pnl": round(total_value - self.initial_cash, 2),
            "trades": trades,
        }

        if self.daily_history and self.daily_history[-1]["day"] == self.day:
            self.daily_history[-1] = record
        else:
            self.daily_history.append(record)

    def is_completed(self):
        return self.day >= SIMULATION_DAYS

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

    def indicator_state(self):
        latest = self._current_market_row()

        return {
            "sma5": self._rounded_value(latest, "SMA5"),
            "sma20": self._rounded_value(latest, "SMA20"),
            "rsi": self._rounded_value(latest, "RSI"),
        }

    def final_report(self):
        final_value = self.cash + self.stock * self.price
        total_return = (
            (final_value - self.initial_cash) / self.initial_cash * 100
            if self.initial_cash
            else 0
        )

        return {
            "summary": {
                "initial_cash": round(self.initial_cash, 2),
                "final_cash": round(self.cash, 2),
                "final_stock": self.stock,
                "final_price": round(self.price, 2),
                "final_value": round(final_value, 2),
                "pnl": round(final_value - self.initial_cash, 2),
                "return_pct": round(total_return, 2),
                "trade_count": len(self.history),
            },
            "daily_history": self.daily_history,
            "trade_history": self.history,
            "advice": self.generate_advice(),
        }

    def generate_advice(self):
        records = self.daily_history
        if not records:
            return []

        bullish_days = sum(
            1
            for item in records
            if item["sma5"] is not None
            and item["sma20"] is not None
            and item["sma5"] > item["sma20"]
        )
        bearish_days = sum(
            1
            for item in records
            if item["sma5"] is not None
            and item["sma20"] is not None
            and item["sma5"] < item["sma20"]
        )
        overbought_days = sum(
            1 for item in records if item["rsi"] is not None and item["rsi"] >= 70
        )
        oversold_days = sum(
            1 for item in records if item["rsi"] is not None and item["rsi"] <= 30
        )
        macd_positive_days = sum(
            1
            for item in records
            if item["macd_hist"] is not None and item["macd_hist"] > 0
        )

        total_days = len(records)
        final_pnl = records[-1]["pnl"]
        advice = []

        if bullish_days >= total_days * 0.6:
            advice.append(
                f"SMA5 高於 SMA20 的天數有 {bullish_days}/{total_days} 天，短線趨勢偏強；若要進場，較適合分批追蹤而不是一次投入。"
            )
        elif bearish_days >= total_days * 0.6:
            advice.append(
                f"SMA5 低於 SMA20 的天數有 {bearish_days}/{total_days} 天，短線趨勢偏弱；建議降低持股比例或等待趨勢轉強。"
            )
        else:
            advice.append(
                "SMA5 與 SMA20 沒有明顯單邊優勢，趨勢偏震盪；建議用較小部位操作，避免頻繁重倉。"
            )

        if overbought_days:
            advice.append(
                f"RSI 高於 70 的天數有 {overbought_days} 天，期間價格可能偏熱；這些日子較適合檢查停利或減碼策略。"
            )
        if oversold_days:
            advice.append(
                f"RSI 低於 30 的天數有 {oversold_days} 天，期間可能出現超賣；若其他指標同步轉強，可觀察反彈機會。"
            )
        if not overbought_days and not oversold_days:
            advice.append(
                "RSI 沒有進入明顯超買或超賣區間，單靠 RSI 訊號不足；建議搭配 SMA 與 MACD 判斷。"
            )

        if macd_positive_days >= total_days * 0.6:
            advice.append(
                f"MACD 柱狀體為正的天數有 {macd_positive_days}/{total_days} 天，動能多數時間偏正向。"
            )
        elif macd_positive_days <= total_days * 0.4:
            advice.append(
                f"MACD 柱狀體為正的天數只有 {macd_positive_days}/{total_days} 天，動能偏弱，進場前應等待更明確訊號。"
            )
        else:
            advice.append(
                "MACD 動能正負交錯，代表方向不穩；操作上應更重視風險控管。"
            )

        if final_pnl > 0:
            advice.append(
                f"本次模擬最終損益為 +{final_pnl:.2f}，結果為正；可回頭檢查獲利交易當天的 SMA、RSI、MACD 條件，整理成自己的進出場規則。"
            )
        elif final_pnl < 0:
            advice.append(
                f"本次模擬最終損益為 {final_pnl:.2f}，結果為負；建議檢查買入日是否出現在 SMA5 < SMA20、RSI 過熱或 MACD 偏弱時。"
            )
        else:
            advice.append(
                "本次模擬最終損益接近損益兩平；建議加入更明確的停利、停損或分批規則。"
            )

        return advice

    def get_init_state(self):
        return {
            "success": True,
            **self.base_state(),
            **self.portfolio_state(),
            **self.market_state(),
            **self.indicator_state(),
            "completed": False,
        }

    def get_next_day_state(self):
        return {
            "success": True,
            **self.market_state(),
            **self.indicator_state(),
            "price": self.price,
            "pnl": round(self.get_pnl(), 2),
            "completed": self.is_completed(),
            "report": self.final_report() if self.is_completed() else None,
        }

    def get_trade_state(self):
        return {
            "success": True,
            **self.market_state(),
            **self.indicator_state(),
            **self.portfolio_state(),
            "price": self.price,
            "completed": self.is_completed(),
            "report": self.final_report() if self.is_completed() else None,
        }

    # ---------------------------
    # 轉換給前端用
    # ---------------------------
    def history_dict(self):
        return self.history.to_dict(orient="records")
