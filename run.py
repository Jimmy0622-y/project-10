from flask import Flask, render_template, request
from app.models import StockAnalyzer

app = Flask(__name__)

analyzer = StockAnalyzer()


@app.route('/', methods=['GET', 'POST'])
def index():
    indicators = None
    table_data = None
    message = ""

    if request.method == 'POST':
        symbol = request.form['symbol']

        try:
            df = analyzer.fetch_stock_data(symbol)

            if df is not None:
                analyzer.save_to_csv(f"{symbol}.csv")

                indicators = analyzer.get_latest_indicators()

                table_data = df.tail(10).to_dict(orient='records')

                message = f"成功抓取 {symbol} 歷史資料並儲存 CSV"
            else:
                message = "查無股票資料"

        except Exception as e:
            message = f"錯誤：{str(e)}"

    return render_template(
        'index.html',
        indicators=indicators,
        table_data=table_data,
        message=message
    )


if __name__ == '__main__':
    app.run(debug=True)