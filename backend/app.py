from flask import Flask, jsonify, request
import yfinance as yf

app = Flask(__name__)

@app.route("/")
def home():
    return "Stock API running"

if __name__ == "__main__":
    app.run(debug=True)