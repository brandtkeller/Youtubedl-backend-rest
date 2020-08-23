import psycopg2
from config import config


def create_table():
    print('Creating Video table')
    """ create tables in the PostgreSQL database"""
    commands = (
        """
        CREATE TABLE IF NOT EXISTS videos (
            id SERIAL PRIMARY KEY,
            vid_url VARCHAR(255) NOT NULL,
            title VARCHAR(255),
            status VARCHAR(255) NOT NULL,
            status_message VARCHAR(255) NOT NULL,
            vid_dir varchar(255)
        )
        """)
    conn = None
    try:
        # read the connection parameters
        params = config()
        # connect to the PostgreSQL server
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.execute(commands)
        # close communication with the PostgreSQL database server
        cur.close()
        # commit the changes
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

def get_all_rows():
    print('Querying all rows in DB')
    conn = None
    rows = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.execute("SELECT * FROM videos")
        rows = cur.fetchall()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
    return rows

def get_row_by_id(id):
    print('Querying for a specific row  with id = ' + str(id))
    conn = None
    row = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.execute("SELECT * FROM videos WHERE id = %s",(id,))
        row = cur.fetchone()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
    return row

def create_row(vid_url, title, status, status_message, vid_dir):
    # Insert row creation logic
    print('Creating row in database')
    sql = """INSERT INTO videos(vid_url, title, status, status_message, vid_dir)
             VALUES(%s, %s, %s, %s, %s) RETURNING id;"""
    conn = None
    id = None
    try:
        # read database configuration
        params = config()
        # connect to the PostgreSQL database
        conn = psycopg2.connect(**params)
        # create a new cursor
        cur = conn.cursor()
        # execute the INSERT statement
        cur.execute(sql, (vid_url, title, status, status_message, vid_dir))
        # get the generated id back
        id = cur.fetchone()[0]
        # commit the changes to the database
        conn.commit()
        # close communication with the database
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

    return id

# We can simply update all parameters for now until we want to improve performance
# Maybe we pass a key/value pair for which parameters are being changed and loop
def update_row(id, vid_url, title, status, status_message, vid_dir):
    print('Updating row in database')
    sql = """ UPDATE videos
                SET vid_url = %s, title = %s, status = %s, status_message = %s, vid_dir = %s
                WHERE id = %s"""
    conn = None
    try:
        # read database configuration
        params = config()
        # connect to the PostgreSQL database
        conn = psycopg2.connect(**params)
        # create a new cursor
        cur = conn.cursor()
        # execute the Update statement
        cur.execute(sql, (vid_url, title, status, status_message, vid_dir, id))
        # commit the changes to the database
        conn.commit()
        # close communication with the database
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

def delete_row(id):
    print('Removing row from database')
    conn = None
    rows_deleted = 0
    try:
        # read database configuration
        params = config()
        # connect to the PostgreSQL database
        conn = psycopg2.connect(**params)
        # create a new cursor
        cur = conn.cursor()
        # execute the UPDATE  statement
        cur.execute("DELETE FROM videos WHERE id = %s", (id,))
        # get the number of updated rows
        rows_deleted = cur.rowcount
        # Commit the changes to the database
        conn.commit()
        # Close communication with the PostgreSQL database
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

    return rows_deleted