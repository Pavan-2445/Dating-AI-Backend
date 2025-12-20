from db import get_connection
from ml_utils import user_to_vector, pair_features, model
from filters import age_filter, gender_filter
from cooldown import cooldown_exceeded, log_request


def fetch_user_profile(user_id, cursor):
    cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
    return cursor.fetchone()


def fetch_user_answers(user_id, cursor):
    cursor.execute(
        "SELECT question_no, selected_option FROM user_answers WHERE user_id = %s",
        (user_id,)
    )
    rows = cursor.fetchall()
    return {row["question_no"]: row["selected_option"] for row in rows}


def generate_matches(user_id, top_n=5):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # 1️⃣ Cooldown check (max 3 successful requests per day)
    if cooldown_exceeded(cursor, user_id):
        conn.close()
        return {
            "user_id": user_id,
            "error": "Daily match request limit reached"
        }

    # 2️⃣ Fetch current user
    user = fetch_user_profile(user_id, cursor)
    if not user:
        conn.close()
        return {
            "user_id": user_id,
            "error": "User not found"
        }

    # 3️⃣ Fetch and validate answers
    user_answers = fetch_user_answers(user_id, cursor)

    # ✅ CRITICAL FIX (THIS WAS MISSING)
    if len(user_answers) < 40:
        conn.close()
        return {
            "user_id": user_id,
            "error": "User has not completed all 40 questions",
            "answered": len(user_answers)
        }

    user_vec = user_to_vector(user_answers)

    # 4️⃣ Fetch candidates
    cursor.execute("SELECT * FROM users WHERE user_id != %s", (user_id,))
    candidates = cursor.fetchall()

    scores = []

    for cand in candidates:
        # Hard filters
        if not age_filter(user, cand):
            continue
        if not gender_filter(user, cand):
            continue

        cand_answers = fetch_user_answers(cand["user_id"], cursor)

        # Skip candidates with incomplete answers
        if len(cand_answers) < 40:
            continue

        cand_vec = user_to_vector(cand_answers)

        pair_vec = pair_features(user_vec, cand_vec).reshape(1, -1)
        score = float(model.predict(pair_vec)[0])

        scores.append((cand["user_id"], score))

    # 5️⃣ Sort & take Top-N
    scores.sort(key=lambda x: x[1], reverse=True)
    scores = scores[:top_n]

    cursor.execute(
    "DELETE FROM user_matches WHERE user_id = %s",
    (user_id,)
    )

    # 6️⃣ Store matches
    for rank, (cid, score) in enumerate(scores, start=1):
        cursor.execute(
        """
        INSERT INTO user_matches
        (user_id, matched_user_id, compatibility_score, rank_position)
        VALUES (%s, %s, %s, %s)
        """,
        (user_id, cid, score, rank)
    )

    # Only log request if matches were successfully stored
    if scores:
        log_request(cursor, user_id)
        conn.commit()
    else:
        conn.commit()
    
    conn.close()

    # 7️⃣ Always return JSON
    if not scores:
        return {
            "user_id": user_id,
            "matches": [],
            "message": "No eligible matches found"
        }

    return {
        "user_id": user_id,
        "matches_count": len(scores),
        "message": f"Successfully computed {len(scores)} matches"
    }

def get_revealed_matches(user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # How many times user requested matches today
    cursor.execute("""
        SELECT COUNT(*) AS cnt
        FROM match_requests
        WHERE user_id = %s
        AND request_time >= NOW() - INTERVAL 1 DAY
    """, (user_id,))
    req_count = cursor.fetchone()["cnt"]

    if req_count == 0:
        conn.close()
        return {
            "user_id": user_id,
            "matches": [],
            "message": "No match requests yet"
        }

    # Fetch cached matches with usernames
    cursor.execute("""
        SELECT
            um.matched_user_id,
            um.compatibility_score,
            um.rank_position,
            u.username AS matched_username
        FROM user_matches um
        JOIN users u ON u.user_id = um.matched_user_id
        WHERE um.user_id = %s
        ORDER BY um.rank_position
        LIMIT %s
    """, (user_id, req_count))

    matches = cursor.fetchall()
    conn.close()

    # If we have requests but no matches, there might be an issue
    if req_count > 0 and not matches:
        return {
            "user_id": user_id,
            "revealed_upto": req_count,
            "matches": [],
            "message": "Matches were requested but none are available. Please try computing matches again."
        }

    return {
        "user_id": user_id,
        "revealed_upto": req_count,
        "matches": matches
    }
def match_label(score):
    if score >= 85:
        return "Perfect Match"
    elif score >= 70:
        return "Strong Match"
    elif score >= 55:
        return "Contrast Match"
    elif score >= 40:
        return "Moderate Match"
    else:
        return "Low Match"
