import math
import sqlite3 as sq
import time

from flask import Flask, g
import os

class Config():
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'privet _will day its okey'

app = Flask(__name__)
app.config.from_object(Config)
app.config.update(dict(DATABASE=os.path.join(app.root_path,'../posts.db')))

def connect_db():
    conn = sq.connect(app.config['DATABASE'])
    conn.row_factory = sq.Row
    return conn


def get_db():
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
        return g.link_db

#Подключение базы данных

def create_db():
    '''Вспомогательная функция для создания таблиц БД '''
    db = connect_db()
    with app.open_resource('sql_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()
    return True

def connect_db():
    conn = sq.connect(app.config['DATABASE'])
    conn.row_factory = sq.Row
    return conn

def get_db():
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
        return g.link_db

#Создаем класс
class FDataBase:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()

    def addData(self, username, password):
        try:
            self.__cur.execute("INSERT INTO user VALUES (NULL, ?, ?)", (username, password))
            self.__db.commit()
        except sq.Error as e:
            print(str(e))
            return False
        return True

    def delData(self, id=0):
        try:
            if id == 0:
                self.__cur.execute("DELETE FROM user")
            else:
                self.__cur.execute(f"DELETE FROM user WHERE id == {id}")
            self.__db.commit()
        except sq.Error as e:
            print(str(e))
            return False
        return True

    def getData(self, username, password):
        try:
            self.__cur.execute("SELECT username, password FROM user WHERE ? = username AND ? = password", (username, password))
            res = self.__cur.fetchall()
            return res
        except sq.Error as e:
            print(str(e))
            return False

    def addMenu(self, title, url):
        try:
            self.__cur.execute("INSERT INTO menu VALUES (NULL, ?, ?)", (title, url))
            self.__db.commit()
        except sq.Error as e:
            print(str(e))
            return False
        return True

    def delMenu(self, id=0):
        try:
            if id == 0:
                self.__cur.execute("DELETE FROM menu")
            else:
                self.__cur.execute(f"DELETE FROM menu WHERE id == {id}")
            self.__db.commit()
        except sq.Error as e:
            print(str(e))
            return False
        return True

    def getMenu(self):
        try:
            self.__cur.execute("SELECT * FROM menu")
            res = self.__cur.fetchall()
            if res: return res
        except sq.Error as e:
            print(str(e))
            return False

    def addAdminMenu(self, title, url):
        try:
            self.__cur.execute("INSERT INTO adminmenu VALUES (NULL, ?, ?)", (title, url))
            self.__db.commit()
        except sq.Error as e:
            print(str(e))
            return False
        return True

    def delAdminMenu(self, id=0):
        try:
            if id == 0:
                self.__cur.execute("DELETE FROM adminmenu")
            else:
                self.__cur.execute("DELETE FROM adminmenu WHERE ? == id", (id))
            self.__db.commit()
        except sq.Error as e:
            print(str(e))
            return False
        return True

    def getAdminMenu(self):
        try:
            self.__cur.execute("SELECT * FROM adminmenu")
            res = self.__cur.fetchall()
            if res: return res
        except sq.Error as e:
            print(str(e))
            return False
        return True

    def addPost(self, title, text, photo):
        try:
            tm = time.ctime()
            self.__cur.execute("INSERT INTO post VALUES (NULL, ?, ?, ?, ?)", (title, text, photo, tm))
            self.__db.commit()
        except sq.Error as e:
            print(str(e))
            return False
        return True

    def delPost(self, id=0):
        try:
            if id == 0:
                self.__cur.execute("DELETE FROM post")
            else:
                self.__cur.execute(f"DELETE FROM post WHERE {id} == id")
            self.__db.commit()
        except sq.Error as e:
            print(str(e))
            return False
        return True

    def getPostAnnoce(self):
        try:
            self.__cur.execute(f"SELECT id, title, text, photo, time FROM post ORDER BY time DESC")
            res = self.__cur.fetchall()
            if res: return res
        except sq.Error as e:
            print("Ошибка получения статей из БД" + str(e))
        return []

    def getPost(self, postid):
        try:
            self.__cur.execute(f"SELECT title, text, photo FROM post WHERE id = {postid} LIMIT 1")
            res = self.__cur.fetchone()
            if res: return res
        except sq.Error as e:
            print("Ошибка получения статьи из БД" + str(e))
        return (False, False)

    def addComment(self, username, text, postid):
        try:
            self.__cur.execute("INSERT INTO comments VALUES (NULL, ?, ?, ?)", (username, text, postid))
            self.__db.commit()
        except sq.Error as e:
            print(str(e))
            return False
        return True

    def delComment(self, postid=0, id=0):
        try:
            if postid == 0:
                self.__cur.execute("DELETE FROM comments")
            else:
                self.__cur.execute(f"DELETE FROM comments WHERE postid == {postid} AND id == {id}")
            self.__db.commit()
        except sq.Error as e:
            print(str(e))
            return False
        return True

    def getComments(self, postid):
        try:
            self.__cur.execute(f"SELECT * FROM comments WHERE postid == {postid}")
            res = self.__cur.fetchall()
            return res
        except sq.Error as e:
            print(str(e))
            return False

    def addTODO(self, text):
        try:
            tm = time.time()
            self.__cur.execute(f"INSERT INTO todo VALUES (NULL, ?, ?)", (text, tm))
            self.__db.commit()
        except sq.Error as e:
            print(str(e))
            return False
        return True

    def delTODO(self, id=0):
        try:
            if id == 0:
                self.__cur.execute("DELETE FROM todo")
            else:
                self.__cur.execute(f"DELETE FROM todo WHERE id == {id}")
            self.__db.commit()
        except sq.Error as e:
            print(str(e))
            return False
        return True

    def getTODO(self):
        try:
            self.__cur.execute("SELECT * FROM todo")
            res = self.__cur.fetchall()
            return res
        except sq.Error as e:
            print(str(e))
            return False

    def addUpdates(self, title, text, photo):
        try:
            tm = time.ctime()
            self.__cur.execute("INSERT INTO updates VALUES (NULL, ?, ?, ?, ?)", (title, text, photo, tm))
            self.__db.commit()
        except sq.Error as e:
            print(str(e))
            return False
        return True

    def delUpdates(self, id=0):
        try:
            if id == 0:
                self.__cur.execute("DELETE FROM updates")
            else:
                self.__cur.execute(f"DELETE FROM updates WHERE {id} == id")
            self.__db.commit()
        except sq.Error as e:
            print(str(e))
            return False
        return True

    def getUpdate(self, updateid):
        try:
            self.__cur.execute(f"SELECT title, text, photo FROM updates WHERE id = {updateid} LIMIT 1")
            res = self.__cur.fetchone()
            if res: return res
        except sq.Error as e:
            print("Ошибка получения обновления из БД" + str(e))
        return (False, False)

    def getUpdatesAnnoce(self):
        try:
            self.__cur.execute(f"SELECT id, title, text, photo, time FROM updates ORDER BY id DESC")
            res = self.__cur.fetchall()
            return res
        except sq.Error as e:
            print("Ошибка получения обновлений из БД" + str(e))
        return []

    def UpdateUpdate(self, title, text, photo, id):
        try:
            self.__cur.execute(f"UPDATE updates SET title == ?, text == ?, photo == ? WHERE id == ?", (title, text, photo, id))
            self.__db.commit()
        except sq.Error as e:
            print(str(e))
            return False
        return True

    def getUpdatesAnnoce(self):
        try:
            self.__cur.execute(f"SELECT id, title, text, photo, time FROM updates ORDER BY id DESC")
            res = self.__cur.fetchall()
            return res
        except sq.Error as e:
            print("Ошибка получения обновлений из БД" + str(e))
        return []

    def PostUpdate(self, title, text, photo, postid):
        try:
            self.__cur.execute(f"UPDATE post SET title == ?, text == ?, photo == ? WHERE id == ?", (title, text, photo, postid))
            self.__db.commit()
        except sq.Error as e:
            print(str(e))
            return False
        return True


if __name__ == "__main__":
    #from app import connect_db
    db = connect_db()
    db = FDataBase(db)
    #create_db()
    #print(db.delData(0))
    #print(db.delMenu(0))
    #print(db.addMenu('Главная', 'start_page'))
    #print(db.addMenu('Авторизация', 'login'))
    #print(db.addMenu('Обновления', 'update_page'))
    #print(db.delAdminMenu(0))
    #print(db.addAdminMenu('Главная', 'start_page'))
    #print(db.addAdminMenu('Добавить пост', 'post'))
    #print(db.addAdminMenu('Admin', 'admin_page'))
    #print(db.addAdminMenu('Обновления', 'update_page'))
    #print(db.addAdminMenu('Выход', 'quit_login'))

