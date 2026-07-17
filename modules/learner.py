from modules.utils import get_db_connection

class Learner:
    @staticmethod
    def record_outcome(target_id, attack, success):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO learning (target_id, attack, success) VALUES (%s, %s, %s)",
                    (target_id, attack, success))
        conn.commit()
        cur.close()
        conn.close()

    @staticmethod
    def get_best_attack(target_id):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT attack, COUNT(*) as cnt FROM learning WHERE target_id = %s AND success = true GROUP BY attack ORDER BY cnt DESC LIMIT 1", (target_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        return row[0] if row else None
