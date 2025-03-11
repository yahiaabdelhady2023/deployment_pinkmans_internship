import sqlite3

conn = sqlite3.connect('pinkmans_database.db')
cursor = conn.cursor()

# Create a function to set up tables
def create_tables():
    # Create a table for User
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS User (
        userid INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) UNIQUE,
        forename VARCHAR(50),
        email VARCHAR(100) UNIQUE,
        password_hashed VARCHAR(255),
        roleid_fk INT,
        FOREIGN KEY (roleid_fk) REFERENCES role(roleid)
        )
    ''')

    # Create a table for Role
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Role (
        roleid INT AUTO_INCREMENT PRIMARY KEY, 
        rolename VARCHAR(50)
        )
    ''')

    # Create a table for Report
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Report (
            reportid INT AUTO_INCREMENT PRIMARY KEY,
            typeid_fk INT,
            file_name VARCHAR(1000),
            start_date DATE,
            end_date DATE,
            FOREIGN KEY (roleid_fk) REFERENCES ReportType(roleid)

        )
    ''')


        # Create a table for ReportType
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ReportType (
            typeid INT AUTO_INCREMENT PRIMARY KEY,
            report_type_name VARCHAR(500)
        )
    ''')

    # Commit the changes and close the connection
    conn.commit()

# Call the function to create tables
create_tables()

# Close the connection when done
conn.close()
