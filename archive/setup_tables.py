import mysql.connector

# Connect to Aiven MySQL Database
conn = mysql.connector.connect(
    host="mysql-1379a447-joshuajmix-8f13.g.aivencloud.com",
    port=22163,
    user="avnadmin",
    password="AVNS_tKAgtABtwEwNX6MZWfQ",  # <--- Put your Aiven password here!
    database="JemagRenewableEnergy"
)
cursor = conn.cursor()

# 1. Create People Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS People (
    PersonID INT AUTO_INCREMENT PRIMARY KEY,
    FullName VARCHAR(255) NOT NULL,
    Email VARCHAR(255) UNIQUE,
    Regular_No VARCHAR(50),
    WhatsApp_No VARCHAR(50),
    RoleType VARCHAR(50) NOT NULL,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

# 2. Create Staff Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS Staff (
    StaffID INT AUTO_INCREMENT PRIMARY KEY,
    PersonID INT,
    StaffRole VARCHAR(100),
    FOREIGN KEY (PersonID) REFERENCES People(PersonID) ON DELETE CASCADE
);
""")

# 3. Create ITStudents Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS ITStudents (
    StudentID INT AUTO_INCREMENT PRIMARY KEY,
    PersonID INT,
    School VARCHAR(255),
    Supervisor VARCHAR(255),
    FocusArea VARCHAR(255),
    FOREIGN KEY (PersonID) REFERENCES People(PersonID) ON DELETE CASCADE
);
""")

# 4. Create StudentEvaluations Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS StudentEvaluations (
    EvaluationID INT AUTO_INCREMENT PRIMARY KEY,
    StudentID INT,
    Punctuality INT,
    TechnicalSkill INT,
    WorkEthic INT,
    Teamwork INT,
    Remarks TEXT,
    EvaluationDate DATE,
    FOREIGN KEY (StudentID) REFERENCES ITStudents(StudentID) ON DELETE CASCADE
);
""")

conn.commit()
print("✅ All missing database tables (People, Staff, ITStudents, StudentEvaluations) have been created successfully!")

cursor.close()
conn.close()