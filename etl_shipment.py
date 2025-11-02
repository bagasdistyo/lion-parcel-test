import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# 1. Load raw data
df = pd.read_excel("shipments_raw.xlsx")

# 2. Clean & Standardize
status_mapping = {
    "in transit": "In Transit",
    "in-transit": "In Transit",
    "delivered": "Delivered",
    "pending": "Pending",
    "cancelled": "Cancelled"
}

df["status"] = df["status"].str.strip().str.lower().map(status_mapping).fillna(df["status"].str.title())

# Parse date columns
date_cols = ["booked_date", "estimated_delivery_date", "delivered_date"]
for col in date_cols:
    df[col] = pd.to_datetime(df[col], errors="coerce")

# Remove duplicates
df = df.drop_duplicates()

# === 3. Handle Missing or Invalid Data ===
print("Data quality check for delivered_date:")
print(df.groupby('status')['delivered_date'].apply(lambda x: x.isna().sum()))

# Business logic:
# - Delivered → delivered_date wajib ada. Jika tidak ada, drop.
# - Non-delivered → delivered_date boleh kosong (biarkan NaT).
missing_delivered = (df["status"] == "Delivered") & (df["delivered_date"].isna())
if missing_delivered.sum() > 0:
    print(f"Dropping {missing_delivered.sum()} delivered rows without delivered_date")
    df = df[~missing_delivered]

# === 4. Derived Columns ===

# delivery_duration_days → hanya untuk Delivered
df["delivery_duration_days"] = np.where(
    df["status"] == "Delivered",
    (df["delivered_date"] - df["booked_date"]).dt.days,
    np.nan
)

# delivery_delay_days → hanya untuk Delivered
df["delivery_delay_days"] = np.where(
    df["status"] == "Delivered",
    (df["delivered_date"] - df["estimated_delivery_date"]).dt.days,
    np.nan
)

# is_delayed flag → hanya untuk Delivered
df["is_delayed"] = np.where(
    (df["status"] == "Delivered") & (df["delivery_delay_days"] > 0),
    True,
    False
)

# === 5. Validate data (no negative durations) ===
invalid_duration = (df["status"] == "Delivered") & (df["delivery_duration_days"] < 0)

print(f"Removing {invalid_duration.sum()} invalid delivery_duration_days rows")
df = df[~invalid_duration]


# === 6. Save cleaned dataset ===
df.to_csv("shipment_transformed.csv", index=False)
print("shipment_transformed.csv created successfully.")
print(f"Final dataset shape: {df.shape}")
