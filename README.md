# APL Logistics — Supply Chain Profitability Dashboard

Customer, Product, and Profitability Performance Analysis in Supply Chain Operations

---

## Overview

This project analyzes order and sales data from APL Logistics (KWE Group) to answer one core question: where is the business actually making money, and where is it bleeding margin?

The output is an interactive Streamlit dashboard that breaks down profitability by customer, product category, market, and discount behavior — built on a dataset of 180,519 orders across 40 fields.

---

## The Problem

High revenue doesn't always mean high profit. After looking at the data, a few things stood out — nearly 1 in 5 orders is loss-making, certain product categories are running margins below 5%, and aggressive discounting is quietly eroding profit across most markets. The business had the data but lacked the visibility.

This dashboard was built to fix that.

---

## Dashboard Modules

| Section | What it covers |
|---|---|
| Revenue & Profit Overview | Top-level KPIs, market-wise revenue vs profit, regional breakdown |
| Customer Value | Most and least profitable customers, segment contribution analysis |
| Product & Category | Margin ranking across all 50 categories, high-revenue low-margin products |
| Discount Impact Analyzer | How discounts affect margins by tier, plus a what-if simulator |

All sections are connected to a global sidebar with filters for market, segment, category, region, and discount rate range.

---

## Key Numbers

- Total Revenue: $36.78M
- Total Profit: $3.97M (10.78% margin)
- Loss-making orders: 18.7% of all transactions
- Worst performing categories: Strength Training (0.6% margin), Men's Clothing (4.6%)
- Europe and LATAM lead on revenue but have room for margin improvement
- Capping discounts at 15% could recover profit on roughly 30% of orders

---

## Tech Stack

- Python 3
- Streamlit
- Pandas
- Plotly

---

## Running Locally

```bash
git clone https://github.com/SuhaniKhanna/apl-logistics-dashboard.git
cd apl-logistics-dashboard
pip install streamlit pandas plotly
streamlit run app.py
```

Make sure `APL_Logistics.csv` is in the same directory as `app.py`.

---

## Live App

[View on Streamlit Cloud](YOUR_STREAMLIT_LINK_HERE)

---

## Project Context

- Internship: Unified Mentor, Data Science Domain
- Client: APL Logistics (KWE Group)
- Domain: Supply Chain, Finance
- Author: Suhani Khanna

---

## Repo Structure

```
apl-logistics-dashboard/
├── app.py
├── APL_Logistics.csv
├── README.md
└── requirements.txt
```
