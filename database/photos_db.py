import os.path
import sqlite3 as sql

con = sql.connect('photo.db', check_same_thread=False)
cur = con.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS photo(id INTEGER PRIMARY KEY, photo BLOB NOT NULL, post TEXT NOT NULL UNIQUE)""")

def PhotoAdd(photo_name, post_name):
    try:
        with open(f"photos/{photo_name}.png", 'rb') as photo:
            cur.execute(f'INSERT INTO photo VALUES(NULL, ?, ?)', (photo.read(), post_name))
            con.commit()
    except sql.Error as e:
        print(str(e))
        return False

def getPhoto(post_name):
    try:
        cur.execute('SELECT photo FROM photo WHERE ? = post', (post_name,))
        res = cur.fetchone()
        if res: return res
    except sql.Error as e:
        print(str(e))
        return False

def getLastPhotoName():
    path = 'photos'
    ss = []
    for i in os.listdir(path):
        ss.append(int(os.path.splitext(i)[0]))
    return max(ss)