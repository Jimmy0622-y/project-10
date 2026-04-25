class TradeManager:
    def __init__(self):
        self.prices = []
        self.trades = []
        self.position = None

    def add_price(self, price):
        self.prices.append(price)

        if len(self.prices) < 20:
            return

        ma5 = sum(self.prices[-5:]) / 5
        ma10 = sum(self.prices[-10:]) / 10
        ma20 = sum(self.prices[-20:]) / 20

        # 買進訊號（多頭排列）
        if self.position is None and ma5 > ma10 > ma20:
            self.position = price
            self.trades.append(("BUY", price))

        # 賣出訊號（空頭排列）
        elif self.position is not None and ma5 < ma10 < ma20:
            profit = round(price - self.position, 2)
            self.trades.append(("SELL", price, profit))
            self.position = None

    def get_statistics(self):
        profits = [t[2] for t in self.trades if t[0] == "SELL"]

        total = len(profits)
        wins = sum(1 for p in profits if p > 0)

        win_rate = round((wins / total) * 100, 2) if total else 0

        total_profit = sum(p for p in profits if p > 0)
        total_loss = abs(sum(p for p in profits if p < 0))

        profit_ratio = round(total_profit / total_loss, 2) if total_loss > 0 else float('inf')

        return {
            "total": total,
            "win_rate": win_rate,
            "profit_ratio": profit_ratio
        }