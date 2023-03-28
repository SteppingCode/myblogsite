import math
import sqlite3 as sq
import time
import datetime
from flask import Flask, g
from config import Config
import os

app = Flask(__name__)
app.config.from_object(Config)
app.config.update(dict(DATABASE=os.path.join(app.root_path,'../posts.db')))

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
        return True

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

    def PostUpdate(self, title, text, photo, postid):
        try:
            self.__cur.execute(f"UPDATE post SET title == ?, text == ?, photo == ? WHERE id == ?", (title, text, photo, postid))
            self.__db.commit()
        except sq.Error as e:
            print(str(e))
            return False
        return True

if __name__ == "__main__":
    from app import connect_db
    db = connect_db()
    db = FDataBase(db)
    #create_db()
    #print(db.delData(0))
    #print(db.addData('admin', '111'))
    #print(db.delMenu(0))
    #print(db.addMenu('Главная', 'start_page'))
    #print(db.addMenu('Авторизация', 'login'))
    #print(db.delAdminMenu(0))
    #print(db.addAdminMenu('Главная', 'start_page'))
    #print(db.addAdminMenu('Добавить пост', 'post'))
    #print(db.addAdminMenu('Admin', 'admin_page'))
    #print(db.addAdminMenu('Выход', 'quit_login'))
    #print(db.addPost('Брянск', 'Брянск это хороший город России!', 'http://t0.gstatic.com/licensed-image?q=tbn:ANd9GcQFDyEYcz2fF8CeyHLlcvTwBQqcZAzvyJlA6dxm_S870ENJT2r208KBxz2-QWv7_Pom'))
    #print(db.delPost(12))
    #print(db.getPostAnnoce())
    #print(db.PostUpdate('', '', 11))

