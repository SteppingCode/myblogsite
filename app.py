from flask import render_template, Flask, request, redirect, url_for, session, g, abort, flash
from config import Config
from database.sqldb import FDataBase
import git, os, sqlite3

#import time
#
#os.environ["TZ"] = "Europe/Moscow"
#time.tzset()

app = Flask(__name__)
app.config.from_object(Config)
app.config.update(dict(DATABASE=os.path.join(app.root_path,'../posts.db'))) #Создается база данных

#Соединение с базой данных
def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

#Получение данных из базы данных
def get_db():
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
        return g.link_db

#Redirect to start_page
@app.route('/', methods=['GET', 'POST'])
def first_page():
    return redirect(url_for('start_page'))

#Git update (doesnt work)
@app.route('/update_server', methods=['POST', 'GET'])
def webhook():
    if request.method == 'POST':
        repo = git.Repo('/home/myblogweb/myblogsite')
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
            return render_template('index.html', title="Главная", menu=database.getAdminMenu())
        return render_template('index.html', title="Главная", menu=database.getMenu())
    return render_template('index.html', title="Главная", menu=database.getUnregMenu())

#Posts page
@app.route('/allposts', methods=['GET', 'POST'])
def allposts():
    db = get_db()
    database = FDataBase(db)
    if 'userlogged' in session:
        if session['userlogged'] == 'admin':
            return render_template('allposts.html', title="Посты", menu=database.getAdminMenu(), posts=database.getPostAnnoce())
        return render_template('allposts.html', title="Посты", menu=database.getMenu(), posts=database.getPostAnnoce())
    return render_template('allposts.html', title="Посты", menu=database.getUnregMenu(), posts=database.getPostAnnoce())

#Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    db = get_db()
    database = FDataBase(db)
    if 'userlogged' in session:
        return redirect(url_for('start_page', username=session['userlogged']))
    if request.method == 'POST':
        if request.form['password'] == request.form['password2']:
            if database.addData(request.form["username"], request.form["password"]):
                session['userlogged'] = request.form['username']
                return redirect(url_for('start_page', username=session['userlogged']))
            else:
                flash('Некорректный логин', category='error')
                return redirect('register')
        else:
            flash("Пароли не совпадают", category='error')
            return redirect(url_for('register'))
    return render_template('register.html', title='Регистрация')

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

#Create post
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
            return render_template('post.html', title='Добавить статью', menu=database.getAdminMenu())
    return redirect(url_for('start_page'))

#Edit post
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
            return render_template('post_edit.html', title='Редактировать статью', menu=database.getAdminMenu(), post=database.getPost(id_post))
    return redirect(url_for('start_page'))

#Quit
@app.route('/quit', methods=['GET', 'POST'])
def quit_login():
    if 'userlogged' in session:
        return redirect(url_for('start_page')), session.clear()
    else:
        return redirect(url_for('start_page'))


#Deleting post
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

#Post page
@app.route('/posts/<int:id_post>', methods=['POST', 'GET'])
def showPost(id_post):
    db = get_db()
    database = FDataBase(db)
    title, aticle, photo = database.getPost(id_post)
    comments = database.getComments(id_post)
    if comments:
        if 'userlogged' in session:
            if session['userlogged'] == 'admin':
                return render_template('aticle.html', title=title, menu=database.getAdminMenu(), post=aticle, post_title=title, post_image=photo, comments=comments)
            return render_template('aticle.html', title=title, menu=database.getMenu(), post=aticle, post_title=title, post_image=photo, comments=comments)
        if request.method == 'POST':
            if len(request.form['text']) > 3:
                addcom = database.addComment(session['userlogged'], request.form['text'], id_post)
                if addcom:
                    flash('Комментарий добавлен', category='success')
                    return redirect(url_for('showPost', id_post=id_post))
                else:
                    flash('Ошибка добавления комментария', category='error')
            else:
                flash('Ошибка добавления комментария', category='error')
        return render_template('aticle.html', title=title, menu=database.getUnregMenu(), post=aticle, post_title=title, post_image=photo, comments=comments)
    if request.method == 'POST':
        if len(request.form['text']) > 3:
            addcom = database.addComment(session['userlogged'], request.form['text'], id_post)
            if addcom:
                flash('Комментарий добавлен', category='success')
                return redirect(url_for('showPost', id_post=id_post))
            else:
                flash('Ошибка добавления комментария', category='error')
        else:
            flash('Ошибка добавления комментария', category='error')
        return render_template('aticle.html', title=title, menu=database.getMenu(), post=aticle, post_title=title, post_image=photo, comments=comments)
    if 'userlogged' in session:
        if session['userlogged'] == 'admin':
            return render_template('aticle.html', title=title, menu=database.getAdminMenu(), post=aticle,
                                   post_title=title, post_image=photo, comments=comments)
        return render_template('aticle.html', title=title, menu=database.getMenu(), post=aticle, post_title=title,
                               post_image=photo, comments=comments)
    return render_template('aticle.html', title=title, menu=database.getUnregMenu(), post=aticle, post_title=title, post_image=photo)

