from modules.utils import get_db_connection

class AdminManager:
    @staticmethod
    def is_admin(user_id):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM admins WHERE user_id = %s", (user_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        return row is not None

    @staticmethod
    def add_admin(user_id):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO admins (user_id) VALUES (%s) ON CONFLICT DO NOTHING", (user_id,))
        conn.commit()
        cur.close()
        conn.close()
        return True

    @staticmethod
    def remove_admin(user_id):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM admins WHERE user_id = %s", (user_id,))
        conn.commit()
        cur.close()
        conn.close()
        return True

    @staticmethod
    def list_admins():
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT user_id, added_at FROM admins ORDER BY added_at")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows
