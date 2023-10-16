import os.path
import sqlite3 as sql

con = sql.connect('photo.db', check_same_thread=False)
cur = con.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS photo(id INTEGER PRIMARY KEY, photo BLOB, post TEXT UNIQUE, filename TEXT)""")

def PhotoAdd(photo_name, post_name, filename):
    try:
        with open(f"static/photos/{photo_name}", 'rb') as photo:
            cur.execute(f'INSERT INTO photo VALUES(NULL, ?, ?, ?)', (photo.read(), post_name, filename))
            con.commit()
    except sql.Error as e:
        print(str(e))
        return False

def PhotoDelete(post_name):
    try:
        cur.execute('DELETE FROM photo WHERE ? = post', (str(post_name),))
        con.commit()
    except sql.Error as e:
        print(str(e))
        return False
    return True

def getPhoto(post_name):
    try:
        cur.execute('SELECT * FROM photo WHERE ? = post', (post_name,))
        res = cur.fetchone()
        if res: return res
    except sql.Error as e:
        print(str(e))
        return False

"""def getLastPhotoName():
    path = 'static/photos'
    ss = []
    for i in os.listdir(path):
        ss.append(int(os.path.splitext(i)[0]))
    return max(ss)"""