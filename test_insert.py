import mysql.connector
from dotenv import load_dotenv
load_dotenv()

def get_connection():
    return mysql.connector.connect(
        host=os.environ["DB_HOST"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        database=os.environ["DB_NAME"],
    )
def insert_user(age, gender, preferred_gender, min_age, max_age):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
    INSERT INTO users (age, gender, preferred_gender, min_age, max_age)
    VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(query, (age, gender, preferred_gender, min_age, max_age))
    conn.commit()

    user_id = cursor.lastrowid
    cursor.close()
    conn.close()

    return user_id
def insert_answers(user_id, answers_dict):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
    INSERT INTO user_answers (user_id, question_no, selected_option)
    VALUES (%s, %s, %s)
    """

    for q_no, option in answers_dict.items():
        cursor.execute(query, (user_id, q_no, option))

    conn.commit()
    cursor.close()
    conn.close()
user_answers = {
 1: "Exploring something new",
 2: "Start the conversation",
 3: "Open after trust",
 4: "Go with the flow",
 5: "Thoughtful messages",
 6: "Serious long-term",
 7: "Talk immediately",
 8: "Deep conversations",
 9: "Occasionally",
10: "Loyalty",
11: "Very close",
12: "Small & deep",
13: "Adventure",
14: "Regular exercise",
15: "Quality time",
16: "Definitely",
17: "Logic first",
18: "Meditate",
19: "Huge priority",
20: "Deep bond",

21: "Workaholic",
22: "Too serious",
23: "Cold detachment",
24: "Negativity",
25: "One-word replies",
26: "Not over ex",
27: "Ignoring messages",
28: "Ignoring feelings",
29: "Over-networking",
30: "Disrespect",
31: "Dislikes PDA",
32: "Ghosting",
33: "Noisy club",
34: "Mocking",
35: "Perfectionist",
36: "Poor hygiene",
37: "Workaholic",
38: "Dirty jokes",
39: "Dishonesty",
40: "Emotionally unavailable"
}
user2_answers = {
 1: "Out with friends",
 2: "Listen to them",
 3: "Very emotionally open",
 4: "Love surprises",
 5: "Fast replies",
 6: "Serious long-term",
 7: "Take time",
 8: "Shared goals",
 9: "All the time",
10: "Emotional depth",
11: "Somewhat close",
12: "Big & diverse",
13: "Dinner & deep talk",
14: "Sometimes",
15: "Words of affirmation",
16: "Sometimes",
17: "Feeling first",
18: "Talk with people",
19: "Somewhat",
20: "Deep bond",

21: "Always staying home",
22: "Overly loud",
23: "Drama",
24: "Overthinking",
25: "Over-texting",
26: "Lets see",
27: "Talking over",
28: "Talking only self",
29: "Loud crowds",
30: "Always negative",
31: "Over PDA",
32: "No effort",
33: "Awkward dinner",
34: "Sarcasm overload",
35: "Dreamy ideals",
36: "Chronic lateness",
37: "Constant travel",
38: "Dark sarcasm",
39: "Indecisive",
40: "Jealous control"
}
user2_id = insert_user(
    age=22,
    gender="Female",
    preferred_gender="Male",
    min_age=21,
    max_age=26
)

insert_answers(user2_id, user2_answers)
print("Second user inserted:", user2_id)

if __name__ == "__main__":
    user_id = insert_user(
        age=23,
        gender="Male",
        preferred_gender="Female",
        min_age=21,
        max_age=26
    )

    insert_answers(user_id, user_answers)

    print("User inserted with ID:", user_id)
