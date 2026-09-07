from database import get_db_connection


try:
    db = get_db_connection()

    print("Database connection successful!")

    cursor = db.cursor()
    cursor.execute("SELECT DATABASE()")

    result = cursor.fetchone()

    print("Current database:", result[0])

    cursor.close()
    db.close()

except Exception as e:
    print("Database connection failed!")
    print("Error:", e)