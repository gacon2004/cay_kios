from fastapi import HTTPException, status
import os
import pymysql.cursors
from pymysql import converters, FIELD_TYPE


class DatabaseConnector:
    def __init__(self):
        self.host = os.getenv("DATABASE_HOST")
        self.user = os.getenv("DATABASE_USERNAME")
        self.password = os.getenv("DATABASE_PASSWORD")
        self.database = os.getenv("DATABASE")
        self.port = int(os.getenv("DATABASE_PORT", "3306"))

        # Convert BIT -> bool
        self.conversions = converters.conversions.copy()
        self.conversions[FIELD_TYPE.BIT] = (
            lambda x: False if x == b"\x00" else True
        )

        # Validate env
        for key, value in {
            "DATABASE_HOST": self.host,
            "DATABASE_USERNAME": self.user,
            "DATABASE_PASSWORD": self.password,
            "DATABASE": self.database,
        }.items():
            if not value:
                raise EnvironmentError(f"{key} environment variable not found")

    def get_connection(self):
        """Tạo connection MySQL và set timezone"""
        try:
            connection = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                cursorclass=pymysql.cursors.DictCursor,
                conv=self.conversions,
            )
            with connection.cursor() as cursor:
                cursor.execute("SET time_zone = '+07:00';")
            return connection
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database connection error: {str(e)}",
            )

    def query_get(self, sql: str, param=()):
        """Trả về nhiều rows"""
        try:
            with self.get_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(sql, param)
                    return cursor.fetchall()
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Database error: {str(e)}"
            )

    def query_one(self, sql: str, param=()):
        """Trả về 1 row"""
        try:
            with self.get_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(sql, param)
                    return cursor.fetchone()
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Database error: {str(e)}"
            )

    def query_put(self, sql: str, param=()):
        """Update/Delete"""
        try:
            with self.get_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(sql, param)
                    connection.commit()
                    return cursor.rowcount
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Database error: {str(e)}"
            )

    def execute_returning_id(self, sql: str, param=()):
        """Insert + trả về ID"""
        try:
            with self.get_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(sql, param)
                    last_id = cursor.lastrowid
                    connection.commit()
                    return last_id
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Database error: {str(e)}"
            )

    def call_procedure(self, proc_name: str, params=()):
        """Gọi Stored Procedure và trả về kết quả"""
        try:
            with self.get_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.callproc(proc_name, params)

                    # Lấy luôn kết quả SELECT trong SP
                    results = cursor.fetchall()

                    connection.commit()  # cần commit nếu SP có insert/update
                    return results
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Stored procedure error: {str(e)}"
            )

