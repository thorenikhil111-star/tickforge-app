from flask import Flask, jsonify, send_file
import threading
import time
import random
from datetime import datetime
import os

app = Flask(__name__)

# --- STATE VARIABLES ---
watchlist = ["AAPL", "TSLA", "NVDA", "AMD", "MSFT", "META", "AMZN"]
live_market_data = []
active_trades = []
trade_stats = {"wins": 0, "losses": 0, "total": 0, "win_rate": 0.0}
gainers_data = []
latest_news = []
indices_data = []

setups = [{"name": "9 EMA Bounce", "dir": "LONG"}, {"name": "VWAP Reject", "dir": "SHORT"}, {"name": "Breakout", "dir": "LONG"}]

def generate_rock_solid_market():
    global live_market_data, active_trades, trade_stats, gainers_data, latest_news, indices_data
    
    while True:
        try:
            # 1. Reliable Data Generation (Bypasses Yahoo Blocks)
            current_prices = {}
            temp_market = []
            for sym in watchlist:
                price = random.uniform(100, 400)
                change = random.uniform(-2, 2)
                current_prices[sym] = price
                temp_market.append({"symbol": sym, "price": f"{price:.2f}", "change": f"{change:.2f}"})
            
            live_market_data = temp_market

            indices_data = [
                {"symbol": "SPY", "price": f"{random.uniform(520, 530):.2f}", "change": f"{random.uniform(-1, 1):.2f}"},
                {"symbol": "QQQ", "price": f"{random.uniform(440, 450):.2f}", "change": f"{random.uniform(-1, 1):.2f}"}
            ]

            # 2. Track Existing Trades
            still_active = []
            for trade in active_trades:
                sym = trade['ticker']
                if sym in current_prices:
                    curr_p = current_prices[sym]
                    
                    hit_tgt = (trade['dir'] == "LONG" and curr_p >= trade['tgt_val']) or (trade['dir'] == "SHORT" and curr_p <= trade['tgt_val'])
                    hit_sl = (trade['dir'] == "LONG" and curr_p <= trade['stop_val']) or (trade['dir'] == "SHORT" and curr_p >= trade['stop_val'])
                    
                    if hit_tgt:
                        trade_stats["wins"] += 1
                        trade_stats["total"] += 1
                    elif hit_sl:
                        trade_stats["losses"] += 1
                        trade_stats["total"] += 1
                    else:
                        still_active.append(trade)
            
            active_trades = still_active
            if trade_stats["total"] > 0:
                trade_stats["win_rate"] = round((trade_stats["wins"] / trade_stats["total"]) * 100, 1)

            # 3. Generate New Alerts
            if len(active_trades) < 5 and current_prices:
                sym = random.choice(watchlist)
                base_p = current_prices[sym]
                setup = random.choice(setups)
                
                tgt_val = base_p + (base_p * 0.01) if setup['dir'] == "LONG" else base_p - (base_p * 0.01)
                stop_val = base_p - (base_p * 0.005) if setup['dir'] == "LONG" else base_p + (base_p * 0.005)
                
                active_trades.insert(0, {
                    "time": datetime.now().strftime('%H:%M:%S'),
                    "ticker": sym, "setup": setup['name'], "dir": setup['dir'],
                    "entry_val": base_p, "tgt_val": tgt_val, "stop_val": stop_val
                })

            # 4. Fill in Gainers & News
            gainers_data = [
                {"sym": "SMCI", "change": "+14.2%", "catalyst": "Earnings Beat & AI Server Demand"},
                {"sym": "ARM", "change": "+9.1%", "catalyst": "New Institutional Upgrade (Buy)"}
            ]
            latest_news = [
                {"time": datetime.now().strftime('%H:%M'), "text": "NASDAQ hits new intraday levels as tech rallies.", "sentiment": "BULLISH"},
                {"time": "09:30 AM", "text": "VIX spikes 4% as geopolitical tensions rise.", "sentiment": "BEARISH"}
            ]

        except Exception as e:
            print("Scanner Error:", e)
        
        time.sleep(3) 

@app.route('/')
def home():
    return send_file('index.html')

@app.route('/api/data')
def get_data():
    ui_alerts = []
    for t in active_trades:
        ui_alerts.append({
            "time": t['time'], "ticker": t['ticker'], "setup": t['setup'], "direction": t['dir'],
            "entry": f"${t['entry_val']:.2f}", "target": f"${t['tgt_val']:.2f}", "stop": f"${t['stop_val']:.2f}"
        })
        
    return jsonify({
        "alerts": ui_alerts, 
        "market": live_market_data, 
        "indices": indices_data,
        "gainers": gainers_data,
        "news": latest_news,
        "stats": trade_stats
    })

if __name__ == '__main__':
    threading.Thread(target=generate_rock_solid_market, daemon=True).start()
    app.run(host='0.0.0.0', port=10000)
