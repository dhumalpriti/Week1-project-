"""
Logistics Data Analyst Internship - Week 1
Strategic Planning and Data Exploration

Run:
    python logistics_analysis.py

The script reads logistics_data.csv, calculates KPIs, performs simple
exploratory analysis, and creates a summary report CSV.
"""

import pandas as pd
import numpy as np
from pathlib import Path

BASE = Path(__file__).resolve().parent
DATA_FILE = BASE / "logistics_data.csv"
OUTPUT_FILE = BASE / "kpi_summary.csv"

df = pd.read_csv(DATA_FILE)

# Basic cleaning
df["Date"] = pd.to_datetime(df["Date"])
numeric_cols = ["Distance_km", "Weight_kg", "Delivery_Days", "Fuel_Litres", "Cost_INR"]
df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors="coerce")
df = df.dropna(subset=numeric_cols + ["On_Time"])

# KPI calculations
total_shipments = len(df)
on_time_rate = (df["On_Time"].eq("Yes").mean()) * 100
avg_delivery_days = df["Delivery_Days"].mean()
total_cost = df["Cost_INR"].sum()
avg_cost = df["Cost_INR"].mean()
fuel_efficiency = df["Distance_km"].sum() / df["Fuel_Litres"].sum()

# Cost per kg
df["Cost_per_kg"] = df["Cost_INR"] / df["Weight_kg"]

# Route-level analysis
route_summary = (
    df.groupby(["Origin", "Destination"])
      .agg(
          Shipments=("Shipment_ID", "count"),
          Avg_Cost_INR=("Cost_INR", "mean"),
          Avg_Delivery_Days=("Delivery_Days", "mean"),
          On_Time_Rate=("On_Time", lambda x: (x.eq("Yes").mean()) * 100),
      )
      .reset_index()
)

# Identify routes needing attention (on-time rate below 80%)
attention_routes = route_summary[route_summary["On_Time_Rate"] < 80]

kpis = pd.DataFrame({
    "KPI": [
        "Total Shipments",
        "On-Time Delivery Rate (%)",
        "Average Delivery Days",
        "Total Logistics Cost (INR)",
        "Average Shipment Cost (INR)",
        "Fleet Fuel Efficiency (km/litre)"
    ],
    "Value": [
        total_shipments,
        round(on_time_rate, 2),
        round(avg_delivery_days, 2),
        round(total_cost, 2),
        round(avg_cost, 2),
        round(fuel_efficiency, 2)
    ]
})

kpis.to_csv(OUTPUT_FILE, index=False)
route_summary.to_csv(BASE/"route_summary.csv", index=False)

print("LOGISTICS KPI SUMMARY")
print("-" * 40)
for _, row in kpis.iterrows():
    print(f"{row['KPI']}: {row['Value']}")

print("\nRoutes needing attention (on-time rate < 80%):")
if attention_routes.empty:
    print("None")
else:
    print(attention_routes.to_string(index=False))

print("\nAnalysis completed. Output files created:")
print(" - kpi_summary.csv")
print(" - route_summary.csv")
