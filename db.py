import os
import mysql.connector
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def get_connection():
    """
    Central DB connection using environment variables.

    Required env vars (with sensible local defaults):
      - DB_HOST
      - DB_USER
      - DB_PASSWORD
      - DB_NAME
    """
    return mysql.connector.connect(
        host=os.environ["DB_HOST"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        database=os.environ["DB_NAME"],
    )


if __name__ == "__main__":
    # Small manual sanity-check without running on import.
    conn = get_connection()
    print("DB connected")
    conn.close()
