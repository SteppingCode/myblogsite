import os.path
import sqlite3 as sq
from flask import Flask, g
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
app.config.update(dict(PHOTOBASE=os.path.join(app.root_path,'../photo.db')))

def connect_photo():
    photo = sq.connect(app.config['PHOTOBASE'], check_same_thread=False)
    photo.row_factory = sq.Row
    return photo

def get_db():
    if not hasattr(g, 'link_db'):
        g.link_db = connect_photo()
        return g.link_db

#Подключение базы данных
def create_db():
    '''Вспомогательная функция для создания таблиц БД '''
    db = connect_photo()
    with app.open_resource('photo.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()
    return True

class Photo:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()

    def PhotoAdd(self, photo_name: str, post_name: str, filename: str):
        try:
            with open(os.path.join(app.root_path,'../static/photos/',photo_name), 'rb') as photo:
                self.__cur.execute('INSERT INTO photo VALUES(NULL, ?, ?, ?)', (photo.read(), post_name, filename))
                self.__db.commit()
        except sq.Error as e:
            print(str(e))
            return False

    def PhotoDelete(self, post_name):
        try:
            self.__cur.execute('DELETE FROM photo WHERE ? = post', (str(post_name),))
            self.__db.commit()
        except sq.Error as e:
            print(str(e))
            return False
        return True

    def getPhoto(self, post_name):
        try:
            self.__cur.execute('SELECT * FROM photo WHERE ? = post', (post_name,))
            res = self.__cur.fetchone()
            if res: return res
        except sq.Error as e:
            print(str(e))
            return False

if __name__ == "__main__":
    #from app import connect_db
    db = connect_photo()
    db = Photo(db)
    #create_db()
    #print(db.PhotoAdd('favicon.png', 'ghfghfghfghfghfghf', 'favicon.png'))

"""def getLastPhotoName():
    path = 'static/photos'
    ss = []
    for i in os.listdir(path):
        ss.append(int(os.path.splitext(i)[0]))
    return max(ss)"""