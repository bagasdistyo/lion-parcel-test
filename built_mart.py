import pandas as pd

# Load cleaned data + customer master
df = pd.read_csv("shipment_transformed.csv")
cust = pd.read_excel("customers_raw.xlsx")

# Join
df = df.merge(cust, on="customer_id", how="left")

# Create month_year column
df["month_year"] = pd.to_datetime(df["booked_date"]).dt.to_period("M").astype(str)

# Aggregation
mart = df.groupby(["customer_id", "customer_name", "month_year"], as_index=False).agg(
    total_shipments = ("shipment_id", "count"),
    delivered_shipments = ("status", lambda x: (x=="Delivered").sum()),
    on_process_shipments = ("status", lambda x: ((x=="In Transit") | (x=="Pending")).sum()),
    cancelled_shipments = ("status", lambda x: (x=="Cancelled").sum()),
    avg_delivery_days = ("delivery_duration_days", "mean"),
    delayed_shipments = ("is_delayed", lambda x: x.sum())
)

# delayed rate
mart["delayed_rate"] = mart["delayed_shipments"] / mart["delivered_shipments"]
mart["delayed_rate"] = mart["delayed_rate"].fillna(0)

# Save file
mart.to_csv("shipment_performance.csv", index=False)

print("shipment_performance.csv created")
