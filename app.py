"""SentiTrade backend: serves the page and a small JSON API.
Works with only Flask installed. Optional extras are used automatically if present:
  yfinance      -> real daily closing prices
  transformers  -> real FinBERT sentiment (downloads the model on first run)
"""
import os, re, time
from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__)
HERE = os.path.dirname(os.path.abspath(__file__))
TICKER = {"AAPL": "AAPL", "TSLA": "TSLA", "TCS": "TCS.NS", "INFY": "INFY.NS", "RELIANCE": "RELIANCE.NS"}
POS = "beat surge record growth profit upgrade strong gain rally bullish wins expands soar boost rise".split()
NEG = "miss fall drop lawsuit downgrade weak loss recall bearish cuts decline probe fraud slump plunge".split()

try:
    import yfinance as yf
except ImportError:
    yf = None
try:
    from transformers import pipeline
    finbert = pipeline("text-classification", model="ProsusAI/finbert")
except Exception:
    finbert = None

def word_score(text):
    words = re.findall(r"[a-z]+", text.lower())
    p = sum(w in POS for w in words)
    n = sum(w in NEG for w in words)
    return (p - n) / (p + n) * min(1, 0.45 + 0.2 * (p + n)) if p + n else 0.0

def score(text):
    if finbert:
        r = finbert(text[:512])[0]
        sign = {"positive": 1, "negative": -1}.get(r["label"].lower(), 0)
        return sign * r["score"], "FinBERT"
    return word_score(text), "word-list scorer"

_cache = {}
def closes(sym):
    hit = _cache.get(sym)
    if hit and time.time() - hit[0] < 600:
        return hit[1]
    data = []
    if yf and sym in TICKER:
        try:
            h = yf.Ticker(TICKER[sym]).history(period="3mo")["Close"].dropna().tail(30)
            data = [round(float(x), 2) for x in h]
        except Exception:
            data = []
    _cache[sym] = (time.time(), data)
    return data

@app.route("/")
def index():
    return send_from_directory(HERE, "index.html")

@app.route("/api/status")
def status():
    return jsonify(prices="live prices" if yf else "simulated prices",
                   sentiment="FinBERT" if finbert else "word-list scorer")

@app.route("/api/score")
def api_score():
    s, model = score(request.args.get("text", ""))
    return jsonify(score=round(s, 3), model=model)

@app.route("/api/stock/<sym>")
def api_stock(sym):
    c = closes(sym.upper())
    return jsonify(source="yfinance" if len(c) >= 30 else "simulated", close=c)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
