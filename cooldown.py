def cooldown_exceeded(cursor, user_id):
    cursor.execute("""
        SELECT COUNT(*) AS cnt
        FROM match_requests
        WHERE user_id = %s
        AND request_time >= NOW() - INTERVAL 1 DAY
    """, (user_id,))

    row = cursor.fetchone()
    return row["cnt"] >= 3

def log_request(cursor, user_id):
    cursor.execute(
        "INSERT INTO match_requests (user_id) VALUES (%s)",
        (user_id,)
    )
