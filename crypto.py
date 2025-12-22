import os
import time
from datetime import datetime
import requests
import pandas as pd
import matplotlib.pyplot as plt
import io
from dotenv import load_dotenv

# --- CONFIGURATION ---
# Load environment variables from .env file
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
TARGET_PRICE = 92000  # Alert triggers if Bitcoin exceeds this price

# --- FUNCTIONS ---

def send_telegram_message(message):
    """Sends a text message to the specified Telegram chat."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Error sending Telegram message: {e}")

def send_telegram_photo(message, image_path):
    """Sends a photo with a caption to the specified Telegram chat."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    try:
        with open(image_path, "rb") as img:
            files = {'photo': img}
            data = {
                "chat_id": CHAT_ID,
                "caption": message
            }
            response = requests.post(url, data=data, files=files)
            response.raise_for_status()
    except Exception as e:
        print(f"Error sending Telegram photo: {e}")

def get_prices():
    """Fetches real-time crypto prices from Coinbase API."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        # Fetching prices individually for better reliability
        btc = requests.get("https://api.coinbase.com/v2/prices/BTC-USD/spot", headers=headers).json()
        eth = requests.get("https://api.coinbase.com/v2/prices/ETH-USD/spot", headers=headers).json()
        sol = requests.get("https://api.coinbase.com/v2/prices/SOL-USD/spot", headers=headers).json()
        
        return {
            'bitcoin': {'usd': float(btc['data']['amount'])},
            'ethereum': {'usd': float(eth['data']['amount'])},
            'solana': {'usd': float(sol['data']['amount'])}
        }
    except Exception as e:
        print(f"Data fetch error: {e}")
        return None

def create_chart(prices_list):
    """Generates a price trend chart and saves it locally."""
    try:
        df = pd.DataFrame(prices_list)
        df['time'] = pd.to_datetime(df['time'])
        
        plt.figure(figsize=(10, 6))
        plt.plot(df['time'], df['bitcoin'], label='Bitcoin (USD)', color='orange', linewidth=2)
        
        plt.title('Bitcoin Price Trend (Last 24h)')
        plt.xlabel('Time')
        plt.ylabel('Price ($)')
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.legend()
        
        filename = "crypto_chart.png"
        plt.savefig(filename)
        plt.close()
        return filename
    except Exception as e:
        print(f"Chart creation error: {e}")
        return None

# --- MAIN LOOP ---

print("🚀 Crypto Alert Bot Started...")
print(f"Target Price: ${TARGET_PRICE} (Alerts will trigger above this)")
print("-" * 50)

price_history = []

while True:
    try:
        prices = get_prices()
        
        if prices:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            btc_price = prices['bitcoin']['usd']
            
            # Add to history for charting
            price_history.append({'time': current_time, 'bitcoin': btc_price})
            
            # Keep only the last 24 hours of data (assuming 1 check per minute = 1440 checks)
            if len(price_history) > 1440:
                price_history.pop(0)
            
            # Log to console
            print(f"💤 {current_time} -> Price ${btc_price:.2f}. Target (${TARGET_PRICE}) not reached yet. Waiting...")
            
            # CHECK TARGET
            if btc_price > TARGET_PRICE:
                print("🚨 TARGET REACHED! Sending alert...")
                
                # Generate chart
                chart_file = create_chart(price_history)
                
                # Create message
                msg = (f"🚀 ALERT: Bitcoin passed the target!\n\n"
                       f"💰 Current Price: ${btc_price:.2f}\n"
                       f"🎯 Target: ${TARGET_PRICE}\n"
                       f"⏳ Time: {current_time}")
                
                # Send to Telegram
                if chart_file:
                    send_telegram_photo(msg, chart_file)
                else:
                    send_telegram_message(msg)
                
                # Wait longer after an alert to avoid spamming (e.g., 1 hour)
                time.sleep(3600) 
            
        # Wait 1 minute before next check
        time.sleep(60)

    except Exception as e:
        print(f"Unexpected error: {e}")
        time.sleep(60)