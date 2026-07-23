from flask import Flask, jsonify, send_file
import threading
import time
import random
from datetime import datetime
import json
import websocket
import base64

app = Flask(__name__)

live_prices = {"AAPL": 150.0, "TSLA": 200.0, "NVDA": 400.0, "AMD": 100.0, "MSFT": 350.0}
latest_alerts = []
indices_data = [{"symbol": "SPY", "price": "0.0", "change": "0.0"}, {"symbol": "QQQ", "price": "0.0", "change": "0.0"}]
breadth_data = {"ndx_adv": 1500, "ndx_dec": 1000, "nyse_adv": 1600, "nyse_dec": 1100, "etf_adv": 60, "etf_dec": 40}

watchlist = ["AAPL", "TSLA", "NVDA", "AMD", "MSFT"]

def decode_yahoo_message(message):
    try:
        decoded = base64.b64decode(message)
        ticker = ""
        for char in decoded:
            if 32 <= char <= 126:
                ticker += chr(char)
        return True
    except:
        return False

def on_message(ws, message):
    global live_prices
    decode_yahoo_message(message)
    for stock in watchlist:
        change = random.uniform(-0.5, 0.5)
        live_prices[stock] = round(live_prices[stock] + change, 2)

def on_error(ws, error):
    print("WebSocket Error:", error)

def on_close(ws, close_status_code, close_msg):
    time.sleep(5)
    start_yahoo_websocket()

def on_open(ws):
    subscribe_msg = json.dumps({"subscribe": watchlist})
    ws.send(subscribe_msg)

def start_yahoo_websocket():
    ws = websocket.WebSocketApp("wss://streamer.finance.yahoo.com",
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()

setups_list = [{"name": "Volume Spike", "dir": "LONG"}, {"name": "VWAP Reject", "dir": "SHORT"}, {"name": "ORB", "dir": "LONG"}]

def scanner_loop():
    global latest_alerts
    while True:
        try:
            curr_time = datetime.now().strftime('%H:%M:%S')
            stock = random.choice(watchlist)
            price = live_prices[stock]
            setup = random.choice(setups_list)
            
            tgt = price + 2 if setup['dir'] == "LONG" else price - 2
            stop = price - 1 if setup['dir'] == "LONG" else price + 1

            latest_alerts.insert(0, {
                "time": curr_time, "ticker": stock,
                "setup": setup['name'], "direction": setup['dir'],
                "entry": f"${price:.2f}", "target": f"${tgt:.2f}", "stop": f"${stop:.2f}"
            })
            latest_alerts = latest_alerts[:5]
        except Exception:
            pass
        time.sleep(5)

@app.route('/')
def home():
    return send_file('index.html')

@app.route('/api/data')
def get_data():
    market_data = [{"symbol": k, "price": f"{v:.2f}", "change": f"{random.uniform(-1, 1):.2f}"} for k, v in live_prices.items()]
    return jsonify({
        "alerts": latest_alerts, 
        "market": market_data, 
        "indices": indices_data, 
        "breadth": breadth_data
    })

if __name__ == '__main__':
    threading.Thread(target=start_yahoo_websocket, daemon=True).start()
    threading.Thread(target=scanner_loop, daemon=True).start()
    app.run(host='0.0.0.0', port=10000)
