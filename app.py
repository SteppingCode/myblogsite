# taskkill /f /im python.exe
import math

from flask import render_template, Flask, request, redirect, url_for, session, g, abort, flash, Markup
from config import Config
from database.sqldb import FDataBase
import git, os, sqlite3
from database.photos_db import Photo
from werkzeug.utils import secure_filename

#import time
#
#os.environ["TZ"] = "Europe/Moscow"
#time.tzset()

# папка для сохранения загруженных файлов
UPLOAD_FOLDER = 'static/photos/'
# расширения файлов, которые разрешено загружать
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config.from_object(Config)
app.config.update(dict(DATABASE=os.path.join(app.root_path, 'posts.db'))) #Создается база данных
app.config.update(dict(PHOTOBASE=os.path.join(app.root_path, 'photo.db'))) #Создается база данных
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000

#Соединение с базой данных
def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def connect_photo():
    photo = sqlite3.connect(app.config['PHOTOBASE'])
    photo.row_factory = sqlite3.Row
    return photo

#Получение данных из базы данных
def get_db():
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
        return g.link_db

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#Server updating
@app.route('/update_server', methods=['POST', 'GET'])
def webhook():
    if request.method == 'POST':
        repo = git.Repo('/home/myblogweb/myblogsite')
        origin = repo.remotes.origin
        origin.pull()
        return 'Сайт обновился', 200
    else:
        return 'Возникла ошибка', 400

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Не могу прочитать файл')
        file = request.files['file']
        if file.filename == '':
            flash('Нет выбранного файла')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return '''
    <!doctype html>
    <title>Загрузить новый файл</title>
    <h1>Загрузить новый файл</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    </html>
    '''

#Main page
@app.route('/', methods=['GET', 'POST'])
def start_page():
    db = get_db()
    database = FDataBase(db)
    page = 0
    if database.getAllPostsId() == []:
        return render_template('index.html', title="Главная", menu=database.getMenu(), posts=database.getPostAnnoce(), page=page, MAX_PAGES=0)
    elif database.getAllPostsId()[-1][0] == 1:
        return render_template('index.html', title="Главная", menu=database.getMenu(), posts=database.getPostAnnoce(), page=page, MAX_PAGES=0)
    else:
        return render_template('index.html', title="Главная", menu=database.getMenu(), posts=database.getPostAnnoce(), page=page, MAX_PAGES=1)

#Login
@app.route('/login', methods=['POST', 'GET'])
def login():
    db = get_db()
    database = FDataBase(db)
    if 'userlogged' in session:
        return redirect(url_for('start_page'))
    if request.method == 'POST':
        if len(request.form['username']) > 0 and len(request.form['password']) > 0:
            if database.getData(request.form['username'], request.form['password']):
                session['userlogged'] = database.getData(request.form['username'], request.form['password'])[0][0]
                return redirect(url_for('start_page'))
        if len(request.form['reg_username']) > 0 and len(request.form['reg_password']) > 0:
            if request.form['reg_password'] == request.form['reg_password2']:
                if database.addData(request.form["reg_username"], request.form["reg_password"], request.form['reg_email']):
                    session['userlogged'] = request.form['reg_username']
                    return redirect(url_for('start_page'))
                else:
                    flash('Такой аккаунт уже существует', category='error')
                    return redirect('login')
            else:
                flash("Пароли не совпадают", category='error')
                return redirect(url_for('login'))
        else:
            return redirect(url_for('login'))
    return render_template('login.html', title="Вход", menu=database.getMenu())

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
            return render_template('admin.html', title='Admin Page', menu=database.getMenu(), \
                                   posts=database.getPostAnnoce(), todo=database.getTODO())
    return redirect(url_for('start_page'))

#Create post
@app.route('/post', methods=['POST', 'GET'])
def post():
    db = get_db()
    database = FDataBase(db)
    ph = connect_photo()
    photobase = Photo(ph)
    if 'userlogged' in session:
        if session['userlogged'] == 'admin':
            if request.method == 'POST':
                if len(request.form['name']) > 3 and len(request.form['post']) > 10:
                    res = database.addPost(request.form['name'], request.form['post'])
                    if 'file' not in request.files:
                        flash('Не могу прочитать файл')
                    file = request.files['file']
                    if file.filename == '':
                        flash('Нет выбранного файла')
                    if file and allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                        photobase.PhotoAdd(filename, request.form['name'], str(filename))
                    if not res:
                        return redirect(url_for('post'))
                    else:
                        return redirect(url_for('post'))
            return render_template('post.html', title='Добавить статью', menu=database.getMenu())
    return redirect(url_for('start_page'))

