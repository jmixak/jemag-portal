import mysql.connector

# Connect directly to your Jemag database on Aiven
conn = mysql.connector.connect(
    host="mysql-1379a447-joshuajmix-8f13.g.aivencloud.com",
    port=22163,
    user="avnadmin",
    password="AVNS_tKAgtABtwEwNX6MZWfQ",  # <--- Put your actual Aiven password here!
    database="JemagRenewableEnergy"       # Notice we are connecting directly to your database this time
)

cursor = conn.cursor()

# Build the BatteryLogs Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS BatteryLogs (
    LogID INT AUTO_INCREMENT PRIMARY KEY,
    SerialNumber VARCHAR(50) UNIQUE NOT NULL,
    BatteryModel VARCHAR(100) NOT NULL,
    Voltage INT NOT NULL,
    CapacityAh INT NOT NULL,
    AssembledBy VARCHAR(100) NOT NULL,
    QC_Status ENUM('Passed', 'Failed', 'Pending') DEFAULT 'Pending',
    ProductionNotes TEXT,
    LogDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

print("🔋 Success! BatteryLogs table created in the cloud!")

cursor.close()
conn.close()