# insert_sample_data.py

from db_config import get_connection
from datetime import date

def insert_sample_data():
    conn = get_connection()
    cursor = conn.cursor()

    # Insert medicines
    medicines = [
        ("Paracetamol", "Painkiller", 100, 1.50, "2026-01-01", "Cipla"),
        ("Cetirizine", "Antihistamine", 200, 0.75, "2025-11-15", "Sun Pharma"),
        ("Amoxicillin", "Antibiotic", 150, 2.00, "2025-08-10", "Alkem"),
        ("Aspirin", "Painkiller", 120, 1.25, "2025-12-01", "Pfizer"),
        ("Ibuprofen", "Anti-inflammatory", 130, 1.80, "2025-10-01", "Zydus")
    ]

    cursor.executemany("""
        INSERT INTO medicines (name, category, quantity, price, expiry_date, manufacturer)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, medicines)

    # Insert suppliers
    # suppliers = [
    #     ("MedSupply Co.", "medsupply@example.com"),
    #     ("PharmaDist Ltd.", "pharmadist@example.com")
    # ]

    # cursor.executemany("""
    #     INSERT INTO suppliers (name, contact_info)
    #     VALUES (%s, %s)
    # """, suppliers)

    # Link medicines to suppliers
    # medicine_supplier_links = [
    #     (1, 1),
    #     (2, 1),
    #     (3, 2),
    #     (4, 2),
    #     (5, 1)
    # ]

    # cursor.executemany("""
    #     INSERT INTO medicine_supplier (med_id, supplier_id)
    #     VALUES (%s, %s)
    # """, medicine_supplier_links)

    # Insert sales
    sales = [
        (1, 10, date(2025, 7, 1)),
        (2, 5, date(2025, 7, 2)),
        (1, 7, date(2025, 7, 3)),
        (3, 3, date(2025, 7, 3)),
        (4, 8, date(2025, 7, 4))
    ]

    cursor.executemany("""
        INSERT INTO sales (med_id, quantity_sold, sale_date)
        VALUES (%s, %s, %s)
    """, sales)

    conn.commit()
    print("✅ Sample data inserted successfully.")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    insert_sample_data()
