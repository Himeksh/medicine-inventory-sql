import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from db_config import get_connection

st.set_page_config(page_title="Inventory Dashboard", layout="wide")
st.title("Medicine Inventory & Sales Dashboard")

# === Load Data ===
conn = get_connection()

# Supplier Dropdown Data
supplier_query = "SELECT DISTINCT name FROM suppliers"
suppliers_list = pd.read_sql(supplier_query, conn)['name'].tolist()

# Sidebar Filters
st.sidebar.header("Filters")

# Date Range
min_date = datetime(2020, 1, 1)
max_date = datetime.today()
start_date, end_date = st.sidebar.date_input("Select Date Range:", [min_date, max_date])
start_dt = datetime.combine(start_date, datetime.min.time())
end_dt = datetime.combine(end_date, datetime.max.time())

# Supplier Filter
supplier_filter = st.sidebar.selectbox("Filter by Supplier", ["All"] + suppliers_list)

# Inventory Status Filter
status_filter = st.sidebar.radio("Inventory Status", ["All", "Expired", "Near Expiry", "OK"])

# === Sales Data ===
sales_query = """
    SELECT s.sale_date, m.name AS medicine_name, s.quantity_sold, sup.name AS supplier_name
    FROM sales s
    JOIN medicines m ON s.med_id = m.med_id
    JOIN medicine_supplier ms ON ms.med_id = m.med_id
    JOIN suppliers sup ON sup.supplier_id = ms.supplier_id
"""
df_sales = pd.read_sql(sales_query, conn)
df_sales["sale_date"] = pd.to_datetime(df_sales["sale_date"])

# Apply Sales Filters
sales_mask = (df_sales["sale_date"] >= start_dt) & (df_sales["sale_date"] <= end_dt)
if supplier_filter != "All":
    sales_mask &= (df_sales["supplier_name"] == supplier_filter)
filtered_sales = df_sales[sales_mask]

# === Inventory Data ===
inventory_query = """
    SELECT m.med_id, m.name, m.category, m.quantity, m.price, m.expiry_date, m.added_on, sup.name AS supplier_name
    FROM medicines m
    JOIN medicine_supplier ms ON m.med_id = ms.med_id
    JOIN suppliers sup ON sup.supplier_id = ms.supplier_id
    WHERE m.added_on BETWEEN %s AND %s
"""
df_inventory = pd.read_sql(inventory_query, conn, params=(start_dt, end_dt))
df_inventory["expiry_date"] = pd.to_datetime(df_inventory["expiry_date"])
df_inventory["added_on"] = pd.to_datetime(df_inventory["added_on"])

# Status Column
today = datetime.today().date()
df_inventory["status"] = df_inventory["expiry_date"].dt.date.apply(
    lambda d: "Expired" if d < today else "Near Expiry" if d <= (today + timedelta(days=30)) else "OK"
)

# Apply Inventory Filters
if supplier_filter != "All":
    df_inventory = df_inventory[df_inventory["supplier_name"] == supplier_filter]
if status_filter != "All":
    df_inventory = df_inventory[df_inventory["status"] == status_filter]

# === Supplier Cost Summary ===
cost_query = """
    SELECT sup.name AS Supplier, ROUND(SUM(m.quantity * m.price), 2) AS Total_Cost
    FROM medicines m
    JOIN medicine_supplier ms ON ms.med_id = m.med_id
    JOIN suppliers sup ON sup.supplier_id = ms.supplier_id
    WHERE m.added_on BETWEEN %s AND %s
    GROUP BY sup.name
"""
df_suppliers = pd.read_sql(cost_query, conn, params=(start_dt, end_dt))
if supplier_filter != "All":
    df_suppliers = df_suppliers[df_suppliers["Supplier"] == supplier_filter]

conn.close()

# === Charts ===

# Line Chart: Daily Sales
sales_chart = filtered_sales.groupby("sale_date")["quantity_sold"].sum().reset_index()
fig_line = px.line(sales_chart, x="sale_date", y="quantity_sold", title="Daily Sales")

# Pie Chart: Inventory by Category
cat_dist = df_inventory.groupby("category")["quantity"].sum().reset_index()
fig_pie = px.pie(cat_dist, names="category", values="quantity", title="Stock by Category")

# Bar Chart: Top-Selling Medicines
top_meds = filtered_sales.groupby("medicine_name")["quantity_sold"].sum().reset_index().sort_values(by="quantity_sold", ascending=False).head(10)
fig_bar = px.bar(top_meds, x="medicine_name", y="quantity_sold", title="Top-Selling Medicines")

# Bar Chart: Supplier Cost Summary
fig_cost = px.bar(df_suppliers, x="Supplier", y="Total_Cost", title="Supplier Cost Summary")

# === KPIs ===
st.markdown("### Key Metrics")
col1, col2, col3 = st.columns(3)
col1.metric("Total Sales", int(filtered_sales["quantity_sold"].sum()))
col2.metric("Inventory Qty", int(df_inventory["quantity"].sum()))
col3.metric("Expired Items", df_inventory[df_inventory["status"] == "Expired"].shape[0])

# === Show Charts ===
st.plotly_chart(fig_line, use_container_width=True)

col4, col5 = st.columns(2)
col4.plotly_chart(fig_pie, use_container_width=True)
col5.plotly_chart(fig_bar, use_container_width=True)

st.plotly_chart(fig_cost, use_container_width=True)

# === Show Tables ===
st.markdown("### Filtered Sales Data")
st.dataframe(filtered_sales)

st.markdown("### Current Inventory")
st.dataframe(df_inventory)

st.markdown("### Supplier Cost Summary")
st.dataframe(df_suppliers)
