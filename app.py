from fastapi import FastAPI
from match_engine import generate_matches, get_revealed_matches

app = FastAPI()

@app.get("/")
def home():
    return {"status": "Dating AI backend running"}

# Run ML & cache matches (ONLY ONCE NEEDED)
@app.post("/compute-matches/{user_id}")
def compute_matches(user_id: int):
    try:
        return generate_matches(user_id, top_n=10)
    except Exception as e:
        return {
            "error": "Internal server error",
            "details": repr(e)
        }

# Reveal matches incrementally
@app.get("/reveal-matches/{user_id}")
def reveal_matches(user_id: int):
    try:
        return get_revealed_matches(user_id)
    except Exception as e:
        return {
            "error": "Internal server error",
            "details": repr(e)
        }
