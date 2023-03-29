import time
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
    if 'userlogged' in session:
        if session['userlogged'] == 'admin':
            return render_template('allposts.html', title="Главная", menu=database.getAdminMenu(), posts=database.getPostAnnoce())
    return render_template('allposts.html', title="Главная", menu=database.getMenu(), posts=database.getPostAnnoce())

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
            if request.method == 'POST':
                addtodo = database.addTODO(request.form['text'])
                if addtodo:
                    flash('Дело добавлено!', category='success')
                else:
                    flash('Дело не было добавлено!', category='error')
                return redirect(url_for('admin_page'))
            return render_template('admin.html', title='Admin Page', menu=database.getAdminMenu(), posts=database.getPostAnnoce(), todo=database.getTODO())
    return redirect(url_for('start_page'))

@app.route('/post', methods=['POST', 'GET'])
def post():
    db = get_db()
    database = FDataBase(db)
    if 'userlogged' in session:
        if session['userlogged'] == 'admin':
            if request.method == 'POST':
                if len(request.form['name']) > 3 and len(request.form['post']) > 10:
                    res = database.addPost(request.form['name'], request.form['post'], request.form['photo'])
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
    if 'userlogged' in session:
        if session['userlogged'] == 'admin':
            return redirect(url_for('start_page')), session.clear()

@app.route('/allposts')
def allposts():
    db = get_db()
    database = FDataBase(db)
    return render_template('allposts.html', title='Cписок постов', menu=database.getMenu(),
                           posts=database.getPostAnnoce())

@app.route('/editpost/<int:id_post>', methods=['POST', 'GET'])
def post_edit(id_post):
    db = get_db()
    database = FDataBase(db)
    if 'userlogged' in session:
        if session['userlogged'] == 'admin':
            if request.method == 'POST':
                if len(request.form['title']) > 3 and len(request.form['text']) > 10:
                    res = database.PostUpdate(request.form['title'], request.form['text'], request.form['photo'], id_post)
                    if not res:
                        flash('Ошибка редактирования статьи', category='error')
                    else:
                        flash('Статья успешно редактирована', category='success')
                else:
                    flash('Ошибка редактирования статьи', category='error')
            return render_template('post_edit.html', title='Редактировать статью', menu=database.getMenu(), post=database.getPost(id_post))
    return redirect(url_for('start_page'))

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


@app.route('/posts/<int:id_post>', methods=['POST', 'GET'])
def showPost(id_post):
    db = get_db()
    database = FDataBase(db)
    title, aticle, photo = database.getPost(id_post)
    comments = database.getComments(id_post)
    if comments:
        if request.method == 'POST':
            if len(request.form['username']) > 3 and len(request.form['text']) > 3:
                addcom = database.addComment(request.form['username'], request.form['text'], id_post)
                if addcom:
                    flash('Комментарий добавлен', category='success')
                    return redirect(url_for('showPost', id_post=id_post))
                else:
                    flash('Ошибка добавления комментария', category='error')
            else:
                flash('Ошибка добавления комментария', category='error')
        return render_template('aticle.html', title=title, menu=database.getMenu(), post=aticle, post_title=title, post_image=photo, comments=comments)
    if request.method == 'POST':
        if len(request.form['username']) > 3 and len(request.form['text']) > 3:
            addcom = database.addComment(request.form['username'], request.form['text'], id_post)
            if addcom:
                flash('Комментарий добавлен', category='success')
                return redirect(url_for('showPost', id_post=id_post))
            else:
                flash('Ошибка добавления комментария', category='error')
        else:
            flash('Ошибка добавления комментария', category='error')
        return render_template('aticle.html', title=title, menu=database.getMenu(), post=aticle, post_title=title, post_image=photo, comments=comments)
    return render_template('aticle.html', title=title, menu=database.getMenu(), post=aticle, post_title=title, post_image=photo)

@app.route('/delcom/<int:id_post>/<int:id_com>')
def delcom_page(id_post, id_com):
    db = get_db()
    database = FDataBase(db)
    if 'userlogged' in session:
        if session['userlogged'] == 'admin':
            delcom = database.delComment(id_post, id_com)
            if delcom:
                return redirect(url_for('start_page'))
            return render_template('aticle.html', menu=database.getAdminMenu())
    else:
        return redirect(url_for('start_page'))

#Update page
@app.route('/updates_log', methods=['POST', 'GET'])
def update_page():
    db = get_db()
    database = FDataBase(db)
    if 'userlogged' in session:
        if session['userlogged'] == 'admin':
            if request.method == 'POST':
                addupd = database.addUpdates(request.form['title'], request.form['text'], request.form['photo'])
                if addupd:
                    flash('Обновление опубликовано!', category='success')
                    return redirect(url_for('update_page'))
                else:
                    flash('Обновление не опубликовано', category='error')
                    return redirect(url_for('update_page'))
            return render_template('updates.html', title='Обновления', menu=database.getAdminMenu(), updates=database.getUpdatesAnnoce())
    return render_template('updates.html', title='Обновления', menu=database.getMenu(), updates=database.getUpdatesAnnoce())

#Deleting update
@app.route('/delupdate/<int:id_update>')
def delupdate_page(id_update):
    db = get_db()
    database = FDataBase(db)
    if 'userlogged' in session:
        if session['userlogged'] == 'admin':
            delupdate = database.delUpdates(id_update)
            if delupdate:
                return redirect(url_for('update_page'))
            return render_template('updates.html', menu=database.getAdminMenu())
    else:
        return redirect(url_for('update_page'))

#Edit post
@app.route('/editupdate/<int:id_update>', methods=['POST', 'GET'])
def editupdate_page(id_update):
    db = get_db()
    database = FDataBase(db)
    if 'userlogged' in session:
        if session['userlogged'] == 'admin':
            if request.method == 'POST':
                if len(request.form['title']) > 3 and len(request.form['text']) > 10:
                    res = database.UpdateUpdate(request.form['title'], request.form['text'], request.form['photo'], id_update)
                    if not res:
                        flash('Ошибка редактирования статьи', category='error')
                    else:
                        flash('Статья успешно редактирована', category='success')
                else:
                    flash('Ошибка редактирования статьи', category='error')
            return render_template('update_edit.html', title='Редактировать обновление', menu=database.getAdminMenu(), update=database.getUpdate(id_update))
    return redirect(url_for('start_page'))


#Deleting to-do-list
@app.route('/deltodo/<int:id_todo>/')
def deltodo(id_todo):
    db = get_db()
    database = FDataBase(db)
    if 'userlogged' in session:
        if session['userlogged'] == 'admin':
            deltodo = database.delTODO(id_todo)
            if deltodo:
                return redirect(url_for('admin_page'))
            return render_template('admin.html', menu=database.getAdminMenu())
    else:
        return redirect(url_for('start_page'))


if __name__ == "__main__":
    app.run(debug=True)

