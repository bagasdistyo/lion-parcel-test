# 📦 Lion Parcel Data Analytics — ETL & Data Mart Project

## 🎯 Objective
Project ini bertujuan untuk melakukan proses data preparation dan membangun data mart shipment performance. Proses ini meniru pipeline modern data warehouse:

- **Bronze Layer:** raw file input
- **Silver Layer:** clean & standardized shipment data
- **Gold Layer:** customer shipment performance mart (monthly)

---

## 🧠 Approach Overview

### ETL Pipeline
| Layer | File | Description |
|---|---|---|
Bronze | `shipments_raw.xlsx` | Raw transactional shipment data  
Silver | `shipment_transformed.csv` | Cleaned & normalized shipment table  
Gold | `shipment_performance.csv` | Aggregated customer performance data mart  

---

## 🧹 Data Cleaning & Transformation Logic (Silver Layer)

### ✅ Standardization
- Normalize status text  
  - Example: `"in-transit"` → `In Transit`, `"DELIVERED"` → `Delivered`
- Parse mixed date formats to `YYYY-MM-DD`
- Remove duplicate rows

### ✅ Data Quality Rules
| Rule | Action |
|---|---|
Delivered but missing delivered_date | Drop row (invalid business logic)  
Delivered but negative duration | Drop row (invalid timeline)  
In-Transit/Pending with no delivered_date | Allowed  
Unknown status | Keep original casing but not mapped  
Duplicate rows | Removed  

### ✅ Derived Columns
| Field | Formula |
|---|---|
`delivery_duration_days` | `delivered_date - booked_date` (only delivered)  
`delivery_delay_days` | `delivered_date - estimated_delivery_date` (only delivered)  
`is_delayed` | `True if delivery_delay_days > 0`  

---

## 📊 Data Mart Logic (Gold Layer)

Aggregation by `customer_id + month_year`:

| Metric | Description |
|---|---|
`total_shipments` | All shipments  
`delivered_shipments` | Count where status = Delivered  
`on_process_shipments` | In Transit + Pending  
`cancelled_shipments` | Cancelled shipments  
`avg_delivery_days` | Mean delivery duration  
`delayed_shipments` | Count delayed deliveries  
`delayed_rate` | delayed_shipments / delivered_shipments (fallback to 0)  

> Join used: **LEFT JOIN** to ensure **no shipment is lost** if customer master incomplete.

---

## 🧾 Files in Project

project/
│── shipments_raw.xlsx              # Raw source data
│── customers_raw.xlsx              # Customer master data
│── etl_shipment.py           # Transformation script (Silver)
│── build_mart.py                   # Data mart script (Gold)
│── shipment_transformed.csv        # Output: cleaned shipment data
│── shipment_performance.csv        # Output: customer monthly performance mart
└── README.md



---

## ▶️ How to Run the Project

### 1️⃣ Install Dependencies

Make sure you have **Python 3.x** installed along with the required libraries:
`pip install pandas numpy`

---

### 2️⃣ Run ETL (Silver Layer)
Run the ETL script to clean and normalize the shipment data:
`python etl_shipment.py`

Output:

`shipment_transformed.csv`

---

### 3️⃣ Build Data Mart (Gold Layer)
Run the script to build the customer shipment performance data mart:
`python build_mart.py`

Output:

`shipment_performance.csv`

---

### 📌 Assumptions & Business Logic
| Area               | Assumption                       |
| ------------------ | -------------------------------- |
| Input format       | Excel input expected             |
| Date parsing       | Mixed date formats allowed       |
| Delivered rows     | Must have `delivered_date`       |
| Non-delivered rows | `delivered_date` can be NULL     |
| Invalid timeline   | Dropped                          |
| Join type          | LEFT JOIN                        |
| Delayed rate       | 0 if no shipments were delivered |

---

### 🧪 Data Quality Validation Performed
The scripts perform:
- Check for missing delivered_date
- Count rows dropped
- Remove negative duration cases
- Print summary logs in console

Example log output:

Dropping 1 delivered rows without delivered_date
Removing 0 invalid delivery rows
shipment_transformed.csv created successfully — shape: (998, 13)
shipment_performance.csv created

---

## 📊 Sample Output

### 🪶 `shipment_transformed.csv` (Silver Layer)

| shipment_id | customer_id | origin_city | destination_city | status    | booked_date | estimated_delivery_date | chargeable_weight_kg | total_amount | delivered_date | delivery_duration_days | delivery_delay_days | is_delayed |
|------------|-------------|------------|-----------------|-----------|------------|------------------------|--------------------|-------------|----------------|-----------------------|-------------------|------------|
| 7          | SHP100999   | 14         | Batam            | Pontianak | Delivered | 2024-02-11             | 2024-02-13         | 13          | 68735          | 2024-02-18           | 7.0               | 5.0        | True       |
| 8          | SHP100336   | 8          | Banjarmasin      | Denpasar  | Delivered | 2024-02-04             | 2024-02-09         | 5           | 49116          | 2024-02-14           | 10.0              | 5.0        | True       |
| 9          | SHP100321   | 11         | Palembang        | Batam     | Delivered | 2024-03-13             | 2024-03-17         | 13          | 105216         | 2024-03-17           | 4.0               | 0.0        | False      |

---

### 💎 `shipment_performance.csv` (Gold Layer)

| customer_id | customer_name | month_year | total_shipments | delivered_shipments | on_process_shipments | cancelled_shipments | avg_delivery_days | delayed_shipments | delayed_rate |
|------------|---------------|------------|----------------|-------------------|--------------------|-------------------|-----------------|-----------------|-------------|
| 1          | Siti Utami    | 2024-01    | 18             | 14                | 2                  | 2                 | 6.285714        | 4               | 0.285714    |
| 1          | Siti Utami    | 2024-02    | 7              | 3                 | 4                  | 0                 | 4.333333        | 0               | 0.000000    |
