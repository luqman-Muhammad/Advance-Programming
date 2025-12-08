import pyodbc

CONN_STR = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost;"  # Double backslash for named instance
    "DATABASE=CourierDB;"
    "Trusted_Connection=yes;"
)

try:
    conn = pyodbc.connect(CONN_STR)
    print("✅ Connected to CourierDB!")

    cursor = conn.cursor()
    cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
    print("📦 Tables in CourierDB:")
    for row in cursor.fetchall():
        print(" -", row.TABLE_NAME)

    conn.close()

except Exception as e:
    print("❌ Failed to connect:")
    print(e)