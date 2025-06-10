import mysql.connector

class Database:
    def __init__(self, host='localhost', user='root', passwd='mandip', database='face_recognition'):
        self.conn = mysql.connector.connect(host=host, user=user, passwd=passwd, database=database)
        self.cursor = self.conn.cursor(dictionary=True)

    def get_employee_info(self, employee_id):
        query = "SELECT * FROM employee WHERE employee_id = %s"
        self.cursor.execute(query, (employee_id,))
        return self.cursor.fetchone()

    def update_employee_attendance(self, employee_id, new_attendance):
        query = "UPDATE employee SET total_attendance = %s WHERE employee_id = %s"
        self.cursor.execute(query, (new_attendance, employee_id))
        self.conn.commit()
        print(f"Employee {employee_id}'s attendance updated to {new_attendance}")

    def update_employee_last_attendance_time(self, employee_id, last_new_attendance_time):
        query = "UPDATE employee SET last_attendance_time = %s WHERE employee_id = %s"
        self.cursor.execute(query, (last_new_attendance_time, employee_id))
        self.conn.commit()
        print(f"Employee {employee_id}'s last attendance time updated to {last_new_attendance_time}")

    def close(self):
        self.cursor.close()
        self.conn.close()