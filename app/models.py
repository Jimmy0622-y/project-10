import pandas as pd
import yfinance as yf
import mplfinance as mpf
import os

from ta.trend import SMAIndicator
from ta.momentum import RSIIndicator


class StockAnalyzer:

    def __init__(self):
        self.data = None

    def fetch_stock_data(self, symbol, period="1y"):
        """
        抓取股票歷史資料
        """

        df = yf.download(
            symbol,
            period=period,
            auto_adjust=True,
            progress=False
        )

        if df.empty:
            return None

        df.reset_index(inplace=True)

        # 修正 MultiIndex 欄位
        df.columns = [
            col[0] if isinstance(col, tuple) else col
            for col in df.columns
        ]

        # 日期格式
        df["Date"] = pd.to_datetime(df["Date"])

        # 修正 yfinance 二維資料問題
        close_price = df["Close"].squeeze()

        # SMA5
        df["SMA5"] = SMAIndicator(
            close=close_price,
            window=5
        ).sma_indicator()

        # SMA20
        df["SMA20"] = SMAIndicator(
            close=close_price,
            window=20
        ).sma_indicator()

        # RSI
        df["RSI"] = RSIIndicator(
            close=close_price,
            window=14
        ).rsi()

        # 四捨五入
        df = df.round(2)

        self.data = df

        return df

    def save_to_csv(self, filename="stock_data.csv"):

        if self.data is not None:

            save_df = self.data.copy()

            save_df["Date"] = save_df["Date"].dt.strftime("%Y-%m-%d")

            save_df.to_csv(filename, index=False)

    def get_latest_indicators(self):

        if self.data is None:
            return None

        latest = self.data.iloc[-1]

        return {
            "close": latest["Close"],
            "sma5": latest["SMA5"],
            "sma20": latest["SMA20"],
            "rsi": latest["RSI"]
        }

    def get_table_data(self):

        if self.data is None:
            return None

        table_df = self.data.copy()

        table_df["Date"] = table_df["Date"].dt.strftime("%Y-%m-%d")

        return table_df.tail(10).to_dict(orient="records")

    def generate_candlestick_chart(self, symbol):

        if self.data is None:
            return None

        df = self.data.copy()

        # 設定索引
        df.set_index("Date", inplace=True)

        # 最近60天
        df = df.tail(60)

        # 建立資料夾
        os.makedirs("app/static/charts", exist_ok=True)

        # 修正檔名
        safe_symbol = symbol.replace(".", "_")

        filename = os.path.join("app", "static", "charts", f"{symbol}.png")

        # K線圖
        mpf.plot(
            df,
            type="candle",
            mav=(5, 20),
            volume=True,
            style="yahoo",
            title=f"{symbol} Candlestick Chart",
            figsize=(12, 8),
            savefig=filename
        )

        return f"charts/{symbol}.png"