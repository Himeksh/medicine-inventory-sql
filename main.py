from db_config import get_connection
from datetime import datetime, timedelta

def show_menu():
    print("\n=== Medicine Inventory & Sales Management ===")
    print("1. View All Medicines")
    print("2. Add New Medicine")
    print("3. Update Medicine Quantity")
    print("4. Record a Sale")
    print("5. View Sales Report")
    print("6. Exit")

def view_medicines():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT med_id, name, category, manufacturer, quantity, price, expiry_date
        FROM medicines
        ORDER BY name ASC, expiry_date ASC
    """)

    results = cursor.fetchall()
    today = datetime.today().date()
    near_expiry_limit = today + timedelta(days=30)

    if results:
        print("\n=== 📦 Medicine Inventory (Batch-wise) ===")
        print(f"{'ID':<5} {'Name':<20} {'Category':<15} {'Manufacturer':<15} {'Qty':<6} {'Price':<8} {'Expiry':<12} {'Status'}")
        print("-" * 100)
        for med_id, name, category, manufacturer, qty, price, expiry in results:
            if expiry < today:
                status = "EXPIRED"
            elif today <= expiry <= near_expiry_limit:
                status = "Near Expiry"
            else:
                status = "OK"

            print(f"{med_id:<5} {name:<20} {category:<15} {manufacturer:<15} {qty:<6} ₹{price:<7.2f} {expiry}  {status}")
    else:
        print("No medicines found in the inventory.")

    cursor.close()
    conn.close()

def get_or_create_supplier(conn, supplier_name):
    cursor = conn.cursor()
    cursor.execute("SELECT supplier_id FROM suppliers WHERE name = %s", (supplier_name,))
    result = cursor.fetchone()

    if result:
        print(f"ℹ Supplier '{supplier_name}' already exists (ID: {result[0]}).")
        return result[0]
    else:
        cursor.execute("INSERT INTO suppliers (name) VALUES (%s)", (supplier_name,))
        conn.commit()
        new_id = cursor.lastrowid
        print(f"New supplier '{supplier_name}' added with ID: {new_id}.")
        return new_id

def add_medicine():
    name = input("Medicine Name: ")
    category = input("Category: ")
    quantity = int(input("Quantity: "))
    price = float(input("Price: "))
    expiry = input("Expiry Date (YYYY-MM-DD): ")
    manufacturer = input("Manufacturer: ")
    supplier_name = input("Supplier Name: ")

    conn = get_connection()
    cursor = conn.cursor()

    supplier_id = get_or_create_supplier(conn, supplier_name)

    cursor.execute("""
        SELECT med_id, quantity FROM medicines 
        WHERE name = %s AND category = %s AND price = %s 
        AND expiry_date = %s AND manufacturer = %s
    """, (name, category, price, expiry, manufacturer))
    existing = cursor.fetchone()

    if existing:
        med_id, current_qty = existing
        print(f"Medicine batch exists. Updating quantity.")
        cursor.execute("UPDATE medicines SET quantity = quantity + %s WHERE med_id = %s", (quantity, med_id))
        conn.commit()
    else:
        cursor.execute("""
            INSERT INTO medicines (name, category, quantity, price, expiry_date, manufacturer)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (name, category, quantity, price, expiry, manufacturer))
        conn.commit()
        med_id = cursor.lastrowid
        print("New medicine batch added.")

    cursor.execute("""
        SELECT 1 FROM medicine_suppliers WHERE med_id = %s AND supplier_id = %s
    """, (med_id, supplier_id))
    link_exists = cursor.fetchone()

    if not link_exists:
        cursor.execute("""
            INSERT INTO medicine_suppliers (med_id, supplier_id)
            VALUES (%s, %s)
        """, (med_id, supplier_id))
        conn.commit()
        print("Supplier linked to medicine.")
    else:
        print("Supplier already linked to this medicine.")

    cursor.close()
    conn.close()

def update_quantity():
    med_id = int(input("Enter Medicine ID: "))
    qty = int(input("Enter Quantity to Add/Subtract (e.g. -5): "))

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE medicines SET quantity = quantity + %s WHERE med_id = %s", (qty, med_id))
    conn.commit()
    print("Quantity updated.")
    cursor.close()
    conn.close()

def record_sale():
    try:
        med_name = input("Enter Medicine Name: ").strip()
        qty = int(input("Quantity Sold: "))
        sale_date_input = input("Sale Date (YYYY-MM-DD, leave blank for today): ").strip()
        sale_date = sale_date_input if sale_date_input else datetime.today().strftime('%Y-%m-%d')

        conn = get_connection()
        cursor = conn.cursor(buffered=True)

        cursor.execute("""
            SELECT med_id, quantity, expiry_date 
            FROM medicines 
            WHERE name = %s AND quantity > 0
            ORDER BY expiry_date ASC
        """, (med_name,))
        batches = cursor.fetchall()

        if not batches:
            print(f"No stock found for '{med_name}'.")
        else:
            qty_needed = qty
            for med_id, available_qty, expiry_date in batches:
                if expiry_date < datetime.today().date():
                    continue

                to_deduct = min(qty_needed, available_qty)

                cursor.execute("""
                    INSERT INTO sales (med_id, quantity_sold, sale_date)
                    VALUES (%s, %s, %s)
                """, (med_id, to_deduct, sale_date))

                cursor.execute("""
                    UPDATE medicines SET quantity = quantity - %s WHERE med_id = %s
                """, (to_deduct, med_id))

                qty_needed -= to_deduct

                if qty_needed == 0:
                    break

            if qty_needed > 0:
                print(f"Only partial stock available. Sold {qty - qty_needed} units out of {qty}.")
            else:
                print(f"Sale recorded: {qty} units of '{med_name}' sold on {sale_date}.")

            conn.commit()

        cursor.close()
        conn.close()

    except ValueError:
        print("Invalid input. Please enter numeric values for quantity.")

def view_sales():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.sale_id, m.name, s.quantity_sold, s.sale_date
        FROM sales s
        JOIN medicines m ON s.med_id = m.med_id
        ORDER BY s.sale_date DESC
    """)
    rows = cursor.fetchall()
    print("\n--- Sales Report ---")
    for row in rows:
        print(f"Sale ID: {row[0]} | Medicine: {row[1]} | Qty Sold: {row[2]} | Date: {row[3]}")
    cursor.close()
    conn.close()

# Main CLI loop
while True:
    show_menu()
    choice = input("Enter your choice (1-6): ")

    if choice == '1':
        view_medicines()
    elif choice == '2':
        add_medicine()
    elif choice == '3':
        update_quantity()
    elif choice == '4':
        record_sale()
    elif choice == '5':
        view_sales()
    elif choice == '6':
        print("Exiting program. Goodbye!")
        break
    else:
        print("Invalid choice. Try again.")
