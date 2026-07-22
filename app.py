from flask import Flask, jsonify, send_file
import random
from datetime import datetime

app = Flask(__name__)

setups_list = [
    {"name": "Bounce off 9 EMA", "dir": "LONG"},
    {"name": "Rejection at 200 SMA", "dir": "SHORT"},
    {"name": "VWAP Pullback Entry", "dir": "LONG"},
    {"name": "Loss of 21 EMA Support", "dir": "SHORT"},
    {"name": "ORB Breakout", "dir": "LONG"}
]
watchlist = ["AAPL", "TSLA", "NVDA", "AMD", "MSFT", "META", "AMZN"]

@app.route('/')
def home():
    return send_file('index.html')

@app.route('/api/data')
def get_data():
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
    
    temp_market = [{"symbol": s, "price": f"{random.uniform(100, 400):.2f}", "change": f"{random.uniform(-2, 2):.2f}"} for s in watchlist]
        
    temp_alerts = []
    for _ in range(5):
        setup = random.choice(setups_list)
        base = random.uniform(100, 300)
        tgt = base + 3 if setup['dir'] == "LONG" else base - 3
        stop = base - 1 if setup['dir'] == "LONG" else base + 1
        temp_alerts.append({
            "time": curr_time, "ticker": random.choice(watchlist),
            "setup": setup['name'], "direction": setup['dir'],
            "entry": f"${base:.2f}", "target": f"${tgt:.2f}", "stop": f"${stop:.2f}"
        })

    return jsonify({
        "alerts": temp_alerts, 
        "market": temp_market, 
        "indices": indices_data, 
        "breadth": breadth_data
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
