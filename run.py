from flask import Flask, render_template, request
from app.models import TradeManager
from app.utils import generate_advice

app = Flask(__name__)
manager = TradeManager()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        price = float(request.form['price'])
        manager.add_price(price)

    stats = manager.get_statistics()
    advice = generate_advice(stats)

    return render_template('index.html',
                           prices=manager.prices,
                           trades=manager.trades,
                           stats=stats,
                           advice=advice)

if __name__ == '__main__':
    app.run(debug=True)