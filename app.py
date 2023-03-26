from flask import render_template, Flask, request, redirect, url_for, session, g, abort, flash
from config import Config
from database.sqldb import FDataBase
import git

import os, sqlite3

app = Flask(__name__)
app.config.from_object(Config)
app.config.update(dict(DATABASE=os.path.join(app.root_path,'../posts.db')))



def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn


def get_db():
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
        return g.link_db

@app.route('/', methods=['GET', 'POST'])
def first_page():
    return redirect(url_for('start_page'))

@app.route('/update_server', methods=['POST', 'GET'])
def webhook():
    if request.method == 'POST':
        repo = git.Repo('/home/dodik337/myblogsite')
        origin = repo.remotes.origin
        origin.pull()
        return 'Сайт обновился', 200
    else:
        return 'Возникла ошибка', 400


#Main page
@app.route('/index', methods=['GET', 'POST'])
def start_page():
    db = get_db()
    database = FDataBase(db)
    return render_template('allposts.html', menu=database.getMenu(), posts=database.getPostAnnoce())

#Login
@app.route('/login', methods=['POST', 'GET'])
def login():
    db = get_db()
    database = FDataBase(db)
    if 'userlogged' in session:
        return redirect(url_for('start_page', username=session['userlogged']))
    elif request.method == 'POST' and database.getData(request.form['username'], request.form['password']):
        session['userlogged'] = request.form['username']
        return redirect(url_for('start_page', username=session['userlogged']))
    return render_template('login.html', title="Авторизация")

#Admin Page
@app.route('/admin', methods=['POST', 'GET'])
def admin_page():
    db = get_db()
    database = FDataBase(db)
    if 'userlogged' in session:
        if session['userlogged'] == 'admin':
            return render_template('admin.html', title='Admin Page', menu=database.getAdminMenu(), posts=database.getPostAnnoce())
    return redirect(url_for('start_page'))

@app.route('/post', methods=['POST', 'GET'])
def post():
    db = get_db()
    database = FDataBase(db)
    if 'userlogged' in session:
        if session['userlogged'] == 'admin':
            if request.method == 'POST':
                if len(request.form['name']) > 3 and len(request.form['post']) > 10:
                    res = database.addPost(request.form['name'], request.form['post'])
                    if not res:
                        flash('Ошибка добавления статьи', category='error')
                    else:
                        flash('Статья добавлена успешно', category='success')
                else:
                    flash('Ошибка добавления статьи', category='error')
            return render_template('post.html', title='Добавить статью', menu=database.getMenu())
    return redirect(url_for('start_page'))

#Quit
@app.route('/quit', methods=['GET', 'POST'])
def quit_login():
    db = get_db()
    database = FDataBase(db)
    if 'userlogged' in session:
        return render_template('quit_page.html', title='Выход', menu=database.getMenu()), session.clear()
    else:
        return redirect(url_for('start_page'))

@app.route('/allposts')
def allposts():
    db = get_db()
    database = FDataBase(db)
    return render_template('allposts.html', title='Cписок постов', menu=database.getMenu(),
                           posts=database.getPostAnnoce())

@app.route('/delpost/<int:id_post>')
def delpost_page(id_post):
    db = get_db()
    database = FDataBase(db)
    title = database.getPostAnnoce()
    aticle = database.getPostAnnoce()
    if 'userlogged' in session:
        if session['userlogged'] == 'admin':
            delpost = database.delPost(id_post)
            if not title:
                abort(404)
            if delpost:
                return redirect(url_for('admin_page'))
            return render_template('admin.html', title='title', menu=database.getAdminMenu(), post=aticle, post_title=title)
    else:
        return redirect(url_for('start_page'))

@app.route('/posts/<int:id_post>')
def showPost(id_post):
    db = get_db()
    database = FDataBase(db)
    title, aticle = database.getPost(id_post)
    if not title:
        abort(404)
    return render_template('aticle.html', title='title', menu=database.getMenu(), post=aticle, post_title=title)


if __name__ == "__main__":
    app.run(debug=True)