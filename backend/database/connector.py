from fastapi import HTTPException, status
import os
import pymysql.cursors
from pymysql import converters

class DatabaseConnector:
    def __init__(self):
        self.host = os.getenv("DATABASE_HOST")
        self.user = os.getenv("DATABASE_USERNAME")
        self.password = os.getenv("DATABASE_PASSWORD")
        self.database = os.getenv("DATABASE")
        self.port = int(os.getenv("DATABASE_PORT"))
        self.conversions = converters.conversions
        self.conversions[pymysql.FIELD_TYPE.BIT] = (
            lambda x: False if x == b"\x00" else True
        )
        if not self.host:
            raise EnvironmentError("DATABASE_HOST environment variable not found")
        if not self.user:
            raise EnvironmentError("DATABASE_USERNAME environment variable not found")
        if not self.password:
            raise EnvironmentError("DATABASE_PASSWORD environment variable not found")
        if not self.database:
            raise EnvironmentError("DATABASE environment variable not found")

    def get_connection(self):
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

    def query_get(self, sql, param):
        try:
            connection = self.get_connection()
            with connection:
                with connection.cursor() as cursor:
                    cursor.execute(sql, param)
                    return cursor.fetchall()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error: " + str(e),
            )

    def query_put(self, sql, param):
        try:
            connection = self.get_connection()
            with connection:
                with connection.cursor() as cursor:
                    cursor.execute(sql, param)
                    connection.commit()
                    return cursor.rowcount
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error: " + str(e),
            )

    def call_proc(self, proc_name: str, params: tuple = (), *, return_all: bool = False):
        """
        Gọi stored procedure và trả về list[dict].
        - Mặc định trả về result set CUỐI CÙNG (phù hợp khi proc SELECT bản ghi cuối cùng).
        - Nếu return_all=True -> trả về list các result set [[...], [...], ...].
        """
        conn = self.get_connection()
        cursor = None
        try:
            # Lấy dict cursor cho mọi driver
            try:
                # mysql-connector-python
                cursor = conn.cursor(dictionary=True)
            except TypeError:
                # PyMySQL / MySQLdb
                try:
                    import pymysql
                    cursor = conn.cursor(pymysql.cursors.DictCursor)
                except Exception:
                    from MySQLdb.cursors import DictCursor  # type: ignore
                    cursor = conn.cursor(DictCursor)

            # Gọi procedure
            cursor.callproc(proc_name, params)

            # Thu thập tất cả result sets (proc có thể trả nhiều SELECT)
            all_sets = []
            while True:
                try:
                    rows = cursor.fetchall()
                    if rows is not None:
                        all_sets.append(rows)
                except Exception:
                    pass
                # nextset() -> False khi hết
                if not hasattr(cursor, "nextset") or not cursor.nextset():
                    break

            conn.commit()  # QUAN TRỌNG: để dữ liệu thấy ngay

            if return_all:
                return all_sets
            # Trả set cuối (thường là SELECT * ... ở cuối proc)
            return all_sets[-1] if all_sets else []

        except Exception as e:
            try: conn.rollback()
            except Exception: pass
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error (proc {proc_name}): {e}",
            )
        finally:
            try:
                if cursor: cursor.close()
            finally:
                try: conn.close()
                except Exception: pass