@app.route('/post/page/<int:page>/<int:last_id>')
def post_page(page, last_id):
    db = connect_db()
    database = FDataBase(db)
    MAX_PAGES = (database.getAllPostsId()[-1][0] - 1) // 3
    if ((database.getAllPostsId()[-1][0] - 1) / 3 - MAX_PAGES) == 0:
        if page > MAX_PAGES:
            if MAX_PAGES == 0:
                return redirect(url_for('start_page'))
            return redirect(url_for('post_page', page=MAX_PAGES, last_id=(MAX_PAGES * 3) - 2))
        return render_template('post_page.html', title=f'Страница {page}', menu=database.getMenu(), posts=database.getPostAnnocePages(last_id), page=page, last_id=last_id, MAX_PAGES=MAX_PAGES)
    elif (MAX_PAGES - (database.getAllPostsId()[-1][0] - 1) / 3) != 0:
        MAX_PAGES = math.floor(MAX_PAGES + 1)
        if page > MAX_PAGES:
            return redirect(url_for('post_page', page=MAX_PAGES, last_id=(MAX_PAGES * 3) - 2))
        return render_template('post_page.html', title=f'Страница {page}', menu=database.getMenu(), posts=database.getPostAnnocePages(last_id), page=page, last_id=last_id, MAX_PAGES=MAX_PAGES)
    return render_template('post_page.html', title=f'Страница {page}', menu=database.getMenu(), posts=database.getPostAnnocePages(last_id), page=page, last_id=last_id, MAX_PAGES=MAX_PAGES)

#Edit post
@app.route('/editpost/<int:id_post>', methods=['POST', 'GET'])
def post_edit(id_post):
    db = get_db()
    database = FDataBase(db)
    if 'userlogged' in session:
        if session['userlogged'] == 'admin':
            if request.method == 'POST':
                if len(request.form['title']) > 3 and len(request.form['text']) > 10:
                    res = database.PostUpdate(request.form['title'], request.form['text'], \
                                              request.form['photo'], id_post)
                    if not res:
                        flash('Ошибка редактирования статьи', category='error')
                    else:
                        flash('Статья успешно редактирована', category='success')
                else:
                    flash('Ошибка редактирования статьи', category='error')
            return render_template('post_edit.html', title='Редактировать статью', menu=database.getMenu(), \
                                   post=database.getPost(id_post))
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
    ph = connect_photo()
    photobase = Photo(ph)
    title = database.getPostAnnoce()
    aticle = database.getPostAnnoce()
    post_name = database.getPost(id_post)[0]
    if 'userlogged' in session:
        if session['userlogged'] == 'admin':
            delpost = database.delPost(id_post)
            delphoto = photobase.PhotoDelete(post_name)
            if not title:
                abort(404)
            if delpost and delphoto:
                return redirect(url_for('admin_page'))
            return render_template('admin.html', title='title', menu=database.getMenu(), post=aticle, \
                                   post_title=title)
    else:
        return redirect(url_for('start_page'))

#Post page
@app.route('/posts/<int:id_post>', methods=['POST', 'GET'])
def showPost(id_post):
    db = get_db()
    database = FDataBase(db)
    ph = connect_photo()
    photobase = Photo(ph)
    title, aticle = database.getPost(id_post)
    photo = photobase.getPhoto(title)
    comments = database.getComments(id_post)
    if 'userlogged' in session:
        if photo:
            return render_template('aticle.html', title=title, menu=database.getMenu(), post=Markup(aticle),
                                   post_title=title,
                                   post_image=photo[2], comments=comments, posts=database.getPostAnnoce(),
                                   id_post=id_post)
        if comments:
            if request.method == 'POST':
                if len(request.form['text']) > 3:
                    addcom = database.addComment(session['userlogged'], request.form['text'], id_post)
                    if addcom:
                        return redirect(url_for('showPost', id_post=id_post))
                return render_template('aticle.html', title=title, menu=database.getMenu(), post=Markup(aticle), \
                                       post_title=title, comments=comments, posts=database.getPostAnnoce(), id_post=id_post)
        return render_template('aticle.html', title=title, menu=database.getMenu(), post=Markup(aticle), post_title=title,
                            comments=comments, posts=database.getPostAnnoce(), id_post=id_post)
    if photo:
        return render_template('aticle.html', title=title, menu=database.getMenu(), post=Markup(aticle),
                               post_title=title,
                               post_image=photo[2], comments=comments, posts=database.getPostAnnoce(), id_post=id_post)
    return render_template('aticle.html', title=title, menu=database.getMenu(), post=Markup(aticle), \
                           post_title=title, posts=database.getPostAnnoce(), comments=comments, id_post=id_post)

