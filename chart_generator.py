import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Verileri tutmak için boş listeler
tarihler = []
bitcoin_fiyatlari = []

with open("fiyat_log.txt", "r", encoding="utf-8") as file:
    for line in file:
        try:
            parts = line.strip().split(" | ")
            if len(parts) < 2:
                continue
            # Tarih
            tarih_str = parts[0]
            # Bitcoin fiyatı
            btc_part = None
            for p in parts:
                if p.startswith("BTC: $") or p.startswith("Bitcoin: $"):
                    btc_part = p
                    break
            if not btc_part:
                continue
            fiyat_str = btc_part.split("$")[1]
            fiyat = float(fiyat_str.replace(",", ""))

            # Tarihi datetime'a çevir
            tarih = datetime.strptime(tarih_str, "%Y-%m-%d %H:%M:%S")
            tarihler.append(tarih)
            bitcoin_fiyatlari.append(fiyat)
        except Exception:
            continue  # Satırda sorun olursa atla

# DataFrame oluştur
df = pd.DataFrame({
    "Tarih": tarihler,
    "Bitcoin": bitcoin_fiyatlari
})

# Tarihi indeks olarak ayarla
df.set_index("Tarih", inplace=True)

# Grafik oluştur
plt.figure(figsize=(12, 6))
plt.plot(df.index, df["Bitcoin"], color="orange", linewidth=2)
plt.title("Bitcoin Fiyat Analizi", fontsize=16)
plt.xlabel("Tarih", fontsize=13)
plt.ylabel("Fiyat (USD)", fontsize=13)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("bitcoin_grafik.png")
