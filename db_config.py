# db_config.py
import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Shriradhe03#",     # 🔁 Replace with your MySQL password
        database="medicine_inventory" # This DB will be created in the next step
    )
