import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os

# Define file paths
LOG_FILE = "price_log.txt"
CHART_FILE = "bitcoin_chart_example.png"

def generate_chart():
    # Check if log file exists
    if not os.path.exists(LOG_FILE):
        print(f"⚠️ Warning: {LOG_FILE} not found. Skipping chart generation.")
        return

    dates = []
    prices = []

    try:
        with open(LOG_FILE, "r", encoding="utf-8") as file:
            for line in file:
                try:
                    # Parse log format: "2025-12-22 15:30 -> Price $90000..."
                    parts = line.strip().split(" -> ")
                    if len(parts) < 2:
                        continue
                    
                    date_part = parts[0]
                    # Extract price safely
                    if "Price $" in parts[1]:
                        price_part = parts[1].split("Price $")[1].split(".")[0]
                        
                        dates.append(datetime.strptime(date_part, "%Y-%m-%d %H:%M:%S"))
                        prices.append(float(price_part))
                except Exception:
                    continue

        if dates:
            # Create DataFrame
            df = pd.DataFrame({"Date": dates, "Price": prices})
            df.set_index("Date", inplace=True)
            
            # Plotting
            plt.figure(figsize=(10, 6))
            plt.plot(df.index, df["Price"], label='Bitcoin (USD)', color='#F7931A', linewidth=2)
            
            plt.title('Bitcoin Price Analysis (Real-Time)', fontsize=14)
            plt.xlabel('Date & Time', fontsize=12)
            plt.ylabel('Price (USD)', fontsize=12)
            plt.grid(True, linestyle='--', alpha=0.5)
            plt.legend()
            plt.tight_layout()
            
            plt.savefig(CHART_FILE)
            print(f"✅ Chart saved to {CHART_FILE}")
        else:
            print("⚠️ No valid data found in logs.")

    except Exception as e:
        print(f"❌ Error creating chart: {e}")

if __name__ == "__main__":
    generate_chart()