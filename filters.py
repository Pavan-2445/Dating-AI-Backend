def age_filter(user, candidate):
    if candidate["age"] < 18 or user["age"] < 18:
        return False

    return user["min_age"] <= candidate["age"] <= user["max_age"]

def gender_filter(user, candidate):
    """
    Gender preference filter.

    If user selects "All", we don't restrict by candidate gender.
    Otherwise we keep legacy behavior: candidate gender must be contained
    in the preferred_gender field.
    """
    pref = user.get("preferred_gender", "")
    if pref.lower() == "all":
        return True
    return candidate["gender"] in pref

def mutual_interest_filter(cursor, user_id, candidate_id):
    cursor.execute("""
        SELECT 1 FROM mutual_interest
        WHERE user_id = %s AND interested_user_id = %s
    """, (candidate_id, user_id))
    return cursor.fetchone() is not None
def fetch_user_profile(user_id, cursor):
    cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
    return cursor.fetchone()
