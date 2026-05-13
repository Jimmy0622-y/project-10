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

        # 多股票資料
        self.stock_data = {}

    def fetch_stock_data(self, symbol, period="1y"):

        # 建立 csv 資料夾
        os.makedirs("csv", exist_ok=True)

        csv_path = os.path.join("csv", f"{symbol}.csv")

        # =========================
        # 本地已有 CSV
        # =========================
        if os.path.exists(csv_path):

            print(f"讀取本地資料：{csv_path}")

            df = pd.read_csv(csv_path,parse_dates=["Date"])

            df["Date"] = pd.to_datetime(df["Date"])

            self.stock_data[symbol] = df

            return df

        # =========================
        # Yahoo 下載
        # =========================
        print(f"下載 Yahoo 資料：{symbol}")

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

        # 修正二維問題
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

        # 存入字典
        self.stock_data[symbol] = df

        # 自動存 CSV
        self.save_to_csv(symbol)

        return df

    def save_to_csv(self, symbol):

        if symbol not in self.stock_data:
            return

        save_df = self.stock_data[symbol].copy()

        save_df["Date"] = save_df["Date"].dt.strftime("%Y-%m-%d")

        filename = os.path.join("csv", f"{symbol}.csv")

        save_df.to_csv(filename, index=False)

    def get_latest_indicators(self, symbol):

        if symbol not in self.stock_data:
            return None

        df = self.stock_data[symbol]

        latest = df.iloc[-1]

        return {
            "close": latest["Close"],
            "sma5": latest["SMA5"],
            "sma20": latest["SMA20"],
            "rsi": latest["RSI"],
            "macd": latest["MACD"]
        }

    def get_table_data(self, symbol):

        if symbol not in self.stock_data:
            return None

        table_df = self.stock_data[symbol].copy()

        table_df["Date"] = table_df["Date"].dt.strftime("%Y-%m-%d")

        return table_df.tail(10).to_dict(orient="records")

    def generate_candlestick_chart(self, symbol):

        if symbol not in self.stock_data:
            return None

        df = self.stock_data[symbol].copy()

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

        if symbol not in self.stock_data:
            return None

        df = self.stock_data[symbol].copy()

        df = df.tail(60)

        chart_dir = os.path.join("static", "charts")

        os.makedirs(chart_dir, exist_ok=True)

        safe_symbol = symbol.replace(".", "_")

        filename = os.path.join(
            chart_dir,
            f"{safe_symbol}_macd.png"
        )

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