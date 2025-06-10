import aiomysql
from datetime import datetime


class AsyncDatabase:
    def __init__(self, host='localhost', user='root', passwd='mandip', database='face_recognition'):
        self.host = host
        self.user = user
        self.passwd = passwd
        self.database = database
        self.pool = None

    async def init_pool(self):
        try:
            self.pool = await aiomysql.create_pool(
                host=self.host,
                user=self.user,
                password=self.passwd,
                db=self.database
            )
            return True
        except Exception as e:
            print(f"Database connection error: {str(e)}")
            return False

    async def get_employee_info(self, employee_id):
        if not self.pool:
            return None

        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                query = "SELECT * FROM employee WHERE employee_id = %s"
                await cursor.execute(query, (employee_id,))
                result = await cursor.fetchone()
                return result

    async def update_employee_attendance(self, employee_id, new_attendance):
        if not self.pool:
            return False

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                query = "UPDATE employee SET total_attendance = %s WHERE employee_id = %s"
                await cursor.execute(query, (new_attendance, employee_id))
                await conn.commit()
                return True

    async def update_employee_last_attendance_time(self, employee_id, last_new_attendance_time):
        if not self.pool:
            return False

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                query = "UPDATE employee SET last_attendance_time = %s WHERE employee_id = %s"
                await cursor.execute(query, (last_new_attendance_time, employee_id))
                await conn.commit()
                return True

    async def close(self):
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()