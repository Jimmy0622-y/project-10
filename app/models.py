import pandas as pd
import yfinance as yf
from ta.trend import SMAIndicator
from ta.momentum import RSIIndicator


class StockAnalyzer:
    def __init__(self):
        self.data = None

    def fetch_stock_data(self, symbol, period="1y"):
        """
        抓取股票歷史資料
        """

        # 使用 download 比較穩定
        df = yf.download(
            symbol,
            period=period,
            auto_adjust=True,
            progress=False
        )

        if df.empty:
            return None

        df.reset_index(inplace=True)

        df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]

        df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")

        close_price = df["Close"].squeeze()

        # 技術指標
        df["SMA5"] = SMAIndicator(
        close=close_price,
        window=5
        ).sma_indicator()

        df["SMA20"] = SMAIndicator(
        close=close_price,
        window=20
        ).sma_indicator()

        rsi = RSIIndicator(
        close=close_price,
        window=14
        )
        df["RSI"] = rsi.rsi()

        self.data = df

        return df

    def save_to_csv(self, filename="stock_data.csv"):
        if self.data is not None:
            self.data.to_csv(filename, index=False)

    def get_latest_indicators(self):
        if self.data is None:
            return None

        latest = self.data.iloc[-1]

        return {
            "close": round(latest["Close"], 2),
            "sma5": round(latest["SMA5"], 2),
            "sma20": round(latest["SMA20"], 2),
            "rsi": round(latest["RSI"], 2)
        }