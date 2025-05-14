import os
from urllib.parse import quote_plus
from sqlalchemy import create_engine
from sqlalchemy.engine import URL


# gets the env variables for the database connection
def get_engine(schema: str = "c12de"):
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT", "5432")
    dbname = os.getenv("DB_NAME")
    if not all([user, password, host, dbname]):
        raise ValueError(
            "missing environment variables: "
        )
# handles the case when the password contains special characters
    pw_esc = quote_plus(password)
# creates the connection string
    url = URL.create(
        "postgresql+psycopg2",
        username=user,
        password=pw_esc,
        host=host,
        port=port,
        database=dbname,
        query={"options": f"-csearch_path={schema}"}
    )
    return create_engine(url)
