import mysql.connector

# Input your database details directly
conn = mysql.connector.connect(
    host="mysql-1379a447-joshuajmix-8f13.g.aivencloud.com",       # e.g., "127.0.0.1" or database host domain
    port=22163,
    user="avnadmin",       # e.g., "root"
    password="YOUR_PASSWORD",
    database="defaultdb"
)

cursor = conn.cursor()

create_table_query = """
CREATE TABLE IF NOT EXISTS TravelLogs (
    TravelID INT AUTO_INCREMENT PRIMARY KEY,
    StaffName VARCHAR(100) NOT NULL,
    State VARCHAR(50) NOT NULL,
    DestinationCity VARCHAR(100) NOT NULL,
    SpecificLocation VARCHAR(255),
    DepartureDate DATE NOT NULL,
    ExpectedReturnDate DATE NOT NULL,
    Purpose VARCHAR(150) NOT NULL,
    TravelStatus VARCHAR(50) DEFAULT 'On Trip',
    Latitude DECIMAL(10, 6),
    Longitude DECIMAL(10, 6),
    LogDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

cursor.execute(create_table_query)
conn.commit()
print("✅ TravelLogs table created successfully in MySQL!")

cursor.close()
conn.close()