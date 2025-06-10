import asyncio
import mysql.connector
import argparse
import sys
from datetime import datetime
import os
import json


async def insert_employee_sync(employee_id, employee_data):
    """Insert a single employee into the database using synchronous connection."""
    try:
        # Connect to MySQL
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="mandip",
            database="face_recognition"
        )

        cursor = conn.cursor()

        # Insert data into MySQL
        cursor.execute(
            """
            INSERT INTO employee (employee_id, name, major, starting_year, total_attendance, standing, year, last_attendance_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                employee_id,
                employee_data["name"],
                employee_data["major"],
                employee_data["starting_year"],
                employee_data["total_attendance"],
                employee_data["standing"],
                employee_data["year"],
                employee_data["last_attendance_time"]
            )
        )

        # Commit the changes
        conn.commit()
        print(f"Successfully inserted employee {employee_id}")

        # Close the connection
        cursor.close()
        conn.close()

        return True
    except Exception as e:
        print(f"Error inserting employee {employee_id}: {str(e)}")
        return False


async def insert_all_employees(employee_data):
    """Insert all employees into the database concurrently."""
    tasks = []
    for employee_id, data in employee_data.items():
        tasks.append(insert_employee_sync(employee_id, data))

    results = await asyncio.gather(*tasks)
    success_count = sum(1 for result in results if result)
    print(f"Successfully inserted {success_count} out of {len(employee_data)} employees")


def create_tables_if_not_exist():
    """Create the necessary database tables if they don't exist."""
    try:
        # Connect to MySQL
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="mandip",
            database="face_recognition"
        )

        cursor = conn.cursor()

        # Create employee table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS employee (
                id INT AUTO_INCREMENT PRIMARY KEY,
                employee_id VARCHAR(10) UNIQUE NOT NULL,
                name VARCHAR(100) NOT NULL,
                major VARCHAR(100),
                starting_year INT,
                total_attendance INT DEFAULT 0,
                standing CHAR(1) DEFAULT 'G',
                year INT,
                last_attendance_time DATETIME
            )
        """)

        # Commit the changes and close the connection
        conn.commit()
        cursor.close()
        conn.close()

        print("Database tables created/verified successfully")
        return True
    except Exception as e:
        print(f"Error creating database tables: {str(e)}")
        return False


def load_employee_data(json_file=None):
    """Load employee data from a JSON file or use default data."""
    if json_file and os.path.exists(json_file):
        try:
            with open(json_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading JSON file: {str(e)}")

    # Default data if no file is provided or there was an error loading the file
    return {
        "234567": {
            "name": "Mandip Chowdhury",
            "major": "Machine Learning",
            "starting_year": 2021,
            "total_attendance": 7,
            "standing": "G",
            "year": 4,
            "last_attendance_time": "2022-12-11 00:54:34"
        },
        "852741": {
            "name": "Emly Blunt",
            "major": "Economics",
            "starting_year": 2021,
            "total_attendance": 12,
            "standing": "B",
            "year": 1,
            "last_attendance_time": "2022-12-11 00:54:34"
        },
        "963852": {
            "name": "Elon Musk",
            "major": "Physics",
            "starting_year": 2020,
            "total_attendance": 7,
            "standing": "G",
            "year": 2,
            "last_attendance_time": "2022-12-11 00:54:34"
        },
        "321654": {
            "name": "Jane Smith",
            "major": "Computer Science",
            "starting_year": 2022,
            "total_attendance": 5,
            "standing": "G",
            "year": 3,
            "last_attendance_time": "2022-12-11 00:54:34"
        }
    }


async def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Add employee data to the database")
    parser.add_argument('--json', help='Path to a JSON file containing employee data')
    args = parser.parse_args()

    # Create tables if they don't exist
    if not create_tables_if_not_exist():
        sys.exit(1)

    # Load employee data
    data = load_employee_data(args.json)

    # Insert all employees into the database
    await insert_all_employees(data)

    print("Data insertion process completed!")


if __name__ == "__main__":
    asyncio.run(main())
