# init_db.py

from db_config import get_connection

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    # Create medicines table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS medicines (
            med_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100),
            category VARCHAR(100),
            quantity INT,
            price DECIMAL(10,2),
            expiry_date DATE,
            manufacturer VARCHAR(100)
        )
    """)

    # Create suppliers table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS suppliers (
            supplier_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100),
            contact_info VARCHAR(100)
        )
    """)

    # Create medicine_supplier table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS medicine_supplier (
            med_id INT,
            supplier_id INT,
            FOREIGN KEY (med_id) REFERENCES medicines(med_id),
            FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
        )
    """)

    # Create sales table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            sale_id INT AUTO_INCREMENT PRIMARY KEY,
            med_id INT,
            quantity_sold INT,
            sale_date DATE,
            FOREIGN KEY (med_id) REFERENCES medicines(med_id)
        )
    """)

    conn.commit()
    print("✅ All tables created successfully.")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    create_tables()
