# analytics_db.py

from db_config import get_connection
import pandas as pd
from datetime import datetime, timedelta
import csv

def top_selling_medicines():
    conn = get_connection()
    query = """
        SELECT m.name AS Medicine, SUM(s.quantity_sold) AS Total_Sold
        FROM sales s
        JOIN medicines m ON s.med_id = m.med_id
        GROUP BY s.med_id
        ORDER BY Total_Sold DESC
        LIMIT 5
    """
    df = pd.read_sql(query, conn)
    df.to_csv("top_selling_medicines.csv", index=False)
    print("\n Top-Selling Medicines:")
    print(df.to_string(index=False))
    conn.close()

def low_stock_medicines(threshold=20):
    conn = get_connection()
    query = """
        SELECT name AS Medicine, quantity AS Stock
        FROM medicines
        WHERE quantity < %s
        ORDER BY quantity ASC
    """
    df = pd.read_sql(query, conn, params=(threshold,))
    df.to_csv("low_stock_medicines.csv", index=False)
    print(f"\n Low Stock Medicines (less than {threshold} units):")
    print(df.to_string(index=False))
    conn.close()

def expiring_soon(days=30):
    conn = get_connection()
    future_date = (datetime.today() + timedelta(days=days)).strftime('%Y-%m-%d')
    query = """
        SELECT name AS Medicine, expiry_date
        FROM medicines
        WHERE expiry_date <= %s
        ORDER BY expiry_date ASC
    """
    df = pd.read_sql(query, conn, params=(future_date,))
    df.to_csv("medicines_expiring_soon.csv", index=False)
    print(f"\n Medicines Expiring Within {days} Days:")
    print(df.to_string(index=False))
    conn.close()

def daily_sales_report():
    conn = get_connection()
    query = """
        SELECT sale_date AS Date, SUM(quantity_sold) AS Total_Sold
        FROM sales
        GROUP BY sale_date
        ORDER BY sale_date DESC
    """
    df = pd.read_sql(query, conn)
    df.to_csv("daily_sales_report.csv", index=False)
    print("\n Daily Sales Report:")
    print(df.to_string(index=False))
    conn.close()

def supplier_supply_log():
    conn = get_connection()
    query = """
        SELECT 
            s.name AS Supplier,
            m.name AS Medicine,
            m.added_on AS Supplied_On,
            m.quantity AS Quantity
        FROM suppliers s
        JOIN medicine_supplier ms ON s.supplier_id = ms.supplier_id
        JOIN medicines m ON ms.med_id = m.med_id
        ORDER BY s.name ASC, m.added_on DESC
    """
    df = pd.read_sql(query, conn)
    df.to_csv("supplier_supply_log.csv", index=False)
    print("\n===  Supplier Supply Log ===")
    print(df.to_string(index=False))
    conn.close()

def supplier_cost_summary():
    conn = get_connection()
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
    df = pd.read_sql(query, conn)
    df.to_csv("supplier_cost_summary.csv", index=False)
    print("\n===  Supplier Total Cost Summary ===")
    print(df.to_string(index=False))
    conn.close()

def export_inventory_to_csv():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT med_id, name, category, manufacturer, quantity, price, expiry_date
        FROM medicines
        ORDER BY name ASC, expiry_date ASC
    """)
    results = cursor.fetchall()
    today = datetime.today().date()
    near_expiry = today + timedelta(days=30)

    if results:
        filename = "medicine_inventory_report.csv"
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['med_id', 'name', 'category', 'manufacturer', 'quantity', 'price', 'expiry_date', 'status'])

            for med_id, name, category, manufacturer, qty, price, expiry in results:
                if expiry < today:
                    status = 'EXPIRED'
                elif today <= expiry <= near_expiry:
                    status = 'NEAR EXPIRY'
                else:
                    status = 'OK'

                writer.writerow([med_id, name, category, manufacturer, qty, f"{price:.2f}", expiry, status])

        print(f" Inventory CSV report generated: {filename}")
    else:
        print(" No medicines found in inventory.")

    cursor.close()
    conn.close()

def export_sales_to_csv():
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT 
            s.sale_id,
            m.name AS medicine_name,
            m.manufacturer,
            s.quantity_sold,
            s.sale_date
        FROM sales s
        JOIN medicines m ON s.med_id = m.med_id
        ORDER BY s.sale_date DESC
    """

    cursor.execute(query)
    results = cursor.fetchall()

    if results:
        filename = "sales_report.csv"
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['sale_id', 'medicine_name', 'manufacturer', 'quantity_sold', 'sale_date'])

            for row in results:
                writer.writerow(row)

        print(f" Sales report exported successfully to '{filename}'")
    else:
        print(" No sales records found.")

    cursor.close()
    conn.close()

def show_menu():
    while True:
        print("\n=== Analytics Dashboard ===")
        print("1. Top-Selling Medicines")
        print("2. Low Stock Alert")
        print("3. Expiring Soon")
        print("4. Daily Sales Report")
        print("5. Supplier Supply Log")
        print("6. Supplier Cost Summary")
        print("7. Export Inventory to CSV")
        print("8. Export Sales to CSV")
        print("9. Exit")

        choice = input("Enter your choice (1-9): ")
        if choice == '1':
            top_selling_medicines()
        elif choice == '2':
            low_stock_medicines()
        elif choice == '3':
            expiring_soon()
        elif choice == '4':
            daily_sales_report()
        elif choice == '5':
            supplier_supply_log()
        elif choice == '6':
            supplier_cost_summary()
        elif choice == '7':
            export_inventory_to_csv()
        elif choice == '8':
            export_sales_to_csv()
        elif choice == '9':
            print(" Exiting Analytics.")
            break
        else:
            print(" Invalid choice. Try again.")

if __name__ == "__main__":
    show_menu()
