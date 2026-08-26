import mysql.connector

# Connect directly to your Jemag database on Aiven
conn = mysql.connector.connect(
    host="mysql-1379a447-joshuajmix-8f13.g.aivencloud.com",
    port=22163,
    user="avnadmin",
    password="YOUR_PASSWORD",  # <--- Put your actual Aiven password here!
    database="JemagRenewableEnergy"       
)

cursor = conn.cursor()

# 1. Drop the old basic table
cursor.execute("DROP TABLE IF EXISTS BatteryLogs;")

# 2. Build the massive new Custom Table matching all your Google Form fields
cursor.execute("""
CREATE TABLE BatteryLogs (
    LogID INT AUTO_INCREMENT PRIMARY KEY,
    -- Group 1: Battery & Client Info
    BatterySerialNumber VARCHAR(100) UNIQUE NOT NULL,
    BatchNumber VARCHAR(50),
    ProductionDate DATE,
    ClientName VARCHAR(100),
    ContactDetails VARCHAR(100),
    BatteryRequestDate DATE,
    BatteryFinalLocation VARCHAR(255),
    
    -- Group 2: Cell Information
    CellCapacityAh INT,
    CellChemistry VARCHAR(100),
    NumberOfCells VARCHAR(100),
    CellSupplier VARCHAR(100),
    CellMatching VARCHAR(20),
    
    -- Group 3: BMS Configuration
    BMSBrand VARCHAR(100),
    BMSModel VARCHAR(100),
    FirmwareVersion VARCHAR(100),
    ChargeCutoffVoltage VARCHAR(50),
    DischargeCutoffVoltage VARCHAR(50),
    BalancingEnabled VARCHAR(20),
    CommunicationType VARCHAR(100),
    
    -- Group 4: Assembly Checklist
    CheckBusBars BOOLEAN,
    CheckTempSensors BOOLEAN,
    CheckInsulation BOOLEAN,
    CheckCaseGrounded BOOLEAN,
    CheckCableGauge BOOLEAN,
    CheckPolarity BOOLEAN,
    CheckOther VARCHAR(255),
    
    -- Group 5: Electrical Test Results
    IndCellVoltages VARCHAR(100),
    PackVoltageBefore VARCHAR(50),
    PackVoltageAfter VARCHAR(50),
    InitialDischargeResult VARCHAR(255),
    LoadTestPassed VARCHAR(20),
    
    -- Group 6: QC & Approval
    VisualInspectionPassed VARCHAR(20),
    ElectricalInspectionPassed VARCHAR(20),
    QCApproval VARCHAR(50),
    QCOfficerName VARCHAR(100),
    Remarks TEXT,
    
    LogDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

print("🔋 Success! Comprehensive BatteryLogs table created in the cloud!")

cursor.close()
conn.close()