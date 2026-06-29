# 📦 APL Logistics — Supply Chain Profitability Dashboard

**Customer, Product, and Profitability Performance Analysis in Supply Chain Operations**

A data-driven Streamlit web application built to uncover margin intelligence, customer value, and discount-driven profit erosion for APL Logistics (KWE Group).

---

## 🔍 Problem Statement

Despite having detailed order and sales data across 180,000+ transactions, APL Logistics lacked:
- Visibility into profitability by customer and product
- Understanding of how discounts erode margins
- Identification of high-value vs loss-making customers
- Market and category-level profit diagnostics

This dashboard delivers **commercial intelligence** — shifting focus from operational efficiency to **profit-first decision making**.

---

## 📊 Dashboard Modules

| Tab | What it shows |
|-----|--------------|
| **Revenue & Profit Overview** | KPI cards, market-level revenue vs profit, regional scatter analysis |
| **Customer Value Dashboard** | Top/bottom customers by profit, segment breakdown, drilldown table |
| **Product & Category Analysis** | Category margin heatmap, bubble chart, high-revenue low-margin products |
| **Discount Impact Analyzer** | Discount tier analysis, what-if simulator, category discount breakdown |

---

## 💡 Key Findings

- **Total Revenue:** $36.78M across 180,519 orders
- **Total Profit:** $3.97M — an overall margin of **10.78%**
- **18.7% of orders are loss-making** — driven largely by aggressive discounting
- **Europe and LATAM** generate the highest revenue but margin optimization is needed
- **Strength Training and Men's Clothing** categories have dangerously thin margins (under 5%)
- Customers with highest revenue are not always the most profitable — profit-blind pricing is a real risk
- Capping discounts at 15% could recover significant profit across 30%+ of orders

---

## 🛠️ Tech Stack

- **Python 3.x**
- **Streamlit** — interactive web dashboard
- **Pandas** — data cleaning and aggregation
- **Plotly** — interactive visualizations

---

## 📁 Dataset

- **Source:** APL Logistics (KWE Group) via Unified Mentor
- **Size:** 180,519 rows × 40 columns
- **Domains:** Supply Chain, Finance
- **Key fields:** Sales, Profit Per Order, Discount Rate, Customer Segment, Market, Category, Region

---

## 🚀 How to Run Locally

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/apl-logistics-dashboard.git
cd apl-logistics-dashboard

# 2. Install dependencies
pip install streamlit pandas plotly

# 3. Run the app
streamlit run app.py
```

> Make sure `APL_Logistics.csv` is in the same folder as `app.py`

---

## 🌐 Live Dashboard

👉 [View Live on Streamlit Cloud](YOUR_STREAMLIT_LINK_HERE)

---

## 📌 Project Context

- **Internship:** Unified Mentor — Data Science Domain
- **Client:** APL Logistics (KWE Group)
- **Domain:** Supply Chain · Finance
- **Analyst:** Suhani Khanna

---

## 📂 Repository Structure

```
apl-logistics-dashboard/
│
├── app.py                  # Main Streamlit dashboard
├── APL_Logistics.csv       # Dataset (180,519 rows)
├── README.md               # Project documentation
└── requirements.txt        # Python dependencies
```
