import yfinance as yf
import pandas as pd
from datetime import datetime

# --- SETTINGS ---
PAIRS = ["BTC-USD", "ETH-USD", "SOL-USD"]
TIMEFRAME = "1h"

def generate_html(status_list):
    now = datetime.now().strftime("%H:%M UTC • %d %b")
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Crypto Dashboard</title>
        <meta http-equiv="refresh" content="300"> <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ background-color: #111; color: #eee; font-family: sans-serif; padding: 20px; text-align: center; }}
            .card {{ background: #222; padding: 15px; margin: 10px auto; border-radius: 10px; max-width: 400px; display: flex; justify-content: space-between; align-items: center; border: 1px solid #333; }}
            .price {{ font-size: 1.2em; color: #aaa; }}
            .long {{ color: #0f0; border: 1px solid #0f0; padding: 5px 10px; border-radius: 5px; }}
            .short {{ color: #f00; border: 1px solid #f00; padding: 5px 10px; border-radius: 5px; }}
            h1 {{ color: #888; font-size: 1.5em; }}
        </style>
    </head>
    <body>
        <h1>📊 Live Market Status</h1>
        <p style="color:#555;">Updated: {now}</p>
    """
    
    for item in status_list:
        color_class = "long" if item['trend'] == "LONG" else "short"
        html += f"""
        <div class="card">
            <div style="text-align:left;">
                <div style="font-weight:bold; font-size:1.2em;">{item['symbol']}</div>
                <div class="price">${item['price']:,.0f}</div>
            </div>
            <div class="{color_class}">
                {item['trend']}
            </div>
        </div>
        """
    
    html += "</body></html>"
    
    with open("index.html", "w") as f:
        f.write(html)

def check_market():
    status_list = []
    for symbol in PAIRS:
        try:
            df = yf.download(symbol, period="5d", interval=TIMEFRAME, progress=False)
            if df.empty: continue
            
            # Clean Data
            df = df.reset_index()
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.droplevel(1)
            df.rename(columns={'Date': 'time', 'Datetime': 'time', 'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close'}, inplace=True)

            # SuperTrend Logic
            df['tr0'] = abs(df['high'] - df['low'])
            df['tr1'] = abs(df['high'] - df['close'].shift(1))
            df['tr2'] = abs(df['low'] - df['close'].shift(1))
            df['tr'] = df[['tr0', 'tr1', 'tr2']].max(axis=1)
            df['atr'] = df['tr'].ewm(alpha=1/10, adjust=False).mean()
            
            hl2 = (df['high'] + df['low']) / 2
            df['upper'] = hl2 + (3.0 * df['atr'])
            df['lower'] = hl2 - (3.0 * df['atr'])
            
            # Simple Trend Snapshot
            price = df['close'].iloc[-1]
            ema = df['close'].ewm(span=20).mean().iloc[-1]
            trend = "LONG" if price > ema else "SHORT"
            
            status_list.append({"symbol": symbol, "price": price, "trend": trend})
        except:
            pass

    generate_html(status_list)

if __name__ == "__main__":
    check_market()
