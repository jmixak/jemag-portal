import pandas as pd
import mysql.connector
import re

# Helper function to extract pure numbers from text like '120Ah' -> 120
def clean_int(val, default=120):
    if pd.isna(val):
        return default
    numbers = re.findall(r'\d+', str(val))
    if numbers:
        return int(numbers[0])
    return default

# Helper function to format dates to YYYY-MM-DD for MySQL
def clean_date(val, default="2026-01-01"):
    if pd.isna(val) or not str(val).strip():
        return default
    try:
        dt = pd.to_datetime(val, dayfirst=True)
        return dt.strftime('%Y-%m-%d')
    except:
        return default

# 1. Connect to Aiven MySQL Database
conn = mysql.connector.connect(
    host="mysql-1379a447-joshuajmix-8f13.g.aivencloud.com",
    port=22163,
    user="avnadmin",
    password="AVNS_tKAgtABtwEwNX6MZWfQ",  # <--- Put your Aiven password here!
    database="JemagRenewableEnergy"
)
cursor = conn.cursor()

# 2. Read the CSV exported from Google Sheets
df = pd.read_csv("past_battery_logs.csv")

print(f"📄 Found {len(df)} records in CSV file. Starting migration...")

success_count = 0

# 3. Loop through each row and clean data dynamically
for index, row in df.iterrows():
    # Clean capacity number (strips 'Ah' or spaces)
    capacity_ah = clean_int(row.get('Cell capacity (Ah)'), 120)

    # Clean dates to MySQL YYYY-MM-DD format
    prod_date = clean_date(row.get('Production Date'))
    req_date = clean_date(row.get('Battery Request Date'))

    query = """
    INSERT INTO BatteryLogs (
        BatterySerialNumber, BatchNumber, ProductionDate, ClientName, ContactDetails, 
        BatteryRequestDate, BatteryFinalLocation, CellCapacityAh, CellChemistry, 
        NumberOfCells, CellSupplier, CellMatching, BMSBrand, BMSModel, FirmwareVersion, 
        ChargeCutoffVoltage, DischargeCutoffVoltage, BalancingEnabled, CommunicationType, 
        CheckBusBars, CheckTempSensors, CheckInsulation, CheckCaseGrounded, CheckCableGauge, 
        CheckPolarity, CheckOther, IndCellVoltages, PackVoltageBefore, PackVoltageAfter, 
        InitialDischargeResult, LoadTestPassed, VisualInspectionPassed, ElectricalInspectionPassed, 
        QCApproval, QCOfficerName, Remarks
    ) VALUES (
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
    )
    """

    values = (
        str(row.get('Battery Serial Number', f'JMG-OLD-{index+1}')),
        str(row.get('Batch Number', 'Batch-001')),
        prod_date,
        str(row.get('Client Name', 'Unknown Client')),
        str(row.get('Contact Details', '')),
        req_date,
        str(row.get('Battery Final Location', 'Jos')),
        capacity_ah,
        str(row.get('Cell chemistry', 'LiFePO4')),
        str(row.get('Number of cells', '16S 1P')),
        str(row.get('Cell supplier', 'N/A')),
        str(row.get('Cell matching', 'Yes')),
        str(row.get('BMS brand', 'JK')),
        str(row.get('BMS model', 'N/A')),
        str(row.get('Firmware version', '')),
        str(row.get('Charge cutoff voltage', '52.6 V')),
        str(row.get('Discharge cutoff voltage', '52.6 V')),
        str(row.get('Balancing enabled', 'Yes')),
        str(row.get('Communication type', 'CAN')),
        True, True, True, True, True, True,
        str(row.get('Check Other', '')),
        str(row.get('Individual cell voltages', '3.2 V')),
        str(row.get('Pack voltage before charge', '52.6 V')),
        str(row.get('Pack voltage after full charge', '52.6 V')),
        str(row.get('Initial discharge test result', 'Pass')),
        str(row.get('Load test passed', 'Yes')),
        str(row.get('Visual inspection passed', 'Yes')),
        str(row.get('Electrical inspection passed', 'Yes')),
        str(row.get('QC approval', 'Pass')),
        str(row.get('QC officer name', 'Admin')),
        str(row.get('Remarks', 'Migrated from Google Sheets'))
    )

    try:
        cursor.execute(query, values)
        success_count += 1
    except mysql.connector.Error as err:
        print(f"⚠️ Row {index+1} skipped due to error: {err}")

conn.commit()
print(f"🎉 Migration complete! Successfully imported {success_count} out of {len(df)} records into your database.")

cursor.close()
conn.close()