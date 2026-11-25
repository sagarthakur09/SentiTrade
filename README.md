# SentiTrade

## Run
1. Install Python 3.9+
2. In this folder: `pip install flask`
3. `python app.py`
4. Open http://127.0.0.1:5000

The header shows "Backend: online" when the server is connected.
Opening index.html directly still works, using the browser-only simulation.

## Optional real data
- `pip install yfinance` -> real daily closing prices (AAPL, TSLA, TCS.NS, INFY.NS, RELIANCE.NS)
- `pip install transformers torch` -> real FinBERT scores in the headline analyzer
  (first run downloads the model, about 440 MB)

## API
- GET /api/status
- GET /api/score?text=Company posts record profit
- GET /api/stock/AAPL