@app.route('/display_image_by_name/<post_name>', methods=['POST', 'GET'])
def display_image_by_name(post_name):
    db = get_db()
    ph = connect_photo()
    photobase = Photo(ph)
    filename = photobase.getPhoto(post_name)[3]
    return redirect(url_for('static', filename='photos/' + filename), code=301)

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
            return render_template('aticle.html', menu=database.getMenu())
    else:
        return redirect(url_for('start_page'))

#Updates page
@app.route('/updates', methods=['POST', 'GET'])
def updates():
    db = get_db()
    database = FDataBase(db)
    page = 0
    if 'userlogged' in session:
        if session['userlogged'] == 'admin':
            if request.method == 'POST':
                addupd = database.addUpdates(request.form['title'], request.form['text'], request.form['photo'])
                if addupd:
                    return redirect(url_for('updates'))
                else:
                    return redirect(url_for('updates'))
            return render_template('updates.html', title='Обновления', menu=database.getMenu(), \
                                   updates=database.getUpdatesAnnoce(), page=page)
        return render_template('updates.html', title='Обновления', menu=database.getMenu(), \
                               updates=database.getUpdatesAnnoce(), page=page)
    return render_template('updates.html', title='Обновления', menu=database.getMenu(), \
                           updates=database.getUpdatesAnnoce(), page=page)

