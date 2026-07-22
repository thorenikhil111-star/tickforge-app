from flask import Flask, jsonify, send_file
from flask_cors import CORS
import threading
import time
import random
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

latest_alerts = []
market_data = []
indices_data = []
breadth_data = {}

setups_list = [
    {"name": "Bounce off 9 EMA", "dir": "LONG"},
    {"name": "Rejection at 200 SMA", "dir": "SHORT"},
    {"name": "VWAP Pullback Entry", "dir": "LONG"},
    {"name": "Loss of 21 EMA Support", "dir": "SHORT"},
    {"name": "ORB Breakout", "dir": "LONG"},
    {"name": "Bear Flag Breakdown", "dir": "SHORT"}
]

def scanner_loop():
    global latest_alerts, market_data, indices_data, breadth_data
    watchlist = ["AAPL", "TSLA", "NVDA", "AMD", "MSFT", "META", "AMZN"]
    
    while True:
        try:
            curr_time = datetime.now().strftime('%H:%M:%S')
            
            breadth_data = {
                "ndx_adv": random.randint(1400, 1800), "ndx_dec": random.randint(800, 1200),
                "nyse_adv": random.randint(1500, 2000), "nyse_dec": random.randint(1000, 1500),
                "etf_adv": random.randint(50, 80), "etf_dec": random.randint(20, 50)
            }
            
            indices_data = [
                {"symbol": "SPY", "price": f"{random.uniform(520, 530):.2f}", "change": f"{random.uniform(-1, 1):.2f}"},
                {"symbol": "QQQ", "price": f"{random.uniform(440, 450):.2f}", "change": f"{random.uniform(-1, 1):.2f}"}
            ]
            
            temp_market = []
            for stock in watchlist:
                temp_market.append({"symbol": stock, "price": f"{random.uniform(100, 400):.2f}", "change": f"{random.uniform(-2, 2):.2f}"})
            market_data = temp_market

            setup = random.choice(setups_list)
            base_price = random.uniform(100, 300)
            tgt = base_price + 3 if setup['dir'] == "LONG" else base_price - 3
            stop = base_price - 1 if setup['dir'] == "LONG" else base_price + 1

            latest_alerts.insert(0, {
                "time": curr_time,
                "ticker": random.choice(watchlist),
                "setup": setup['name'],
                "direction": setup['dir'],
                "entry": f"${base_price:.2f}", 
                "target": f"${tgt:.2f}", 
                "stop": f"${stop:.2f}"
            })
            latest_alerts = latest_alerts[:6]
            
        except Exception:
            pass
        time.sleep(3)

@app.route('/')
def home():
    return send_file('index.html')

@app.route('/api/data')
def get_data():
    # Bina kisi password ke data de dega
    return jsonify({
        "alerts": latest_alerts, 
        "market": market_data, 
        "indices": indices_data, 
        "breadth": breadth_data
    })

if __name__ == '__main__':
    threading.Thread(target=scanner_loop, daemon=True).start()
    app.run(host='0.0.0.0', port=10000)
