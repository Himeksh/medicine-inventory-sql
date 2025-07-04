# dashboard.py

import streamlit as st
import pandas as pd
from db_config import get_connection
from datetime import datetime, timedelta

# Page Config
st.set_page_config(page_title="💊 Medicine Inventory Dashboard", layout="wide")
st.title("💊 Medicine Inventory & Sales Dashboard")

# Connect to DB
conn = get_connection()

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📈 Sales Report", "📦 Inventory", "⚠️ Expiry Alerts", "💰 Supplier Analytics"])

# ----------------------
# 📈 Tab 1 - Sales Report
# ----------------------
with tab1:
    st.subheader("Daily Sales Overview")
    query = """
        SELECT sale_date AS Date, SUM(quantity_sold) AS Total_Sold
        FROM sales
        GROUP BY sale_date
        ORDER BY sale_date DESC
    """
    df_sales = pd.read_sql(query, conn)
    if not df_sales.empty:
        st.line_chart(df_sales.set_index('Date'))

    st.subheader("Top-Selling Medicines")
    query = """
        SELECT m.name AS Medicine, SUM(s.quantity_sold) AS Total_Sold
        FROM sales s
        JOIN medicines m ON s.med_id = m.med_id
        GROUP BY s.med_id
        ORDER BY Total_Sold DESC
        LIMIT 5
    """
    df_top = pd.read_sql(query, conn)
    if not df_top.empty:
        st.bar_chart(df_top.set_index('Medicine'))

# -------------------------
# 📦 Tab 2 - Inventory
# -------------------------
with tab2:
    st.subheader("Full Inventory")
    df_inventory = pd.read_sql("""
        SELECT med_id, name, category, manufacturer, quantity, price, expiry_date
        FROM medicines
        ORDER BY name ASC
    """, conn)

    df_inventory['expiry_date'] = pd.to_datetime(df_inventory['expiry_date'])

    st.dataframe(df_inventory)

    st.subheader("Low Stock Medicines")
    low_stock = df_inventory[df_inventory['quantity'] < 20]
    st.warning(f"{len(low_stock)} medicine(s) with low stock")
    st.dataframe(low_stock)

# -------------------------
# ⚠️ Tab 3 - Expiry Alerts
# -------------------------
with tab3:
    st.subheader("Expiring Soon (Next 30 Days)")
    today = pd.Timestamp(datetime.today())
    upcoming = today + pd.Timedelta(days=30)

    df_expiring = df_inventory[df_inventory['expiry_date'] <= upcoming]
    st.dataframe(df_expiring)

    st.subheader("Already Expired")
    df_expired = df_inventory[df_inventory['expiry_date'] < today]
    st.dataframe(df_expired)

# -------------------------------
# 💰 Tab 4 - Supplier Analytics
# -------------------------------
with tab4:
    st.subheader("Supplier Cost Summary")
    query = """
        SELECT 
            s.name AS Supplier,
            ROUND(SUM(m.quantity * m.price), 2) AS Total_Cost
        FROM suppliers s
        JOIN medicine_supplier ms ON s.supplier_id = ms.supplier_id
        JOIN medicines m ON ms.med_id = m.med_id
        GROUP BY s.supplier_id
        ORDER BY Total_Cost DESC
    """
    df_suppliers = pd.read_sql(query, conn)
    st.dataframe(df_suppliers)

    if not df_suppliers.empty:
        st.bar_chart(df_suppliers.set_index("Supplier"))

# Close DB
conn.close()
