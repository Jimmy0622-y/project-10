import pandas as pd
import yfinance as yf
import mplfinance as mpf
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import os

from ta.trend import SMAIndicator
from ta.momentum import RSIIndicator
from ta.trend import MACD
from app.watchlist import WATCHLIST


class StockAnalyzer:

    def __init__(self):

        # 多股票資料
        self.stock_data = {}

    def fetch_stock_data(self, symbol, period="5y"):

        # 建立 csv 資料夾
        os.makedirs("csv", exist_ok=True)

        csv_path = os.path.join("csv", f"{symbol}.csv")

        # =========================
        # 本地已有 CSV
        # =========================
        if os.path.exists(csv_path):

            print(f"讀取本地資料：{csv_path}")

            df = pd.read_csv(csv_path, parse_dates=["Date"])

            df["Date"] = pd.to_datetime(df["Date"])

            self.stock_data[symbol] = df

            return df

        # =========================
        # Yahoo 下載
        # =========================
        print(f"下載 Yahoo 資料：{symbol}")

        df = yf.download(symbol, period=period, auto_adjust=True, progress=False)

        if df.empty:
            return None

        df.reset_index(inplace=True)

        # 修正 MultiIndex
        df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]

        # 日期格式
        df["Date"] = pd.to_datetime(df["Date"])

        # 修正二維問題
        close_price = df["Close"].squeeze()

        # SMA5
        df["SMA5"] = SMAIndicator(close=close_price, window=5).sma_indicator()

        # SMA20
        df["SMA20"] = SMAIndicator(close=close_price, window=20).sma_indicator()

        # RSI
        df["RSI"] = RSIIndicator(close=close_price, window=14).rsi()

        # MACD
        macd = MACD(close=close_price)

        df["MACD"] = macd.macd()
        df["MACD_SIGNAL"] = macd.macd_signal()
        df["MACD_HIST"] = macd.macd_diff()

        # 小數點
        numeric_cols = df.select_dtypes(include=["number"]).columns

        df[numeric_cols] = df[numeric_cols].round(2)

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
            "macd": latest["MACD"],
        }

    def get_table_data(self, symbol):

        if symbol not in self.stock_data:
            return None

        table_df = self.stock_data[symbol].copy()

        table_df["Date"] = table_df["Date"].dt.strftime("%Y-%m-%d")

        return table_df.tail(10).to_dict(orient="records")

    def generate_candlestick_chart(self, df, symbol):

        # 保險：資料檢查
        if df is None or len(df) == 0:
            return None

        df = df.copy()

        # === 統一時間格式 ===
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.set_index("Date")

        # === 只取最近 60 根 ===
        df = df.tail(60)

        # === 建立資料夾 ===
        chart_dir = os.path.join("app", "static", "charts")
        os.makedirs(chart_dir, exist_ok=True)

        # === 檔名安全化 ===
        safe_symbol = (
            symbol.replace(".", "_").replace("/", "_").replace("\\", "_").strip()
        )
        filename = os.path.join(chart_dir, f"{safe_symbol}.png")

        # === 刪舊圖 ===
        if os.path.exists(filename):
            os.remove(filename)

        # === 畫圖 ===
        fig, axlist = mpf.plot(
            df,
            type="candle",
            mav=(5, 20),
            volume=True,
            style="charles",
            figsize=(12, 8),
            returnfig=True,
        )

        # === 存檔 ===
        fig.savefig(filename)
        plt.close(fig)

        # === 確認 ===
        if not os.path.exists(filename):
            print("K線圖生成失敗")
            return None

        return f"/static/charts/{safe_symbol}.png"

    def generate_macd_chart(self, df, symbol):

        if symbol not in self.stock_data:
            return None

        df = self.stock_data[symbol].copy()

        df = df.tail(60)

        chart_dir = os.path.join("app", "static", "charts")

        os.makedirs(chart_dir, exist_ok=True)

        safe_symbol = (
            symbol.replace(".", "_").replace("/", "_").replace("\\", "_").strip()
        )

        filename = os.path.join(chart_dir, f"{safe_symbol}_macd.png")

        # 刪除舊圖
        if os.path.exists(filename):
            os.remove(filename)

        fig, ax = plt.subplots(figsize=(12, 6))

        ax.plot(df["Date"], df["MACD"], label="MACD")

        ax.plot(df["Date"], df["MACD_SIGNAL"], label="Signal")

        ax.bar(df["Date"], df["MACD_HIST"])

        ax.set_title(f"{symbol} MACD")

        ax.legend()

        plt.xticks(rotation=45)

        plt.tight_layout()

        fig.savefig(filename)

        plt.close(fig)

        # 確認圖片存在
        if not os.path.exists(filename):

            print("MACD圖生成失敗")

            return None

        return f"/static/charts/{safe_symbol}_macd.png"

    def update_watchlist(self, watchlist):

        results = []

        for symbol in watchlist:

            try:

                print(f"更新：{symbol}")

                df = self.fetch_stock_data(symbol)

                self.generate_candlestick_chart(df, symbol)

                self.generate_macd_chart(df, symbol)

                results.append({"symbol": symbol, "status": "成功"})

            except Exception as e:

                results.append({"symbol": symbol, "status": f"失敗：{str(e)}"})

        return results

    def add_to_watchlist(self, symbol):

        symbol = symbol.upper().strip()

        # 避免重複
        if symbol in WATCHLIST:
            return

        WATCHLIST.append(symbol)

        # 寫回 watchlist.py
        filepath = os.path.join("app", "watchlist.py")

        with open(filepath, "w", encoding="utf-8") as f:

            f.write("WATCHLIST = [\n")

            for item in WATCHLIST:
                f.write(f'    "{item}",\n')

            f.write("]\n")

        print(f"{symbol} 已加入 WATCHLIST")