#Deleting comment
@app.route('/delcom/<int:id_post>/<int:id_com>')
def delcom_page(id_post, id_com):
    db = get_db()
    database = FDataBase(db)
    if 'userlogged' in session:
        if session['userlogged'] == 'admin':
            delcom = database.delComment(id_post, id_com)
            if delcom:
                return redirect(url_for('showPost', id_post=id_post))
            return render_template('aticle.html', menu=database.getAdminMenu())
    else:
        return redirect(url_for('start_page'))

#Updates page
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

#Update page
@app.route('/update/<int:id_update>', methods=['POST', 'GET'])
def showUpdate(id_update):
    db = get_db()
    database = FDataBase(db)
    title, aticle, photo = database.getUpdate(id_update)
    likes = database.getLikes(id_update)
    if likes:
        return render_template('update_page.html', title=title, menu=database.getMenu(), update_text=aticle, update_title=title, update_image=photo, likes=likes, id_update=id_update)
    else:
        return render_template('update_page.html', title=title, menu=database.getMenu(), update_text=aticle, update_title=title, update_image=photo, likes=likes, id_update=id_update), database.addLike(id_update)
    return render_template('update_page.html', title=title, menu=database.getMenu(), update_text=aticle, update_title=title, update_image=photo, likes=likes, id_update=id_update)

#    {% else %}
#        <p><a class="image like" href="{{url_for('addlike', id_update=id_update)}}" title="Мне нравится"><img src="https://cdn-icons-png.flaticon.com/512/633/633759.png" width="125px" height="50px"></a></p>
#        <p><a class="image dislike" href="{{url_for('addlike', id_update=id_update)}}" title="Мне не нравится"><img src="https://cdn-icons-png.flaticon.com/512/633/633758.png" width="125px" height="50px"></a></p>

#Like update
@app.route('/like/<int:id_update>/')
def update_like(id_update):
    db = get_db()
    database = FDataBase(db)
    addlike = database.likeUpdate(id_update)
    if 'userlogged' in session:
        if addlike:
            return redirect(url_for('showUpdate', id_update=id_update))
        if session['userlogged'] == 'admin':
            return render_template('update_page.html', menu=database.getAdminMenu(), id_update=id_update)
        return render_template('update_page.html', menu=database.getMenu(), id_update=id_update)
    else:
        return redirect(url_for('update_page'))
    return render_template('update_page.html', menu=database.getMenu(), id_update=id_update)

#Dislike update
@app.route('/dislike/<int:id_update>/')
def update_dislike(id_update):
    db = get_db()
    database = FDataBase(db)
    adddislike = database.dislikeUpdate(id_update)
    if 'userlogged' in session:
        if adddislike:
            return redirect(url_for('showUpdate', id_update=id_update))
        if session['userlogged'] == 'admin':
            return render_template('update_page.html', menu=database.getAdminMenu(), id_update=id_update)
        return render_template('update_page.html', menu=database.getMenu(), id_update=id_update)
    else:
        return redirect(url_for('update_page'))
    return render_template('update_page.html', menu=database.getMenu(), id_update=id_update)

#Edit update
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
                        flash('Ошибка редактирования обновления', category='error')
                    else:
                        flash('Обновление успешно редактировано', category='success')
                else:
                    flash('Ошибка редактирования обновления', category='error')
            return render_template('update_edit.html', title='Редактировать обновление', menu=database.getAdminMenu(), update=database.getUpdate(id_update))
    return redirect(url_for('start_page'))

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

#Site start
if __name__ == "__main__":
    app.run(debug=True)