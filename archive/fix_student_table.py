import mysql.connector

# Connect to Aiven MySQL Database
conn = mysql.connector.connect(
    host="mysql-1379a447-joshuajmix-8f13.g.aivencloud.com",
    port=22163,
    user="avnadmin",
    password="YOUR_PASSWORD",  # <--- Put your Aiven password here!
    database="JemagRenewableEnergy"
)
cursor = conn.cursor()

# Drop child table first if foreign keys exist
cursor.execute("DROP TABLE IF EXISTS StudentEvaluations;")
cursor.execute("DROP TABLE IF EXISTS ITStudents;")

# Recreate ITStudents with all column variations expected by app1.py
cursor.execute("""
CREATE TABLE ITStudents (
    StudentID INT AUTO_INCREMENT PRIMARY KEY,
    PersonID INT,
    School VARCHAR(255),
    Student_School VARCHAR(255),
    Supervisor VARCHAR(255),
    AssignedSupervisor VARCHAR(255),
    FocusArea VARCHAR(255),
    Focus_Area VARCHAR(255),
    FOREIGN KEY (PersonID) REFERENCES People(PersonID) ON DELETE CASCADE
);
""")

# Recreate StudentEvaluations linked to the new ITStudents table
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
print("✅ Table ITStudents updated with 'AssignedSupervisor' column!")

cursor.close()
conn.close()