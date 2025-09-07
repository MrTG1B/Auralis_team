import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# -------------------------------
# Step 1: Load Traffic CSV
# -------------------------------
traffic_df = pd.read_csv("traffic_count.csv")  # Replace with your CSV file name

# Create proper timestamp
traffic_df["timestamp"] = pd.to_datetime(
    traffic_df["Dates"].astype(str) + " " + traffic_df["Start"].astype(str).str.split().str[1],
    dayfirst=True,
    format="%d/%m/%Y %H.%M"
)

traffic_df.set_index("timestamp", inplace=True)

# Use the 'Count' column as vehicle counts
traffic_series = traffic_df["Count"].astype(float).resample("h").sum()

# -------------------------------
# Step 2: Load Energy Mapping XLSX
# -------------------------------
energy_cols = [
    "Sl.No", "Time", "No of Vehicle", "No of Vehicle (in front of lp)", "Average speed",
    "Energy Consumption of Tradional Light", "Energy Consumption of Smart Light",
    "Total Energy Consumption of Tradional Lights", "Total Energy Consumption of Smart Lights",
    "Energy Savings", "distance between 2lp", "time for 100%", "watt", "20%", "time for 20%"
]

energy_df = pd.read_excel("Smart_Street_Light_Energy.xlsx", header=1, names=energy_cols)
energy_df.columns = energy_df.columns.str.strip()

# Filter rows with valid 'Time' format
energy_df = energy_df[energy_df["Time"].str.contains(r"^\d{2}:\d{2}-\d{2}:\d{2}$")].copy()

# -------------------------------
# Step 3: Compute Hourly Traffic Pattern
# -------------------------------
# Average traffic by hour of day
hourly_pattern = traffic_series.groupby(traffic_series.index.hour).mean()

# Function to forecast 24h traffic for any date
def forecast_traffic(date_str):
    start_date = pd.to_datetime(date_str)
    forecast_index = pd.date_range(start=start_date, periods=24, freq='h')
    forecast_values = [hourly_pattern.get(h.hour, 0) for h in forecast_index]
    return pd.Series(forecast_values, index=forecast_index)

# Example: forecast for a given date
forecast_date = "2022-01-08"
forecast_traffic_24h = forecast_traffic(forecast_date)

# -------------------------------
# Step 4: Map Forecasted Traffic to Energy
# -------------------------------
max_traffic = energy_df["No of Vehicle"].max()
max_trad_energy = energy_df["Total Energy Consumption of Tradional Lights"].max()
max_smart_energy = energy_df["Total Energy Consumption of Smart Lights"].max()

trad_list, smart_list = [], []

for h, v in zip(forecast_traffic_24h.index, forecast_traffic_24h.values):
    trad = max_trad_energy * v / max_traffic
    smart = max_smart_energy * v / max_traffic
    
    # Night adjustment: 0–6 AM lights may be off
    if h.hour < 6:
        smart = 0
    
    trad_list.append(trad)
    smart_list.append(smart)

savings_pct = [(1 - s/t)*100 if t>0 else 0 for t,s in zip(trad_list, smart_list)]

forecast_df = pd.DataFrame({
    "Hour": forecast_traffic_24h.index,
    "Vehicles": forecast_traffic_24h.values,
    "Traditional (kWh)": trad_list,
    "Smart (kWh)": smart_list,
    "Savings (%)": savings_pct
})

print("\nForecasted Traffic & Energy for Next 24 Hours:")
print(forecast_df)

# -------------------------------
# Step 5: Plot
# -------------------------------
plt.figure(figsize=(12,5))
plt.plot(forecast_df["Hour"], forecast_df["Vehicles"], 'o-', label="Forecast Traffic")
plt.title("Traffic Forecast for Next 24 Hours")
plt.xlabel("Hour")
plt.ylabel("Vehicles")
plt.legend()
plt.show()

plt.figure(figsize=(12,5))
plt.plot(forecast_df["Hour"], forecast_df["Traditional (kWh)"], 'o-', label="Traditional Lights")
plt.plot(forecast_df["Hour"], forecast_df["Smart (kWh)"], 'o-', label="Smart Lights")
plt.title("Predicted Energy Consumption for Next 24 Hours")
plt.xlabel("Hour")
plt.ylabel("Energy (kWh)")
plt.legend()
plt.show()
