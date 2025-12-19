import os
import mysql.connector
import joblib
from collections import defaultdict
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

MODEL_DIR = "model"
MODEL_PATH = os.path.join(MODEL_DIR, "weight_map.pkl")

def get_db_connection():
    return mysql.connector.connect(
        host=os.environ["DB_HOST"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        database=os.environ["DB_NAME"],
    )

def build_weight_map():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT question_no, option_code, weight
        FROM question_options
        ORDER BY question_no
    """)

    rows = cursor.fetchall()
    conn.close()

    weight_map = defaultdict(dict)

    for row in rows:
        weight_map[row["question_no"]][row["option_code"]] = float(row["weight"])

    return dict(weight_map)

if __name__ == "__main__":
    os.makedirs(MODEL_DIR, exist_ok=True)  # 🔥 FIX HERE

    weight_map = build_weight_map()
    joblib.dump(weight_map, MODEL_PATH)

    print("✅ weight_map.pkl generated successfully")
    print(f"📊 Total questions loaded: {len(weight_map)}")
