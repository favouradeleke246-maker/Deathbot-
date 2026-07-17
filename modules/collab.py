from modules.utils import get_db_connection

class Collaboration:
    @staticmethod
    def share_target(target_id, user_id):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO shared_targets (target_id, user_id) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                    (target_id, user_id))
        conn.commit()
        cur.close()
        conn.close()

    @staticmethod
    def unshare_target(target_id, user_id):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM shared_targets WHERE target_id = %s AND user_id = %s", (target_id, user_id))
        conn.commit()
        cur.close()
        conn.close()
