import os
import time
import requests
from datetime import datetime
from dotenv import load_dotenv
import chart_generator  # We will update this next

# --- v2.0 CONFIGURATION (The Trinity) ---
# Define your target prices here
TRACKING_LIST = {
    "BTC": {"api_id": "BTC-USD", "name": "Bitcoin", "target": 98000},  # Alert if > $98k
    "ETH": {"api_id": "ETH-USD", "name": "Ethereum", "target": 3500},  # Alert if > $3.5k
    "SOL": {"api_id": "SOL-USD", "name": "Solana",   "target": 210},   # Alert if > $210
}

# Load secrets
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
LOG_FILE = "price_log.txt"

# --- FUNCTIONS ---

def send_telegram_alert(coin_name, price, chart_path):
    """Sends a photo alert with caption to Telegram."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    caption = f"🚨 **ARKHE LABS ALERT** 🚨\n\n📈 **{coin_name}** just surged!\n💰 Current Price: ${price:,.2f}\n⚠️ Target Exceeded!"
    
    try:
        with open(chart_path, "rb") as image_file:
            payload = {"chat_id": CHAT_ID, "caption": caption, "parse_mode": "Markdown"}
            files = {"photo": image_file}
            requests.post(url, data=payload, files=files)
        print(f"✅ Alert sent for {coin_name}!")
    except Exception as e:
        print(f"❌ Failed to send Telegram alert: {e}")

def get_price(currency_pair):
    """Fetches price from Coinbase API (e.g., BTC-USD)."""
    url = f"https://api.coinbase.com/v2/prices/{currency_pair}/spot"
    try:
        response = requests.get(url)
        data = response.json()
        return float(data['data']['amount'])
    except Exception as e:
        print(f"❌ API Error ({currency_pair}): {e}")
        return None

def log_price(coin_symbol, price):
    """Saves price to a text file with timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"{timestamp} | {coin_symbol} | ${price:.2f}\n"
    
    with open(LOG_FILE, "a", encoding="utf-8") as file:
        file.write(log_entry)
    
    print(f"📝 {coin_symbol}: ${price:,.2f} logged.")

# --- MAIN LOOP ---

def start_sentinel():
    print("-" * 40)
    print("🛡️  ARKHE LABS SENTINEL v2.0 (Trinity) STARTED")
    print(f"🔭 Tracking: {', '.join(TRACKING_LIST.keys())}")
    print("-" * 40)

    while True:
        try:
            for symbol, data in TRACKING_LIST.items():
                # 1. Get Price
                current_price = get_price(data["api_id"])
                
                if current_price:
                    # 2. Log Data
                    log_price(symbol, current_price)

                    # 3. Check Target
                    if current_price > data["target"]:
                        print(f"🔥 {symbol} TARGET HIT! Generarting Chart...")
                        
                        # Generate specific chart for this coin
                        chart_path = chart_generator.create_chart(symbol)
                        
                        if chart_path:
                            send_telegram_alert(data["name"], current_price, chart_path)
                            
                            # Update target to avoid spamming (add 5% to new target)
                            new_target = current_price * 1.05
                            TRACKING_LIST[symbol]["target"] = new_target
                            print(f"🔄 New target for {symbol} set to ${new_target:,.2f}")

            print("💤 Waiting 60 seconds...")
            time.sleep(60)

        except KeyboardInterrupt:
            print("\n🛑 Sentinel Stopped.")
            break
        except Exception as e:
            print(f"❌ Unexpected Error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    start_sentinel()