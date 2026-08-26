import mysql.connector

# Connect directly to your Aiven MySQL database
conn = mysql.connector.connect(
    host="mysql-1379a447-joshuajmix-8f13.g.aivencloud.com",
    port=22163,
    user="avnadmin",
    password="YOUR_PASSWORD",  # <--- Put your actual Aiven password here!
    database="defaultdb"
)

cursor = conn.cursor()

# 1. Create Jemag Database
cursor.execute("CREATE DATABASE IF NOT EXISTS JemagRenewableEnergy;")
cursor.execute("USE JemagRenewableEnergy;")

# 2. Build Tables
cursor.execute("""
CREATE TABLE IF NOT EXISTS People (
    PersonID INT AUTO_INCREMENT PRIMARY KEY,
    FirstName VARCHAR(50) NOT NULL,
    LastName VARCHAR(50) NOT NULL,
    Email VARCHAR(100) UNIQUE NOT NULL,
    RegularPhone VARCHAR(20),
    WhatsappPhone VARCHAR(20),
    RoleType ENUM('Staff', 'IT Student') NOT NULL,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS StaffDetails (
    StaffID INT AUTO_INCREMENT PRIMARY KEY,
    PersonID INT UNIQUE NOT NULL,
    JobTitle VARCHAR(100) NOT NULL,
    Department VARCHAR(100) DEFAULT 'Renewable Energy',
    FOREIGN KEY (PersonID) REFERENCES People(PersonID) ON DELETE CASCADE
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS ITStudentDetails (
    StudentID INT AUTO_INCREMENT PRIMARY KEY,
    PersonID INT UNIQUE NOT NULL,
    InstitutionName VARCHAR(100) NOT NULL,
    TrainingFocus VARCHAR(100) NOT NULL,
    SupervisorID INT,
    FOREIGN KEY (PersonID) REFERENCES People(PersonID) ON DELETE CASCADE,
    FOREIGN KEY (SupervisorID) REFERENCES StaffDetails(StaffID) ON DELETE SET NULL
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS StudentEvaluations (
    EvaluationID INT AUTO_INCREMENT PRIMARY KEY,
    StudentID INT NOT NULL,
    EvaluationType VARCHAR(50) NOT NULL,
    PerformanceScore DECIMAL(5,2) CHECK (PerformanceScore BETWEEN 0 AND 100),
    Comments TEXT,
    EvaluatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (StudentID) REFERENCES ITStudentDetails(StudentID) ON DELETE CASCADE
);
""")

# 3. Build Directory View
cursor.execute("DROP VIEW IF EXISTS View_JemagDirectory;")
cursor.execute("""
CREATE VIEW View_JemagDirectory AS
SELECT 
    p.PersonID,
    CONCAT(p.FirstName, ' ', p.LastName) AS FullName,
    p.Email,
    p.RegularPhone AS Regular_No,
    p.WhatsappPhone AS WhatsApp_No,
    p.RoleType,
    sd.JobTitle AS Staff_Role,
    its.InstitutionName AS Student_School,
    its.TrainingFocus AS Student_Focus,
    CONCAT(sp.FirstName, ' ', sp.LastName) AS Assigned_Supervisor
FROM People p
LEFT JOIN StaffDetails sd ON p.PersonID = sd.PersonID
LEFT JOIN ITStudentDetails its ON p.PersonID = its.PersonID
LEFT JOIN StaffDetails sup_sd ON its.SupervisorID = sup_sd.StaffID
LEFT JOIN People sp ON sup_sd.PersonID = sp.PersonID;
""")

print("🚀 Success! All Jemag tables and views have been created in the cloud!")

cursor.close()
conn.close()