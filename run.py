from flask import Flask, render_template, request
from app.models import StockAnalyzer

app = Flask(__name__)

analyzer = StockAnalyzer()


@app.route("/", methods=["GET", "POST"])
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

                # CSV
                analyzer.save_to_csv(f"{symbol}.csv")

                # 指標
                indicators = analyzer.get_latest_indicators()

                # 表格
                table_data = analyzer.get_table_data()

                # K線圖
                chart_path = analyzer.generate_candlestick_chart(symbol)

                # MACD圖
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
        message=message
    )


if __name__ == "__main__":
    app.run(debug=True)