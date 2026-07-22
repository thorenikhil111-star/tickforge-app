from flask import Flask, jsonify, send_file, request, session, redirect, url_for
from flask_cors import CORS
import threading
import time
import random
from datetime import datetime
import logging
import os

app = Flask(__name__)
app.secret_key = os.urandom(24) # Security ke liye
CORS(app)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR) 

# --- LOGIN DATABASE ---
USERS_DB = {
    "admin": "admin123",
    "nikhil": "trader2024"
}

latest_alerts = []
market_data = []
indices_data = []
breadth_data = {}

def scanner_loop():
    global latest_alerts, market_data, indices_data, breadth_data
    watchlist = ["AAPL", "TSLA", "NVDA", "AMD", "MSFT"]
    setups = ["Bounce off 9 EMA", "VWAP Pullback Entry", "Bear Flag Breakdown"]
    
    while True:
        try:
            curr_time = datetime.now().strftime('%H:%M:%S')
            
            # Dummy Market Data (Taaki API na atke)
            breadth_data = {"ndx_adv": random.randint(1400, 1800), "ndx_dec": random.randint(800, 1200), "nyse_adv": 1500, "nyse_dec": 1000}
            indices_data = [{"symbol": "SPY", "price": "520.10", "change": "0.15"}, {"symbol": "QQQ", "price": "440.00", "change": "-0.20"}]
            
            temp_market = []
            for stock in watchlist:
                temp_market.append({"symbol": stock, "price": f"{random.uniform(150, 400):.2f}", "change": f"{random.uniform(-2, 2):.2f}"})
            market_data = temp_market

            # Generate Alerts
            latest_alerts.insert(0, {
                "time": curr_time,
                "ticker": random.choice(watchlist),
                "setup": random.choice(setups),
                "direction": random.choice(["LONG", "SHORT"]),
                "entry": "$150.00", "target": "$155.00", "stop": "$148.00"
            })
            latest_alerts = latest_alerts[:5]
            
        except Exception:
            pass
        time.sleep(3)

# --- WEB ROUTES ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username in USERS_DB and USERS_DB[username] == password:
            session['logged_in'] = True
            return redirect(url_for('home'))
        else:
            return "Invalid Credentials! <a href='/login'>Try Again</a>"
            
    return '''
        <body style="background:#050505; color:white; font-family:sans-serif; display:flex; justify-content:center; align-items:center; height:100vh;">
            <div style="background:#0d1117; padding:40px; border-radius:8px; border:1px solid #1f2937; text-align:center;">
                <h2 style="color:#2f81f7;">TickForge AI</h2>
                <form method="post">
                    <input type="text" name="username" placeholder="Username" style="width:100%; padding:10px; margin-bottom:10px;"><br>
                    <input type="password" name="password" placeholder="Password" style="width:100%; padding:10px; margin-bottom:20px;"><br>
                    <button type="submit" style="width:100%; padding:10px; background:#2ea043; color:white; border:none; cursor:pointer;">Login</button>
                </form>
            </div>
        </body>
    '''

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
def home():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return send_file('index.html')

@app.route('/api/data')
def get_data():
    return jsonify({
        "alerts": latest_alerts, "market": market_data,
        "indices": indices_data, "breadth": breadth_data
    })

if __name__ == '__main__':
    threading.Thread(target=scanner_loop, daemon=True).start()
    app.run(host='0.0.0.0', port=8080)