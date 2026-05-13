import pandas as pd
import yfinance as yf
import mplfinance as mpf
import matplotlib.pyplot as plt
import os

from ta.trend import SMAIndicator
from ta.momentum import RSIIndicator
from ta.trend import MACD


class StockAnalyzer:

    def __init__(self):
        self.data = None

    def fetch_stock_data(self, symbol, period="1y"):

        df = yf.download(
            symbol,
            period=period,
            auto_adjust=True,
            progress=False
        )

        if df.empty:
            return None

        df.reset_index(inplace=True)

        # 修正 MultiIndex
        df.columns = [
            col[0] if isinstance(col, tuple) else col
            for col in df.columns
        ]

        # 日期格式
        df["Date"] = pd.to_datetime(df["Date"])

        # 修正 yfinance 二維問題
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

        # MACD
        macd = MACD(close=close_price)

        df["MACD"] = macd.macd()
        df["MACD_SIGNAL"] = macd.macd_signal()
        df["MACD_HIST"] = macd.macd_diff()

        # 小數點
        df = df.round(2)

        self.data = df

        return df

    def save_to_csv(self, symbol):

        if self.data is not None:

            # 建立 csv 資料夾
            os.makedirs("csv", exist_ok=True)

            save_df = self.data.copy()

            # 日期格式
            save_df["Date"] = save_df["Date"].dt.strftime("%Y-%m-%d")

            # 檔案路徑
            filename = os.path.join("csv", f"{symbol}.csv")

            # 儲存 CSV
            save_df.to_csv(filename, index=False)

            return filename

    def get_latest_indicators(self):

        if self.data is None:
            return None

        latest = self.data.iloc[-1]

        return {
            "close": latest["Close"],
            "sma5": latest["SMA5"],
            "sma20": latest["SMA20"],
            "rsi": latest["RSI"],
            "macd": latest["MACD"]
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

        df.set_index("Date", inplace=True)

        df = df.tail(60)

        chart_dir = os.path.join("static", "charts")

        os.makedirs(chart_dir, exist_ok=True)

        safe_symbol = symbol.replace(".", "_")

        filename = os.path.join(chart_dir, f"{safe_symbol}.png")

        mpf.plot(
            df,
            type="candle",
            mav=(5, 20),
            volume=True,
            style="charles",
            figsize=(12, 8),
            savefig=filename
        )

        return f"charts/{safe_symbol}.png"

    def generate_macd_chart(self, symbol):

        if self.data is None:
            return None

        df = self.data.copy()

        df = df.tail(60)

        safe_symbol = symbol.replace(".", "_")

        chart_dir = os.path.join("static", "charts")

        os.makedirs(chart_dir, exist_ok=True)

        filename = os.path.join(chart_dir, f"{safe_symbol}_macd.png")

        plt.figure(figsize=(12, 6))

        plt.plot(
            df["Date"],
            df["MACD"],
            label="MACD"
        )

        plt.plot(
            df["Date"],
            df["MACD_SIGNAL"],
            label="Signal"
        )

        plt.bar(
            df["Date"],
            df["MACD_HIST"]
        )

        plt.title(f"{symbol} MACD")

        plt.legend()

        plt.xticks(rotation=45)

        plt.tight_layout()

        plt.savefig(filename)

        plt.close()

        return f"charts/{safe_symbol}_macd.png"