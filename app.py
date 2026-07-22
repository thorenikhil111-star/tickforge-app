from flask import Flask, jsonify, send_file, request, session, redirect, url_for
import threading
import time
import random
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

USERS_DB = {"admin": "admin123", "nikhil": "trader2024"}

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
            latest_alerts = latest_alerts[:8]
            
        except Exception:
            pass
        time.sleep(3)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('username') in USERS_DB and USERS_DB[request.form.get('username')] == request.form.get('password'):
            session['logged_in'] = True
            return redirect(url_for('home'))
        return "<div style='color:red; text-align:center; padding:20px;'>Invalid Credentials! <a href='/login'>Try Again</a></div>"
            
    return '''
        <body style="background:#050505; color:white; font-family:sans-serif; display:flex; justify-content:center; align-items:center; height:100vh;">
            <div style="background:#0d1117; padding:40px; border-radius:8px; border:1px solid #1f2937; text-align:center;">
                <h2 style="color:#2f81f7;">TickForge AI</h2>
                <p style="font-size:12px; color:#6e7681; margin-bottom:20px;">Restricted Access Terminal</p>
                <form method="post">
                    <input type="text" name="username" placeholder="Username" style="width:100%; padding:10px; margin-bottom:10px; background:#161b22; border:1px solid #30363d; color:white; border-radius:4px;"><br>
                    <input type="password" name="password" placeholder="Password" style="width:100%; padding:10px; margin-bottom:20px; background:#161b22; border:1px solid #30363d; color:white; border-radius:4px;"><br>
                    <button type="submit" style="width:100%; padding:10px; background:#2ea043; color:white; border:none; border-radius:4px; font-weight:bold; cursor:pointer;">Secure Login</button>
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
    if not session.get('logged_in'):
        return jsonify({"error": "Unauthorized"}), 401
    return jsonify({"alerts": latest_alerts, "market": market_data, "indices": indices_data, "breadth": breadth_data})

if __name__ == '__main__':
    threading.Thread(target=scanner_loop, daemon=True).start()
    app.run(host='0.0.0.0', port=10000)
