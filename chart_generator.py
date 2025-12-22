import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os

LOG_FILE = "price_log.txt"

def create_chart(target_symbol):
    """
    Reads the log file, filters for the specific coin (BTC, ETH, or SOL),
    and generates a trend chart.
    """
    if not os.path.exists(LOG_FILE):
        return None

    dates = []
    prices = []

    try:
        with open(LOG_FILE, "r", encoding="utf-8") as file:
            for line in file:
                # Format: "2025-12-23 02:45:00 | BTC | $98000.50"
                try:
                    parts = line.strip().split(" | ")
                    if len(parts) < 3:
                        continue
                    
                    time_str = parts[0]
                    symbol = parts[1]
                    price_str = parts[2].replace("$", "")

                    # Only take data for the requested coin (e.g., only ETH)
                    if symbol == target_symbol:
                        dates.append(datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S"))
                        prices.append(float(price_str))

                except Exception:
                    continue
        
        if not dates:
            print(f"⚠️ No data found for {target_symbol}")
            return None

        # Create DataFrame
        df = pd.DataFrame({"Date": dates, "Price": prices})
        
        # Plot
        plt.figure(figsize=(10, 6))
        
        # Color logic based on coin
        color_map = {"BTC": "#F7931A", "ETH": "#627EEA", "SOL": "#14F195"}
        chart_color = color_map.get(target_symbol, "blue")

        plt.plot(df["Date"], df["Price"], color=chart_color, linewidth=2, label=target_symbol)
        
        plt.title(f'{target_symbol} Price Trend - Arkhe Labs', fontsize=14, fontweight='bold')
        plt.xlabel('Time', fontsize=10)
        plt.ylabel('Price (USD)', fontsize=10)
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.legend()
        plt.tight_layout()

        filename = f"{target_symbol}_alert_chart.png"
        plt.savefig(filename)
        plt.close()
        
        return filename

    except Exception as e:
        print(f"❌ Chart Error: {e}")
        return None