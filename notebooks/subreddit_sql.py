import sqlite3
import pathlib
import json

# https://www.sqlitetutorial.net/sqlite-python/creating-database/
def create_connection(db_file):
    """create a database connection to a SQLite database"""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except sqlite3.Error as e:
        print(e)

    return conn


def drop_reddit_table(connection, table_name):
    sql_cmd = f"DROP TABLE IF EXISTS {table_name};"
    c = connection.cursor()
    c.execute(sql_cmd)

    return


def get_all_keys(subreddit):
    all_keys = set()

    subreddit_directory = f"../data/raw/{subreddit}"
    subreddit_path = pathlib.Path(subreddit_directory)
    subreddit_glob = list(subreddit_path.glob("*.json"))

    for p in subreddit_glob:
        with p.open() as js:
            json_content = json.load(js)
            for k in json_content.keys():
                all_keys.add(k)

    return all_keys


def create_reddit_table(connection, table_name, all_keys):
    column_names = (
        ["id PRIMARY KEY"] + [key for key in all_keys if key != "id"] + ["article_text"]
    )
    column_string = ",".join(column_names)

    sql_cmd = f"CREATE TABLE IF NOT EXISTS {table_name} ({column_string});"

    c = connection.cursor()
    c.execute(sql_cmd)
    connection.commit()

    return


def make_row(json_content, article_text, all_keys):
    row = [json_content.get("id")]
    allowed_types = [str, int, float, bool]
    for key in all_keys:
        if key != "id":
            content = json_content.get(key, "")
            row.append(content if type(content) in allowed_types and content else None)
    row.append(article_text if article_text else None)

    return row


def insert_into_table(conn, row, table_name, all_keys):
    column_names = ["id"] + [key for key in all_keys if key != "id"] + ["article_text"]
    column_string = ",".join(column_names)
    question_marks = ",".join(["?" for _ in column_names])

    sql_cmd = f"INSERT INTO {table_name}({column_string})VALUES({question_marks});"

    c = conn.cursor()
    c.execute(sql_cmd, row)
    conn.commit()

    return


def sqlize(db, subreddit):
    conn = create_connection(db)

    all_keys = get_all_keys(subreddit)

    drop_reddit_table(conn, subreddit)
    create_reddit_table(conn, subreddit, all_keys)

    subreddit_directory = f"../data/raw/{subreddit}"
    subreddit_path = pathlib.Path(subreddit_directory)
    subreddit_json_glob = list(subreddit_path.glob("*.json"))
    N = len(subreddit_json_glob)

    for n, p in enumerate(subreddit_json_glob):
        # not sure if ordering is the same for json and txt
        t = pathlib.Path(p.parent / f"{p.stem}.txt")
        with p.open(mode="r") as js, t.open(mode="r") as txt:
            json_content = json.load(js)
            article_text = txt.read()
            row = make_row(json_content, article_text, all_keys)
            insert_into_table(conn, row, subreddit, all_keys)

            print(f"Posts SQLized: {n + 1}/{N}", end="\r")