#Update page
@app.route('/updates/page/<int:page>/<int:last_id>')
def update_page(page, last_id):
    db = connect_db()
    database = FDataBase(db)
    MAX_PAGES = (database.getAllUpdatesId()[-1][0] // 3) - 1
    if ((((database.getAllUpdatesId()[-1][0]) / 3) - 1) - MAX_PAGES) == 0:
        if page > MAX_PAGES:
            return redirect(url_for('update_page', page=MAX_PAGES, last_id=(MAX_PAGES * 3)))
        return render_template('update_page.html', title=f'Страница {page}', menu=database.getMenu(), posts=database.getUpdateAnnocePages(last_id), page=page, last_id=last_id, MAX_PAGES=MAX_PAGES)
    elif (MAX_PAGES - ((database.getAllUpdatesId()[-1][0]) / 3) - 1) != 0:
        MAX_PAGES = math.floor(MAX_PAGES + 1)
        if page > MAX_PAGES:
            return redirect(url_for('update_page', page=MAX_PAGES, last_id=(MAX_PAGES * 3)))
        return render_template('update_page.html', title=f'Страница {page}', menu=database.getMenu(), posts=database.getUpdateAnnocePages(last_id), page=page, last_id=last_id, MAX_PAGES=MAX_PAGES)
    return render_template('update_page.html', title=f'Страница {page}', menu=database.getMenu(), posts=database.getUpdateAnnocePages(last_id), page=page, last_id=last_id, MAX_PAGES=MAX_PAGES)

#    {% else %}
#        <p><a class="image like" href="{{url_for('addlike', id_update=id_update)}}" title="Мне нравится"><img src="https://cdn-icons-png.flaticon.com/512/633/633759.png" width="125px" height="50px"></a></p>
#        <p><a class="image dislike" href="{{url_for('addlike', id_update=id_update)}}" title="Мне не нравится"><img src="https://cdn-icons-png.flaticon.com/512/633/633758.png" width="125px" height="50px"></a></p>

@app.route('/profile/<name>', methods=['GET', 'POST'])
def profile_page(name):
    db = get_db()
    database = FDataBase(db)
    profile = database.getProfile(name)
    if 'userlogged' in session:
        if profile:
            return render_template('profile.html', menu=database.getMenu(), title=name, prof=profile)
        return render_template('profile.html', menu=database.getMenu(), title='Профиль не найден')
    return redirect(url_for('start_page'))

@app.route('/reg_profile', methods=['GET', 'POST'])
def profile_reg():
    db = get_db()
    database = FDataBase(db)
    if 'userlogged' in session:
        if request.method == 'POST':
            if database.addProfile(session['userlogged'], request.form["name"], request.form["age"], \
                                   request.form["game"]):
                return redirect(url_for('profile_page', name=session['userlogged']))
            else:
                flash('Некорректный логин', category='error')
                return redirect('profile_reg')
        return render_template('profile_reg.html', title='Регистрация профиля', menu=database.getMenu())
    return redirect(url_for('start_page'))

#Like update
@app.route('/like/<int:id_update>/')
def update_like(id_update):
    db = get_db()
    database = FDataBase(db)
    addlike = database.likeUpdate(id_update)
    if 'userlogged' in session:
        if addlike:
            return redirect(url_for('showUpdate', id_update=id_update))
        return render_template('update_page.html', menu=database.getMenu(), id_update=id_update)
    else:
        return redirect(url_for('update_page'))

#Dislike update
@app.route('/dislike/<int:id_update>/')
def update_dislike(id_update):
    db = get_db()
    database = FDataBase(db)
    adddislike = database.dislikeUpdate(id_update)
    if 'userlogged' in session:
        if adddislike:
            return redirect(url_for('showUpdate', id_update=id_update))
        return render_template('update_page.html', menu=database.getMenu(), id_update=id_update)
    else:
        return redirect(url_for('update_page'))

#Edit update
@app.route('/editupdate/<int:id_update>', methods=['POST', 'GET'])
def editupdate_page(id_update):
    db = get_db()
    database = FDataBase(db)
    if 'userlogged' in session:
        if session['userlogged'] == 'admin':
            if request.method == 'POST':
                if len(request.form['title']) > 3 and len(request.form['text']) > 10:
                    res = database.UpdateUpdate(request.form['title'], request.form['text'], \
                                                request.form['photo'], id_update)
                    if not res:
                        flash('Ошибка редактирования обновления', category='error')
                    else:
                        flash('Обновление успешно редактировано', category='success')
                else:
                    flash('Ошибка редактирования обновления', category='error')
            return render_template('update_edit.html', title='Редактировать обновление', menu=database.getMenu(), \
                                   update=database.getUpdate(id_update))
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
            return render_template('updates.html', menu=database.getMenu())
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
            return render_template('admin.html', menu=database.getMenu())
    else:
        return redirect(url_for('start_page'))

@app.route('/settings/', methods=['POST', 'GET'])
def settings():
    db = connect_db()
    database = FDataBase(db)
    if 'userlogged' in session:
        if request.method == 'POST':
            if len(request.form['cur_psw']) > 0 and len(request.form['psw']) > 0 and len(request.form['psw2']) > 0:
                if database.getData(session['userlogged'], request.form['cur_psw']):
                    if request.form['psw'] == request.form['psw2']:
                        if database.UpdateUserPass(session['userlogged'], request.form['psw']):
                            flash('Password was successfully changed', category='success')
                            return redirect(url_for('settings'))
                        else:
                            flash('Error updating password in data base', category='error')
                            return redirect(url_for('settings'))
                    else:
                        flash('Passwords are not match', category='error')
                        return redirect(url_for('settings'))
                else:
                    flash('Incorrect password', category='error')
                    return redirect(url_for('settings'))
            if database.getEmail(session['userlogged'])[0] != '':
                if len(request.form['email_upd']) > 0:
                    if database.UpdateEmail(request.form['email_upd'], session['userlogged']):
                        flash('Email was successfully changed', category='success')
                        return redirect(url_for('settings'))
                    else:
                        flash('Error', category='error')
                        return redirect(url_for('settings'))
            if len(request.form['email_set']) > 0:
                if database.UpdateEmail(request.form['email_set'], session['userlogged']):
                    flash('Email was successfully changed', category='success')
                    return redirect(url_for('settings'))
                else:
                    flash('Error', category='error')
                    return redirect(url_for('settings'))
        return render_template('settings.html', menu=database.getMenu(), title='Настройки', email=database.getEmail(session['userlogged'])[0])
    return redirect(url_for('start_page'))

#Site start
if __name__ == "__main__":
    app.run(debug=True)