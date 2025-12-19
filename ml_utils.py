import joblib
import numpy as np

model = joblib.load("model/compatibility_model.pkl")
WEIGHT_MAP = joblib.load("model/weight_map.pkl")

def user_to_vector(user_answers):
    vec = []

    # Force questions 1 → 40 only
    for q in range(1, 41):
        q_weights = WEIGHT_MAP.get(q)

        # If weight map itself is missing the question
        if q_weights is None:
            vec.append(0.0)
            continue

        option = user_answers.get(q)

        # If user didn't answer this question
        if option is None:
            vec.append(0.0)
            continue

        # Safe lookup
        vec.append(q_weights.get(option, 0.0))

    return np.array(vec, dtype=float)

def pair_features(vecA, vecB):
    vecA = np.asarray(vecA, dtype=float)
    vecB = np.asarray(vecB, dtype=float)

    diff = np.abs(vecA - vecB)
    return np.concatenate([diff, [vecA.sum(), vecB.sum()]])
