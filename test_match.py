import mysql.connector
import numpy as np
import joblib
from dotenv import load_dotenv
load_dotenv()
#db connection
def get_connection():
    return mysql.connector.connect(
        host=os.environ["DB_HOST"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        database=os.environ["DB_NAME"],
    )
#load models
model = joblib.load("../model/compatibility_model.pkl")
WEIGHT_MAP = joblib.load("../model/weight_map.pkl")
#fetch users from db
def fetch_user_answers(user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT question_no, selected_option FROM user_answers WHERE user_id = %s",
        (user_id,)
    )

    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    return {row["question_no"]: row["selected_option"] for row in rows}
#convert user answers to vector
def user_to_vector(user_answers):
    vec = []
    for q in range(1, 41):
        option = user_answers.get(q)
        vec.append(WEIGHT_MAP[q].get(option, 0.0))
    return np.array(vec)
#pair wise feature builder
def pair_features(vecA, vecB):
    diff = np.abs(vecA - vecB)
    return np.concatenate([
        diff,
        [vecA.sum(), vecB.sum()]
    ])
#fetch eligible candidates
def fetch_candidate_users(current_user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT user_id FROM users WHERE user_id != %s",
        (current_user_id,)
    )

    users = cursor.fetchall()
    cursor.close()
    conn.close()

    return [u["user_id"] for u in users]
#generate and store
def generate_and_store_matches(user_id, top_n=5):
    user_answers = fetch_user_answers(user_id)
    user_vec = user_to_vector(user_answers)

    candidates = fetch_candidate_users(user_id)
    scores = []

    for cand_id in candidates:
        cand_answers = fetch_user_answers(cand_id)
        cand_vec = user_to_vector(cand_answers)

        pair_vec = pair_features(user_vec, cand_vec).reshape(1, -1)
        score = model.predict(pair_vec)[0]

        scores.append((cand_id, float(score)))

    scores.sort(key=lambda x: x[1], reverse=True)
    scores = scores[:top_n]

    conn = get_connection()
    cursor = conn.cursor()

    for rank, (cid, score) in enumerate(scores, start=1):
        cursor.execute(
            """
            INSERT INTO user_matches (user_id, matched_user_id, compatibility_score, rank_position)
            VALUES (%s, %s, %s, %s)
            """,
            (user_id, cid, score, rank)
        )

    conn.commit()
    cursor.close()
    conn.close()
if __name__ == "__main__":
    generate_and_store_matches(user_id=1, top_n=3)
    print("Top matches generated and stored")
