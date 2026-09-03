# Logistics Data Analytics — Last-Mile Delivery Optimization

**Internship task:** Week 1 — Strategic Planning and Data Exploration in Logistics
**Role:** Logistics Data Analyst Intern (NSDC)

## Scenario

A mid-size e-commerce logistics operation runs last-mile deliveries across
five zones (North, South, East, West, Central) using a mixed fleet
(bikes, small/large vans, trucks). The company wants to understand where
deliveries are breaching SLA windows, where cost per delivery is highest,
and how routes and dispatch could be optimized.

## KPIs Tracked

1. **On-Time Delivery Rate (OTD%)** — share of deliveries completed within
   the promised SLA window.
2. **Cost Per Delivery (CPD)** — average delivery cost in USD, by zone and
   vehicle type.
3. **Vehicle Utilization Rate** — share of total delivery volume handled
   per vehicle type, used to spot over/under-used fleet segments.

## Project Structure

```
logistics-intern/
├── data/
│   └── generate_sample_data.py   # builds the synthetic delivery dataset
├── src/
│   ├── data_cleaning.py          # dedup, impute, outlier removal
│   ├── eda.py                    # KPI computation + charts
│   ├── clustering.py             # K-Means delivery segmentation
│   ├── regression_model.py       # delivery-time prediction + SLA risk
│   └── route_optimization.py     # nearest-neighbor route sequencing
├── requirements.txt
└── README.md
```

## How to Run

```bash
pip install -r requirements.txt
cd data && python generate_sample_data.py
cd ../src
python data_cleaning.py
python eda.py
python clustering.py
python regression_model.py
python route_optimization.py
```

## Note on Data

This project uses a **synthetically generated dataset** built to mirror
realistic last-mile delivery statistics (distance distributions, peak-hour
congestion effects, vehicle-type cost/speed differences). Real carrier
delivery data is generally proprietary and not publicly released at
order-level granularity, so `generate_sample_data.py` documents every
assumption behind the simulated numbers — see the docstring in that file.

## Methods

- **Regression** (Linear Regression, Random Forest) to predict delivery
  time and flag orders at risk of SLA breach before dispatch.
- **Clustering** (K-Means, silhouette-selected k) to find natural
  operational segments independent of administrative zone boundaries.
- **Optimization** (nearest-neighbor heuristic, with OR-Tools VRP noted
  as the production path) to sequence delivery stops.

Full write-up, literature context, and roadmap are in the submitted
Word report (`Week1_Strategic_Planning_Report.docx`).
