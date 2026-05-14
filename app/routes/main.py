from flask import Blueprint, render_template, request

from app.services.models import StockAnalyzer
from app.watchlist import WATCHLIST

main = Blueprint("main", __name__)

analyzer = StockAnalyzer()


# =========================
# 一鍵更新股票清單
# =========================
@main.route("/update_all")
def update_all():

    results = analyzer.update_watchlist(WATCHLIST)

    return render_template(
        "update.html",
        results=results
    )


# =========================
# 首頁
# =========================
@main.route("/", methods=["GET", "POST"])
def index():

    indicators = None
    table_data = None
    chart_path = None
    macd_chart = None
    message = ""

    if request.method == "POST":

        symbol = request.form["symbol"]

        try:

            df = analyzer.fetch_stock_data(symbol)

            if df is None:

                message = "抓不到股票資料"

            else:

                # 技術指標
                indicators = analyzer.get_latest_indicators(symbol)

                # 表格
                table_data = analyzer.get_table_data(symbol)

                # K 線圖
                chart_path = analyzer.generate_candlestick_chart(symbol)

                # MACD 圖
                macd_chart = analyzer.generate_macd_chart(symbol)

                message = f"{symbol} 分析完成"

        except Exception as e:

            message = f"錯誤：{str(e)}"

    return render_template(
        "index.html",
        indicators=indicators,
        table_data=table_data,
        chart_path=chart_path,
        macd_chart=macd_chart,
        message=message,
    )