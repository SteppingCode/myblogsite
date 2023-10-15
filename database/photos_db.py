import os.path
import sqlite3 as sql

con = sql.connect('../photo.db')
cur = con.cursor()

cur.execute('CREATE TABLE IF NOT EXISTS photo(id INTEGER PRIMARY KEY, photo BLOB NOT NULL)')

class Photo:
    def __init__(self, con):
        self.__db = con
        self.__cur = con.cursor()
    def PhotoAdd(self, photo_name):
        try:
            with open(f"../photos/{photo_name}.png", 'rb') as photo:
                self.__cur.execute(f'INSERT INTO photo VALUES(NULL, ?)', [photo.read(),])
                self.__db.commit()
                self.__cur.close()
                self.__db.close()
        except sql.Error as e:
            print(str(e))
            return False

def getLastPhotoName():
    path = '../photos/'
    ss = []
    for i in os.listdir(path):
        ss.append(int(i[0]))
    print(max(ss))

getLastPhotoName()