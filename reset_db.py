from db_config import get_connection

def reset_all_tables():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Disable foreign key checks to prevent errors while truncating
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

        # Truncate all data
        cursor.execute("TRUNCATE TABLE sales")
        cursor.execute("TRUNCATE TABLE medicines")

        # Re-enable foreign key checks
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

        conn.commit()
        print("All table records deleted successfully. Database reset.")

    except Exception as e:
        print("Error resetting the database:", str(e))
        conn.rollback()

    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    confirm = input("Are you sure you want to delete all records? Type 'yes' to continue: ")
    if confirm.lower() == "yes":
        reset_all_tables()
    else:
        print("Operation cancelled.")
