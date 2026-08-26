import mysql.connector

# Connect to Aiven MySQL Database
conn = mysql.connector.connect(
    host="mysql-1379a447-joshuajmix-8f13.g.aivencloud.com",
    port=22163,
    user="avnadmin",
    password="YOUR_PASSWORD",  # <--- Replace with your Aiven password!
    database="JemagRenewableEnergy"
)
cursor = conn.cursor()

# 1. Create Installations Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS Installations (
    InstallationID INT AUTO_INCREMENT PRIMARY KEY,
    ClientName VARCHAR(255) NOT NULL,
    PhoneNumber VARCHAR(50),
    CityTown VARCHAR(100),
    FullAddress TEXT,
    Latitude DECIMAL(10, 8),
    Longitude DECIMAL(11, 8),
    GoogleMapsLink TEXT,
    SystemCapacityKW DECIMAL(10, 2),
    BatteryCapacityKWh DECIMAL(10, 2),
    InverterBrandModel VARCHAR(255),
    BatterySerialNumber VARCHAR(255),
    InstallerName VARCHAR(255),
    InstallationDate DATE,
    CurrentStatus VARCHAR(50) DEFAULT 'Operational',
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

# 2. Create MaintenanceLogs Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS MaintenanceLogs (
    MaintenanceID INT AUTO_INCREMENT PRIMARY KEY,
    InstallationID INT,
    BatterySerialNumber VARCHAR(255),
    ClientName VARCHAR(255),
    PhoneNumber VARCHAR(50),
    CityTown VARCHAR(100),
    FullAddress TEXT,
    GoogleMapsLink TEXT,
    SystemCapacityKW DECIMAL(10, 2),
    BatteryCapacityKWh DECIMAL(10, 2),
    InverterBrandModel VARCHAR(255),
    PurposeOfVisit VARCHAR(255),
    CurrentStatus VARCHAR(50),
    IssuesObserved TEXT,
    ActionTaken TEXT,
    TechnicianName VARCHAR(255),
    VisitDate DATE,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (InstallationID) REFERENCES Installations(InstallationID) ON DELETE SET NULL
);
""")

conn.commit()
print("✅ Installations and MaintenanceLogs tables created successfully!")

cursor.close()
conn.close()