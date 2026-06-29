import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="APL Logistics | Profitability Dashboard",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0f1117; }
    .metric-card {
        background: linear-gradient(135deg, #1e2130, #252a3a);
        border: 1px solid #2d3250;
        border-radius: 12px;
        padding: 20px 24px;
        text-align: center;
        margin-bottom: 8px;
    }
    .metric-label {
        font-size: 0.78rem;
        color: #8892b0;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 600;
        margin-bottom: 6px;
    }
    .metric-value {
        font-size: 1.9rem;
        font-weight: 700;
        color: #e2e8f0;
        line-height: 1.1;
    }
    .metric-delta-pos { color: #4ade80; font-size: 0.82rem; margin-top: 4px; }
    .metric-delta-neg { color: #f87171; font-size: 0.82rem; margin-top: 4px; }
    .section-header {
        font-size: 1.05rem;
        font-weight: 700;
        color: #a5b4fc;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        margin: 28px 0 12px 0;
        padding-bottom: 6px;
        border-bottom: 1px solid #2d3250;
    }
    .sidebar-label { color: #94a3b8; font-size: 0.8rem; }
    div[data-testid="stMetric"] { background: transparent; }
    .stPlotlyChart { border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("APL_Logistics.csv", encoding="latin-1")
    df["Customer Name"] = df["Customer Fname"].str.strip() + " " + df["Customer Lname"].fillna("").str.strip()
    df["Profit Margin %"] = (df["Order Profit Per Order"] / df["Sales"] * 100).round(2)
    return df

df = load_data()

# ─────────────────────────────────────────────
# SIDEBAR – GLOBAL FILTERS
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📦 APL Logistics")
    st.markdown("**Profitability Intelligence Dashboard**")
    st.divider()

    st.markdown("### 🎛️ Global Filters")

    markets = ["All"] + sorted(df["Market"].dropna().unique().tolist())
    sel_market = st.selectbox("Market", markets)

    segments = ["All"] + sorted(df["Customer Segment"].dropna().unique().tolist())
    sel_segment = st.selectbox("Customer Segment", segments)

    categories = ["All"] + sorted(df["Category Name"].dropna().unique().tolist())
    sel_category = st.selectbox("Product Category", categories)

    regions = ["All"] + sorted(df["Order Region"].dropna().unique().tolist())
    sel_region = st.selectbox("Order Region", regions)

    disc_min, disc_max = float(df["Order Item Discount Rate"].min()), float(df["Order Item Discount Rate"].max())
    sel_discount = st.slider(
        "Discount Rate Range",
        min_value=disc_min, max_value=disc_max,
        value=(disc_min, disc_max), step=0.01,
        format="%.2f"
    )

    st.divider()
    st.caption("Data: APL Logistics (KWE Group) · 180,519 orders")

# ─────────────────────────────────────────────
# APPLY FILTERS
# ─────────────────────────────────────────────
fdf = df.copy()
if sel_market != "All":
    fdf = fdf[fdf["Market"] == sel_market]
if sel_segment != "All":
    fdf = fdf[fdf["Customer Segment"] == sel_segment]
if sel_category != "All":
    fdf = fdf[fdf["Category Name"] == sel_category]
if sel_region != "All":
    fdf = fdf[fdf["Order Region"] == sel_region]
fdf = fdf[
    (fdf["Order Item Discount Rate"] >= sel_discount[0]) &
    (fdf["Order Item Discount Rate"] <= sel_discount[1])
]

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("# 📦 APL Logistics – Profitability Dashboard")
st.markdown(f"Showing **{len(fdf):,}** of {len(df):,} orders after filters")
st.divider()

# ─────────────────────────────────────────────
# TAB NAVIGATION
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Revenue & Profit Overview",
    "👥 Customer Value",
    "🏷️ Product & Category",
    "💸 Discount Impact"
])

# ═══════════════════════════════════════════════════
# TAB 1 — REVENUE & PROFIT OVERVIEW
# ═══════════════════════════════════════════════════
with tab1:
    total_rev = fdf["Sales"].sum()
    total_profit = fdf["Order Profit Per Order"].sum()
    margin_pct = (total_profit / total_rev * 100) if total_rev else 0
    loss_orders = (fdf["Order Profit Per Order"] < 0).sum()
    loss_pct = loss_orders / len(fdf) * 100 if len(fdf) else 0
    avg_order_val = fdf["Sales"].mean()

    c1, c2, c3, c4, c5 = st.columns(5)

    def kpi_card(col, label, value, delta_text, delta_pos=True):
        delta_class = "metric-delta-pos" if delta_pos else "metric-delta-neg"
        col.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="{delta_class}">{delta_text}</div>
        </div>
        """, unsafe_allow_html=True)

    kpi_card(c1, "Total Revenue", f"${total_rev/1e6:.2f}M", "Gross Sales")
    kpi_card(c2, "Total Profit", f"${total_profit/1e6:.2f}M", "After costs", total_profit > 0)
    kpi_card(c3, "Profit Margin", f"{margin_pct:.1f}%", "Revenue retained", margin_pct > 10)
    kpi_card(c4, "Loss Orders", f"{loss_pct:.1f}%", f"{loss_orders:,} orders", loss_pct < 20)
    kpi_card(c5, "Avg Order Value", f"${avg_order_val:.0f}", "Per transaction")

    st.markdown('<div class="section-header">Revenue vs Profit by Market</div>', unsafe_allow_html=True)

    market_data = fdf.groupby("Market").agg(
        Revenue=("Sales", "sum"),
        Profit=("Order Profit Per Order", "sum")
    ).reset_index()
    market_data["Margin %"] = (market_data["Profit"] / market_data["Revenue"] * 100).round(2)
    market_data = market_data.sort_values("Revenue", ascending=False)

    col_a, col_b = st.columns([3, 2])
    with col_a:
        fig = go.Figure()
        fig.add_bar(name="Revenue", x=market_data["Market"], y=market_data["Revenue"],
                    marker_color="#6366f1")
        fig.add_bar(name="Profit", x=market_data["Market"], y=market_data["Profit"],
                    marker_color="#4ade80")
        fig.update_layout(
            barmode="group", template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
            margin=dict(t=10, b=0, l=0, r=0), height=320
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        fig2 = px.bar(
            market_data, x="Margin %", y="Market", orientation="h",
            color="Margin %", color_continuous_scale="RdYlGn",
            text=market_data["Margin %"].apply(lambda x: f"{x:.1f}%")
        )
        fig2.update_layout(
            template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)", coloraxis_showscale=False,
            margin=dict(t=10, b=0, l=0, r=0), height=320,
            xaxis_title="Margin %", yaxis_title=""
        )
        fig2.update_traces(textposition="outside")
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="section-header">Profitability by Order Region</div>', unsafe_allow_html=True)

    region_data = fdf.groupby("Order Region").agg(
        Revenue=("Sales", "sum"),
        Profit=("Order Profit Per Order", "sum"),
        Orders=("Sales", "count")
    ).reset_index()
    region_data["Margin %"] = (region_data["Profit"] / region_data["Revenue"] * 100).round(2)

    fig3 = px.scatter(
        region_data, x="Revenue", y="Profit", size="Orders",
        color="Margin %", text="Order Region",
        color_continuous_scale="RdYlGn",
        hover_data={"Margin %": ":.2f", "Orders": ":,"}
    )
    fig3.update_traces(textposition="top center", marker=dict(opacity=0.85, line=dict(width=1, color="#fff")))
    fig3.update_layout(
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)", height=380,
        margin=dict(t=10, b=0), xaxis_title="Revenue ($)", yaxis_title="Profit ($)"
    )
    st.plotly_chart(fig3, use_container_width=True)

# ═══════════════════════════════════════════════════
# TAB 2 — CUSTOMER VALUE
# ═══════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-header">Customer Profit Contribution</div>', unsafe_allow_html=True)

    cust_data = fdf.groupby(["Customer Id", "Customer Name", "Customer Segment"]).agg(
        Revenue=("Sales", "sum"),
        Profit=("Order Profit Per Order", "sum"),
        Orders=("Sales", "count")
    ).reset_index()
    cust_data["Margin %"] = (cust_data["Profit"] / cust_data["Revenue"] * 100).round(2)
    cust_data = cust_data.sort_values("Profit", ascending=False)

    n_show = st.slider("Number of customers to display (top & bottom)", 5, 30, 10)

    top_cust = cust_data.head(n_show)
    bot_cust = cust_data.tail(n_show).sort_values("Profit")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**🏆 Top Customers by Profit**")
        fig_top = px.bar(
            top_cust, x="Profit", y="Customer Name", orientation="h",
            color="Profit", color_continuous_scale="Greens",
            hover_data={"Revenue": ":,.0f", "Margin %": ":.1f", "Orders": True}
        )
        fig_top.update_layout(
            template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)", coloraxis_showscale=False,
            margin=dict(t=0, b=0, l=0, r=0), height=420, yaxis_title=""
        )
        st.plotly_chart(fig_top, use_container_width=True)

    with col2:
        st.markdown("**⚠️ Bottom Customers by Profit (Loss-Makers)**")
        fig_bot = px.bar(
            bot_cust, x="Profit", y="Customer Name", orientation="h",
            color="Profit", color_continuous_scale="Reds_r",
            hover_data={"Revenue": ":,.0f", "Margin %": ":.1f", "Orders": True}
        )
        fig_bot.update_layout(
            template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)", coloraxis_showscale=False,
            margin=dict(t=0, b=0, l=0, r=0), height=420, yaxis_title=""
        )
        st.plotly_chart(fig_bot, use_container_width=True)

    st.markdown('<div class="section-header">Customer Segment Breakdown</div>', unsafe_allow_html=True)

    seg_data = fdf.groupby("Customer Segment").agg(
        Revenue=("Sales", "sum"),
        Profit=("Order Profit Per Order", "sum"),
        Customers=("Customer Id", "nunique"),
        Orders=("Sales", "count")
    ).reset_index()
    seg_data["Margin %"] = (seg_data["Profit"] / seg_data["Revenue"] * 100).round(2)

    col_a, col_b, col_c = st.columns(3)
    fig_pie_rev = px.pie(seg_data, values="Revenue", names="Customer Segment",
                          color_discrete_sequence=["#6366f1", "#4ade80", "#fb923c"],
                          title="Revenue Share")
    fig_pie_rev.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
                               margin=dict(t=30, b=0), height=300)
    col_a.plotly_chart(fig_pie_rev, use_container_width=True)

    fig_pie_prof = px.pie(seg_data, values="Profit", names="Customer Segment",
                           color_discrete_sequence=["#6366f1", "#4ade80", "#fb923c"],
                           title="Profit Share")
    fig_pie_prof.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
                                margin=dict(t=30, b=0), height=300)
    col_b.plotly_chart(fig_pie_prof, use_container_width=True)

    fig_bar_margin = px.bar(seg_data, x="Customer Segment", y="Margin %",
                             color="Margin %", color_continuous_scale="RdYlGn",
                             text=seg_data["Margin %"].apply(lambda x: f"{x:.1f}%"),
                             title="Margin % by Segment")
    fig_bar_margin.update_traces(textposition="outside")
    fig_bar_margin.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
                                  plot_bgcolor="rgba(0,0,0,0)", coloraxis_showscale=False,
                                  margin=dict(t=30, b=0), height=300)
    col_c.plotly_chart(fig_bar_margin, use_container_width=True)

    # Detailed table
    st.markdown('<div class="section-header">Customer Detail Table</div>', unsafe_allow_html=True)
    view_mode = st.radio("Show", ["Top Profitable", "Loss-Making"], horizontal=True)
    if view_mode == "Top Profitable":
        table_df = cust_data[cust_data["Profit"] > 0].head(50)
    else:
        table_df = cust_data[cust_data["Profit"] < 0].sort_values("Profit").head(50)

    st.dataframe(
        table_df[["Customer Name", "Customer Segment", "Revenue", "Profit", "Margin %", "Orders"]]
        .rename(columns={"Revenue": "Revenue ($)", "Profit": "Profit ($)"})
        .style.format({"Revenue ($)": "${:,.0f}", "Profit ($)": "${:,.0f}", "Margin %": "{:.1f}%"})
        .background_gradient(subset=["Profit ($)"], cmap="RdYlGn"),
        use_container_width=True, height=380
    )

# ═══════════════════════════════════════════════════
# TAB 3 — PRODUCT & CATEGORY
# ═══════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-header">Category Profitability Analysis</div>', unsafe_allow_html=True)

    cat_data = fdf.groupby("Category Name").agg(
        Revenue=("Sales", "sum"),
        Profit=("Order Profit Per Order", "sum"),
        Orders=("Sales", "count")
    ).reset_index()
    cat_data["Margin %"] = (cat_data["Profit"] / cat_data["Revenue"] * 100).round(2)
    cat_data = cat_data.sort_values("Margin %", ascending=False)

    # Heatmap-style bar
    fig_cat = px.bar(
        cat_data, x="Margin %", y="Category Name", orientation="h",
        color="Margin %", color_continuous_scale="RdYlGn",
        hover_data={"Revenue": ":,.0f", "Profit": ":,.0f"},
        text=cat_data["Margin %"].apply(lambda x: f"{x:.1f}%")
    )
    fig_cat.update_traces(textposition="outside")
    fig_cat.update_layout(
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)", coloraxis_showscale=False,
        margin=dict(t=0, b=0), height=max(400, len(cat_data) * 22),
        yaxis=dict(autorange="reversed"), xaxis_title="Profit Margin %", yaxis_title=""
    )
    st.plotly_chart(fig_cat, use_container_width=True)

    st.markdown('<div class="section-header">Revenue vs Profit — Category Bubble Chart</div>', unsafe_allow_html=True)

    fig_bubble = px.scatter(
        cat_data, x="Revenue", y="Profit", size="Orders",
        color="Margin %", text="Category Name",
        color_continuous_scale="RdYlGn",
        hover_data={"Margin %": ":.2f", "Orders": ":,"}
    )
    fig_bubble.add_hline(y=0, line_dash="dash", line_color="#f87171", annotation_text="Break-even")
    fig_bubble.update_traces(textposition="top center", marker=dict(opacity=0.8))
    fig_bubble.update_layout(
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)", height=480,
        margin=dict(t=10, b=0), xaxis_title="Revenue ($)", yaxis_title="Profit ($)"
    )
    st.plotly_chart(fig_bubble, use_container_width=True)

    st.markdown('<div class="section-header">Top Product Analysis</div>', unsafe_allow_html=True)

    prod_data = fdf.groupby("Product Name").agg(
        Revenue=("Sales", "sum"),
        Profit=("Order Profit Per Order", "sum"),
        Orders=("Sales", "count")
    ).reset_index()
    prod_data["Margin %"] = (prod_data["Profit"] / prod_data["Revenue"] * 100).round(2)

    col_p1, col_p2 = st.columns(2)

    with col_p1:
        st.markdown("**🔝 Top 15 Products by Revenue**")
        top_prod = prod_data.sort_values("Revenue", ascending=False).head(15)
        fig_prod = px.bar(
            top_prod, x="Revenue", y="Product Name", orientation="h",
            color="Margin %", color_continuous_scale="RdYlGn",
            hover_data={"Profit": ":,.0f", "Margin %": ":.1f"}
        )
        fig_prod.update_layout(
            template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)", height=480,
            margin=dict(t=0, b=0), yaxis=dict(autorange="reversed"), yaxis_title=""
        )
        st.plotly_chart(fig_prod, use_container_width=True)

    with col_p2:
        st.markdown("**⚠️ High Revenue, Low Margin Products**")
        concern_prod = prod_data[prod_data["Revenue"] > prod_data["Revenue"].quantile(0.5)]
        concern_prod = concern_prod.sort_values("Margin %").head(15)
        fig_concern = px.bar(
            concern_prod, x="Margin %", y="Product Name", orientation="h",
            color="Margin %", color_continuous_scale="RdYlGn",
            hover_data={"Revenue": ":,.0f", "Profit": ":,.0f"}
        )
        fig_concern.update_layout(
            template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)", height=480,
            margin=dict(t=0, b=0), yaxis=dict(autorange="reversed"), yaxis_title=""
        )
        st.plotly_chart(fig_concern, use_container_width=True)

# ═══════════════════════════════════════════════════
# TAB 4 — DISCOUNT IMPACT ANALYZER
# ═══════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-header">Discount Rate vs Profit Ratio</div>', unsafe_allow_html=True)

    # Bin discount rates for cleaner analysis
    disc_data = fdf.copy()
    disc_data["Discount Bucket"] = pd.cut(
        disc_data["Order Item Discount Rate"],
        bins=[-0.01, 0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 1.0],
        labels=["0%", "1–5%", "6–10%", "11–15%", "16–20%", "21–25%", "26–30%", "30%+"]
    )

    disc_agg = disc_data.groupby("Discount Bucket", observed=True).agg(
        Avg_Profit_Ratio=("Order Item Profit Ratio", "mean"),
        Avg_Margin=("Profit Margin %", "mean"),
        Orders=("Sales", "count"),
        Total_Discount=("Order Item Discount", "sum"),
        Total_Profit=("Order Profit Per Order", "sum")
    ).reset_index()

    col_d1, col_d2 = st.columns(2)

    with col_d1:
        fig_disc1 = px.bar(
            disc_agg, x="Discount Bucket", y="Avg_Profit_Ratio",
            color="Avg_Profit_Ratio", color_continuous_scale="RdYlGn",
            text=disc_agg["Avg_Profit_Ratio"].apply(lambda x: f"{x:.2f}"),
            title="Avg Profit Ratio by Discount Tier"
        )
        fig_disc1.add_hline(y=0, line_dash="dash", line_color="#f87171")
        fig_disc1.update_traces(textposition="outside")
        fig_disc1.update_layout(
            template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)", coloraxis_showscale=False,
            margin=dict(t=40, b=0), height=360, yaxis_title="Profit Ratio"
        )
        st.plotly_chart(fig_disc1, use_container_width=True)

    with col_d2:
        fig_disc2 = go.Figure()
        fig_disc2.add_bar(
            x=disc_agg["Discount Bucket"], y=disc_agg["Orders"],
            name="Order Count", marker_color="#6366f1", yaxis="y"
        )
        fig_disc2.add_scatter(
            x=disc_agg["Discount Bucket"], y=disc_agg["Total_Profit"],
            name="Total Profit ($)", mode="lines+markers",
            line=dict(color="#4ade80", width=2), marker=dict(size=7), yaxis="y2"
        )
        fig_disc2.update_layout(
            title="Order Volume vs Total Profit by Discount Tier",
            template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)", height=360,
            margin=dict(t=40, b=0),
            yaxis=dict(title="Orders", side="left"),
            yaxis2=dict(title="Total Profit ($)", overlaying="y", side="right"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02)
        )
        st.plotly_chart(fig_disc2, use_container_width=True)

    # ── WHAT-IF DISCOUNT SIMULATOR ──────────────────
    st.markdown('<div class="section-header">💡 What-If: Discount Scenario Simulator</div>', unsafe_allow_html=True)
    st.markdown("Simulate how changing your discount strategy affects total profit.")

    col_s1, col_s2, col_s3 = st.columns(3)

    with col_s1:
        sim_discount_cap = st.slider(
            "Cap discount rate at (%)", 0.0, 0.30, 0.15, step=0.01,
            format="%.0f%%",
            help="Orders above this discount rate will be capped at this value in the simulation"
        )

    with col_s2:
        # Estimate: each 1% discount reduction improves margin by ~X%
        baseline_profit = fdf["Order Profit Per Order"].sum()
        baseline_discount = fdf["Order Item Discount"].sum()

        capped_df = fdf.copy()
        # For orders above cap, reduce discount and proportionally estimate profit gain
        mask = capped_df["Order Item Discount Rate"] > sim_discount_cap
        excess_discount = capped_df.loc[mask, "Order Item Discount"] * (
            1 - sim_discount_cap / capped_df.loc[mask, "Order Item Discount Rate"]
        )
        recovered_profit = excess_discount.sum()
        sim_profit = baseline_profit + recovered_profit
        sim_margin = (sim_profit / fdf["Sales"].sum() * 100) if fdf["Sales"].sum() else 0

        st.metric("Simulated Total Profit", f"${sim_profit:,.0f}",
                  delta=f"+${recovered_profit:,.0f} vs current")

    with col_s3:
        st.metric("Simulated Margin %", f"{sim_margin:.2f}%",
                  delta=f"+{sim_margin - (baseline_profit/fdf['Sales'].sum()*100 if fdf['Sales'].sum() else 0):.2f}%")

    # Orders affected
    affected = (fdf["Order Item Discount Rate"] > sim_discount_cap).sum()
    st.info(f"**{affected:,} orders** ({affected/len(fdf)*100:.1f}%) would be affected by capping discounts at {sim_discount_cap*100:.0f}%.")

    # Scatter of discount rate vs profit ratio (sampled)
    st.markdown('<div class="section-header">Discount Rate vs Profit Ratio — Distribution</div>', unsafe_allow_html=True)

    sample = fdf.sample(min(5000, len(fdf)), random_state=42)
    fig_scatter = px.scatter(
        sample,
        x="Order Item Discount Rate", y="Order Item Profit Ratio",
        color="Customer Segment", opacity=0.5,
        color_discrete_sequence=["#6366f1", "#4ade80", "#fb923c"],
        labels={"Order Item Discount Rate": "Discount Rate", "Order Item Profit Ratio": "Profit Ratio"}
    )
    fig_scatter.add_hline(y=0, line_dash="dash", line_color="#f87171", annotation_text="Break-even")
    fig_scatter.add_vline(x=sim_discount_cap, line_dash="dot", line_color="#facc15",
                           annotation_text=f"Cap: {sim_discount_cap*100:.0f}%")
    fig_scatter.update_layout(
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)", height=420,
        margin=dict(t=10, b=0)
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    # Category discount breakdown table
    st.markdown('<div class="section-header">Discount Impact by Category</div>', unsafe_allow_html=True)

    cat_disc = fdf.groupby("Category Name").agg(
        Avg_Discount_Rate=("Order Item Discount Rate", "mean"),
        Total_Discount=("Order Item Discount", "sum"),
        Total_Profit=("Order Profit Per Order", "sum"),
        Avg_Margin=("Profit Margin %", "mean")
    ).reset_index().sort_values("Total_Discount", ascending=False).head(20)

    cat_disc["Avg_Discount_Rate"] = (cat_disc["Avg_Discount_Rate"] * 100).round(2)
    cat_disc["Avg_Margin"] = cat_disc["Avg_Margin"].round(2)

    st.dataframe(
        cat_disc.rename(columns={
            "Category Name": "Category",
            "Avg_Discount_Rate": "Avg Discount Rate (%)",
            "Total_Discount": "Total Discount Given ($)",
            "Total_Profit": "Total Profit ($)",
            "Avg_Margin": "Avg Margin (%)"
        }).style.format({
            "Total Discount Given ($)": "${:,.0f}",
            "Total Profit ($)": "${:,.0f}",
            "Avg Discount Rate (%)": "{:.2f}%",
            "Avg Margin (%)": "{:.2f}%"
        }).background_gradient(subset=["Total Profit ($)"], cmap="RdYlGn"),
        use_container_width=True, height=420
    )

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.divider()
st.caption("APL Logistics (KWE Group) · Customer, Product & Profitability Performance Analysis · Unified Mentor Internship")
