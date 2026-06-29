import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="APL Logistics | Profitability Analysis",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background-color: #0d0f14; }
    [data-testid="stSidebar"] { background-color: #111318; border-right: 1px solid #1f2130; }

    .kpi-block {
        background-color: #13161f;
        border: 1px solid #1e2235;
        border-radius: 8px;
        padding: 18px 20px;
        text-align: center;
    }
    .kpi-label {
        font-size: 0.72rem;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        font-weight: 600;
        margin-bottom: 8px;
    }
    .kpi-value {
        font-size: 1.75rem;
        font-weight: 700;
        color: #f1f5f9;
        line-height: 1;
    }
    .kpi-sub { font-size: 0.75rem; color: #4b5563; margin-top: 5px; }
    .kpi-pos { color: #34d399; }
    .kpi-neg { color: #f87171; }

    .section-title {
        font-size: 0.78rem;
        font-weight: 700;
        color: #6366f1;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        margin: 32px 0 10px 0;
        padding-bottom: 8px;
        border-bottom: 1px solid #1e2235;
    }
    .analyst-note {
        background-color: #13161f;
        border-left: 3px solid #6366f1;
        padding: 10px 14px;
        border-radius: 0 6px 6px 0;
        font-size: 0.82rem;
        color: #9ca3af;
        margin: 10px 0 20px 0;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    df = pd.read_csv("APL_Logistics.csv", encoding="latin-1")
    df["Customer Name"] = (
        df["Customer Fname"].str.strip() + " " +
        df["Customer Lname"].fillna("").str.strip()
    )
    df["Profit Margin %"] = (
        df["Order Profit Per Order"] / df["Sales"] * 100
    ).round(2)
    return df


df = load_data()

COLORS = ["#6366f1", "#34d399", "#fb923c", "#f472b6", "#60a5fa"]


def base_layout(fig, height=360, coloraxis_showscale=None, margin=None, **kwargs):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=margin if margin is not None else dict(t=10, b=10, l=10, r=10),
        height=height,
        font=dict(size=12),
        **kwargs
    )
    if coloraxis_showscale is not None:
        fig.update_coloraxes(showscale=coloraxis_showscale)
    return fig


# ── SIDEBAR ────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### APL Logistics")
    st.markdown(
        "<span style='color:#6b7280;font-size:0.8rem'>Profitability Analysis Dashboard</span>",
        unsafe_allow_html=True
    )
    st.divider()
    st.markdown("**Filters**")
    st.caption("Defaults show full dataset. Narrow down by market, segment, or category.")

    sel_market = st.selectbox(
        "Market",
        ["All"] + sorted(df["Market"].dropna().unique().tolist())
    )
    sel_segment = st.selectbox(
        "Customer Segment",
        ["All"] + sorted(df["Customer Segment"].dropna().unique().tolist())
    )
    sel_category = st.selectbox(
        "Product Category",
        ["All"] + sorted(df["Category Name"].dropna().unique().tolist())
    )
    sel_region = st.selectbox(
        "Order Region",
        ["All"] + sorted(df["Order Region"].dropna().unique().tolist())
    )

    disc_min = float(df["Order Item Discount Rate"].min())
    disc_max = float(df["Order Item Discount Rate"].max())
    sel_discount = st.slider(
        "Discount Rate Range",
        min_value=disc_min, max_value=disc_max,
        value=(disc_min, disc_max), step=0.01, format="%.2f"
    )

    st.divider()
    st.caption("180,519 orders · 40 fields")
    st.caption("Source: APL Logistics (KWE Group)")

# ── APPLY FILTERS ──────────────────────────────────────────
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

# ── HEADER ─────────────────────────────────────────────────
st.markdown("## APL Logistics — Profitability Intelligence")
st.markdown(
    f"<span style='color:#6b7280;font-size:0.85rem'>"
    f"Showing {len(fdf):,} of {len(df):,} orders after filters applied</span>",
    unsafe_allow_html=True
)
st.divider()

tab1, tab2, tab3, tab4 = st.tabs([
    "Revenue & Profit",
    "Customer Value",
    "Product & Category",
    "Discount Impact"
])


# ══════════════════════════════════════════════════════════
# TAB 1 — REVENUE & PROFIT
# ══════════════════════════════════════════════════════════
with tab1:
    total_rev = fdf["Sales"].sum()
    total_profit = fdf["Order Profit Per Order"].sum()
    margin_pct = (total_profit / total_rev * 100) if total_rev else 0
    loss_orders = int((fdf["Order Profit Per Order"] < 0).sum())
    loss_pct = loss_orders / len(fdf) * 100 if len(fdf) else 0
    avg_order = fdf["Sales"].mean()

    c1, c2, c3, c4, c5 = st.columns(5)

    def kpi(col, label, value, sub, pos=True):
        sub_class = "kpi-pos" if pos else "kpi-neg"
        col.markdown(f"""
        <div class="kpi-block">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-sub {sub_class}">{sub}</div>
        </div>""", unsafe_allow_html=True)

    kpi(c1, "Total Revenue", f"${total_rev/1e6:.2f}M", "gross sales")
    kpi(c2, "Total Profit", f"${total_profit/1e6:.2f}M", "after costs", total_profit > 0)
    kpi(c3, "Profit Margin", f"{margin_pct:.1f}%", "of revenue retained", margin_pct > 10)
    kpi(c4, "Loss Order Rate", f"{loss_pct:.1f}%", f"{loss_orders:,} unprofitable orders", loss_pct < 20)
    kpi(c5, "Avg Order Value", f"${avg_order:.0f}", "per transaction")

    st.markdown('<div class="section-title">Revenue vs. Profit by Market</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="analyst-note">Europe and LATAM lead on volume, but margin compression is visible across all markets — '
        'high revenue does not reliably translate to high profit here.</div>',
        unsafe_allow_html=True
    )

    mkt = fdf.groupby("Market").agg(
        Revenue=("Sales", "sum"),
        Profit=("Order Profit Per Order", "sum")
    ).reset_index()
    mkt["Margin %"] = (mkt["Profit"] / mkt["Revenue"] * 100).round(2)
    mkt = mkt.sort_values("Revenue", ascending=False)

    col_a, col_b = st.columns([3, 2])
    with col_a:
        fig = go.Figure()
        fig.add_bar(
            name="Revenue", x=mkt["Market"], y=mkt["Revenue"],
            marker_color="#6366f1"
        )
        fig.add_bar(
            name="Profit", x=mkt["Market"], y=mkt["Profit"],
            marker_color="#34d399"
        )
        base_layout(
            fig, barmode="group",
            legend=dict(orientation="h", yanchor="bottom", y=1.02)
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        fig2 = px.bar(
            mkt, x="Margin %", y="Market", orientation="h",
            color="Margin %", color_continuous_scale="RdYlGn",
            text=mkt["Margin %"].apply(lambda x: f"{x:.1f}%")
        )
        fig2.update_traces(textposition="outside")
        base_layout(
            fig2, coloraxis_showscale=False,
            xaxis_title="Margin %", yaxis_title=""
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="section-title">Profitability by Order Region</div>', unsafe_allow_html=True)

    reg = fdf.groupby("Order Region").agg(
        Revenue=("Sales", "sum"),
        Profit=("Order Profit Per Order", "sum"),
        Orders=("Sales", "count")
    ).reset_index()
    reg["Margin %"] = (reg["Profit"] / reg["Revenue"] * 100).round(2)

    fig3 = px.scatter(
        reg, x="Revenue", y="Profit", size="Orders",
        color="Margin %", text="Order Region",
        color_continuous_scale="RdYlGn",
        hover_data={"Margin %": ":.2f", "Orders": ":,"}
    )
    fig3.update_traces(
        textposition="top center",
        marker=dict(opacity=0.85, line=dict(width=1, color="#1e2235"))
    )
    base_layout(
        fig3, height=400,
        xaxis_title="Revenue ($)", yaxis_title="Profit ($)"
    )
    st.plotly_chart(fig3, use_container_width=True)


# ══════════════════════════════════════════════════════════
# TAB 2 — CUSTOMER VALUE
# ══════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-title">Customer Profit Ranking</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="analyst-note">Customers with the highest revenue are not always the most profitable. '
        'The bottom segment often signals pricing or discount policy issues rather than low volume.</div>',
        unsafe_allow_html=True
    )

    cust = fdf.groupby(["Customer Id", "Customer Name", "Customer Segment"]).agg(
        Revenue=("Sales", "sum"),
        Profit=("Order Profit Per Order", "sum"),
        Orders=("Sales", "count")
    ).reset_index()
    cust["Margin %"] = (cust["Profit"] / cust["Revenue"] * 100).round(2)
    cust = cust.sort_values("Profit", ascending=False)

    n_show = st.slider("Customers to display (top & bottom)", 5, 30, 10)

    top_c = cust.head(n_show)
    bot_c = cust.tail(n_show).sort_values("Profit")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Top customers by profit**")
        fig_t = px.bar(
            top_c, x="Profit", y="Customer Name", orientation="h",
            color="Profit", color_continuous_scale="Greens",
            hover_data={"Revenue": ":,.0f", "Margin %": ":.1f", "Orders": True}
        )
        base_layout(fig_t, height=420, coloraxis_showscale=False, yaxis_title="")
        st.plotly_chart(fig_t, use_container_width=True)

    with col2:
        st.markdown("**Bottom customers by profit**")
        fig_b = px.bar(
            bot_c, x="Profit", y="Customer Name", orientation="h",
            color="Profit", color_continuous_scale="Reds_r",
            hover_data={"Revenue": ":,.0f", "Margin %": ":.1f", "Orders": True}
        )
        base_layout(fig_b, height=420, coloraxis_showscale=False, yaxis_title="")
        st.plotly_chart(fig_b, use_container_width=True)

    st.markdown('<div class="section-title">Segment Breakdown</div>', unsafe_allow_html=True)

    seg = fdf.groupby("Customer Segment").agg(
        Revenue=("Sales", "sum"),
        Profit=("Order Profit Per Order", "sum"),
        Customers=("Customer Id", "nunique"),
        Orders=("Sales", "count")
    ).reset_index()
    seg["Margin %"] = (seg["Profit"] / seg["Revenue"] * 100).round(2)

    ca, cb, cc = st.columns(3)

    fig_pr = px.pie(
        seg, values="Revenue", names="Customer Segment",
        color_discrete_sequence=COLORS, title="Revenue share by segment"
    )
    fig_pr.update_layout(
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=40, b=0), height=280
    )
    ca.plotly_chart(fig_pr, use_container_width=True)

    fig_pp = px.pie(
        seg, values="Profit", names="Customer Segment",
        color_discrete_sequence=COLORS, title="Profit share by segment"
    )
    fig_pp.update_layout(
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=40, b=0), height=280
    )
    cb.plotly_chart(fig_pp, use_container_width=True)

    fig_pm = px.bar(
        seg, x="Customer Segment", y="Margin %",
        color="Margin %", color_continuous_scale="RdYlGn",
        text=seg["Margin %"].apply(lambda x: f"{x:.1f}%"),
        title="Profit margin by segment"
    )
    fig_pm.update_traces(textposition="outside")
    base_layout(
        fig_pm, height=280, coloraxis_showscale=False,
        margin=dict(t=40, b=0)
    )
    cc.plotly_chart(fig_pm, use_container_width=True)

    st.markdown('<div class="section-title">Customer Detail</div>', unsafe_allow_html=True)

    view = st.radio("Show", ["Most profitable", "Loss-making"], horizontal=True)
    if view == "Most profitable":
        tbl = cust[cust["Profit"] > 0].head(50).copy()
    else:
        tbl = cust[cust["Profit"] < 0].sort_values("Profit").head(50).copy()

    tbl_display = tbl[["Customer Name", "Customer Segment", "Revenue", "Profit", "Margin %", "Orders"]].copy()
    tbl_display["Revenue"] = tbl_display["Revenue"].apply(lambda x: f"${x:,.0f}")
    tbl_display["Profit"] = tbl_display["Profit"].apply(lambda x: f"${x:,.0f}")
    tbl_display["Margin %"] = tbl_display["Margin %"].apply(lambda x: f"{x:.1f}%")
    tbl_display.columns = ["Customer", "Segment", "Revenue", "Profit", "Margin", "Orders"]

    st.dataframe(tbl_display, use_container_width=True, height=380, hide_index=True)


# ══════════════════════════════════════════════════════════
# TAB 3 — PRODUCT & CATEGORY
# ══════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-title">Category Margin Ranking</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="analyst-note">Strength Training sits at 0.6% margin — effectively a break-even category. '
        'Men\'s Clothing at 4.6% is similarly concerning given its order volume. '
        'Both warrant a pricing review before the next planning cycle.</div>',
        unsafe_allow_html=True
    )

    cat = fdf.groupby("Category Name").agg(
        Revenue=("Sales", "sum"),
        Profit=("Order Profit Per Order", "sum"),
        Orders=("Sales", "count")
    ).reset_index()
    cat["Margin %"] = (cat["Profit"] / cat["Revenue"] * 100).round(2)
    cat = cat.sort_values("Margin %", ascending=False)

    fig_cat = px.bar(
        cat, x="Margin %", y="Category Name", orientation="h",
        color="Margin %", color_continuous_scale="RdYlGn",
        hover_data={"Revenue": ":,.0f", "Profit": ":,.0f"},
        text=cat["Margin %"].apply(lambda x: f"{x:.1f}%")
    )
    fig_cat.update_traces(textposition="outside")
    base_layout(
        fig_cat,
        height=max(420, len(cat) * 22),
        coloraxis_showscale=False,
        yaxis=dict(autorange="reversed"),
        xaxis_title="Profit Margin %",
        yaxis_title=""
    )
    st.plotly_chart(fig_cat, use_container_width=True)

    st.markdown('<div class="section-title">Revenue vs. Profit by Category</div>', unsafe_allow_html=True)

    fig_bub = px.scatter(
        cat, x="Revenue", y="Profit", size="Orders",
        color="Margin %", text="Category Name",
        color_continuous_scale="RdYlGn",
        hover_data={"Margin %": ":.2f", "Orders": ":,"}
    )
    fig_bub.add_hline(
        y=0, line_dash="dash", line_color="#f87171",
        annotation_text="Break-even line"
    )
    fig_bub.update_traces(textposition="top center", marker=dict(opacity=0.8))
    base_layout(
        fig_bub, height=480,
        xaxis_title="Revenue ($)", yaxis_title="Profit ($)"
    )
    st.plotly_chart(fig_bub, use_container_width=True)

    st.markdown('<div class="section-title">Product-Level View</div>', unsafe_allow_html=True)

    prod = fdf.groupby("Product Name").agg(
        Revenue=("Sales", "sum"),
        Profit=("Order Profit Per Order", "sum"),
        Orders=("Sales", "count")
    ).reset_index()
    prod["Margin %"] = (prod["Profit"] / prod["Revenue"] * 100).round(2)

    cp1, cp2 = st.columns([3, 2])

    with cp1:
        st.markdown("**Top 15 products by revenue**")
        top_prod = prod.sort_values("Revenue", ascending=False).head(15)
        fig_tp = px.bar(
            top_prod, x="Revenue", y="Product Name", orientation="h",
            color="Margin %", color_continuous_scale="RdYlGn",
            hover_data={"Profit": ":,.0f", "Margin %": ":.1f"}
        )
        base_layout(
            fig_tp, height=480,
            yaxis=dict(autorange="reversed"), yaxis_title=""
        )
        st.plotly_chart(fig_tp, use_container_width=True)

    with cp2:
        st.markdown("**High revenue, weak margin — products to watch**")
        at_risk = prod[prod["Revenue"] > prod["Revenue"].quantile(0.5)]
        at_risk = at_risk.sort_values("Margin %").head(15)
        fig_ar = px.bar(
            at_risk, x="Margin %", y="Product Name", orientation="h",
            color="Margin %", color_continuous_scale="RdYlGn",
            hover_data={"Revenue": ":,.0f", "Profit": ":,.0f"}
        )
        base_layout(
            fig_ar, height=480,
            yaxis=dict(autorange="reversed"), yaxis_title=""
        )
        st.plotly_chart(fig_ar, use_container_width=True)


# ══════════════════════════════════════════════════════════
# TAB 4 — DISCOUNT IMPACT
# ══════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-title">Profit Ratio by Discount Tier</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="analyst-note">Discounting beyond 20% shows a clear and consistent drop in profit ratio. '
        'The 30%+ tier is where most margin destruction happens — '
        'and it affects a non-trivial share of total order volume.</div>',
        unsafe_allow_html=True
    )

    disc = fdf.copy()
    disc["Discount Bucket"] = pd.cut(
        disc["Order Item Discount Rate"],
        bins=[-0.01, 0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 1.0],
        labels=["0%", "1-5%", "6-10%", "11-15%", "16-20%", "21-25%", "26-30%", "30%+"]
    )
    disc_agg = disc.groupby("Discount Bucket", observed=True).agg(
        Avg_Profit_Ratio=("Order Item Profit Ratio", "mean"),
        Orders=("Sales", "count"),
        Total_Discount=("Order Item Discount", "sum"),
        Total_Profit=("Order Profit Per Order", "sum")
    ).reset_index()

    cd1, cd2 = st.columns(2)

    with cd1:
        fig_d1 = px.bar(
            disc_agg, x="Discount Bucket", y="Avg_Profit_Ratio",
            color="Avg_Profit_Ratio", color_continuous_scale="RdYlGn",
            text=disc_agg["Avg_Profit_Ratio"].apply(lambda x: f"{x:.2f}"),
            title="Avg profit ratio per discount tier"
        )
        fig_d1.add_hline(y=0, line_dash="dash", line_color="#f87171")
        fig_d1.update_traces(textposition="outside")
        base_layout(
            fig_d1, height=360, coloraxis_showscale=False,
            margin=dict(t=40, b=10, l=10, r=10),
            yaxis_title="Profit Ratio"
        )
        st.plotly_chart(fig_d1, use_container_width=True)

    with cd2:
        fig_d2 = go.Figure()
        fig_d2.add_bar(
            x=disc_agg["Discount Bucket"], y=disc_agg["Orders"],
            name="Order count", marker_color="#6366f1", yaxis="y"
        )
        fig_d2.add_scatter(
            x=disc_agg["Discount Bucket"], y=disc_agg["Total_Profit"],
            name="Total profit ($)", mode="lines+markers",
            line=dict(color="#34d399", width=2),
            marker=dict(size=7), yaxis="y2"
        )
        fig_d2.update_layout(
            title="Order volume vs. total profit by discount tier",
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=360,
            margin=dict(t=40, b=10, l=10, r=10),
            yaxis=dict(title="Orders", side="left"),
            yaxis2=dict(title="Total Profit ($)", overlaying="y", side="right"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02)
        )
        st.plotly_chart(fig_d2, use_container_width=True)

    st.markdown('<div class="section-title">What-If: Discount Cap Simulator</div>', unsafe_allow_html=True)
    st.markdown(
        "<span style='color:#6b7280;font-size:0.85rem'>"
        "Use this to estimate how much profit could be recovered by capping discounts at a given rate."
        "</span>",
        unsafe_allow_html=True
    )

    cs1, cs2, cs3 = st.columns(3)
    with cs1:
        sim_cap = st.slider(
            "Cap discount rate at", 0.0, 0.30, 0.15, step=0.01,
            format="%.2f",
            help="Any order above this discount rate will be recalculated at the cap in the simulation"
        )

    baseline_profit = fdf["Order Profit Per Order"].sum()
    mask = fdf["Order Item Discount Rate"] > sim_cap
    excess = fdf.loc[mask, "Order Item Discount"] * (
        1 - sim_cap / fdf.loc[mask, "Order Item Discount Rate"]
    )
    recovered = excess.sum()
    sim_profit = baseline_profit + recovered
    sim_margin = (sim_profit / fdf["Sales"].sum() * 100) if fdf["Sales"].sum() else 0
    base_margin = (baseline_profit / fdf["Sales"].sum() * 100) if fdf["Sales"].sum() else 0

    with cs2:
        st.metric(
            "Simulated Profit",
            f"${sim_profit:,.0f}",
            delta=f"+${recovered:,.0f} recovered"
        )
    with cs3:
        st.metric(
            "Simulated Margin",
            f"{sim_margin:.2f}%",
            delta=f"+{sim_margin - base_margin:.2f}%"
        )

    affected = int(mask.sum())
    st.info(
        f"{affected:,} orders ({affected/len(fdf)*100:.1f}%) would be affected "
        f"by capping discounts at {sim_cap*100:.0f}%."
    )

    st.markdown('<div class="section-title">Discount Rate vs. Profit Ratio — Order Distribution</div>', unsafe_allow_html=True)

    sample = fdf.sample(min(5000, len(fdf)), random_state=42)
    fig_sc = px.scatter(
        sample,
        x="Order Item Discount Rate",
        y="Order Item Profit Ratio",
        color="Customer Segment",
        opacity=0.45,
        color_discrete_sequence=COLORS,
        labels={
            "Order Item Discount Rate": "Discount Rate",
            "Order Item Profit Ratio": "Profit Ratio"
        }
    )
    fig_sc.add_hline(
        y=0, line_dash="dash", line_color="#f87171",
        annotation_text="Break-even"
    )
    fig_sc.add_vline(
        x=sim_cap, line_dash="dot", line_color="#facc15",
        annotation_text=f"Cap: {sim_cap*100:.0f}%"
    )
    base_layout(fig_sc, height=420)
    st.plotly_chart(fig_sc, use_container_width=True)

    st.markdown('<div class="section-title">Discount Impact by Category</div>', unsafe_allow_html=True)

    cat_disc = fdf.groupby("Category Name").agg(
        Avg_Discount_Rate=("Order Item Discount Rate", "mean"),
        Total_Discount=("Order Item Discount", "sum"),
        Total_Profit=("Order Profit Per Order", "sum"),
        Avg_Margin=("Profit Margin %", "mean")
    ).reset_index().sort_values("Total_Discount", ascending=False).head(20)

    cat_disc_display = cat_disc.copy()
    cat_disc_display["Avg_Discount_Rate"] = cat_disc_display["Avg_Discount_Rate"].apply(lambda x: f"{x*100:.2f}%")
    cat_disc_display["Total_Discount"] = cat_disc_display["Total_Discount"].apply(lambda x: f"${x:,.0f}")
    cat_disc_display["Total_Profit"] = cat_disc_display["Total_Profit"].apply(lambda x: f"${x:,.0f}")
    cat_disc_display["Avg_Margin"] = cat_disc_display["Avg_Margin"].apply(lambda x: f"{x:.2f}%")
    cat_disc_display.columns = ["Category", "Avg Discount Rate", "Total Discount Given", "Total Profit", "Avg Margin"]

    st.dataframe(cat_disc_display, use_container_width=True, height=420, hide_index=True)

st.divider()
st.markdown(
    "<span style='color:#374151;font-size:0.75rem'>"
    "APL Logistics (KWE Group) · Supply Chain Profitability Analysis · Unified Mentor Internship"
    "</span>",
    unsafe_allow_html=True
)
