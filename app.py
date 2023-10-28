# taskkill /f /im python.exe
from flask import render_template, Flask, request, redirect, url_for, session, g, abort, flash, Markup
from config import Config
from database.sqldb import FDataBase
import git, os, sqlite3, math
from database.photos_db import Photo
from werkzeug.utils import secure_filename

# папка для сохранения загруженных файлов
UPLOAD_FOLDER = 'static/photos/'
# расширения файлов, которые разрешено загружать
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
ALLOWED_EXTENSIONS_AVATAR = {'png'}

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


#Main page
@app.route('/', methods=['GET', 'POST'])
def start_page():
    db = get_db()
    database = FDataBase(db)
    page = 0
    if database.getAllPostsId() == []:
        if 'userlogged' in session:
            filename = str(session['userlogged']) + '.png'
            status = database.getStatus(session['userlogged'])[0]
            nick = database.getProfile(session['userlogged'])[0]['nick']
            for i in os.listdir(f'{app.root_path + "/static/avatars/"}'):
                if filename in i:
                    return render_template('index.html', title="Главная", menu=database.getMenu(), posts=database.getPostAnnoce(), page=page, MAX_PAGES=0, ava=open(f'{app.root_path + "/static/avatars/" + filename}', 'rb'), status=status, nick=nick)
            else:
                return render_template('index.html', title="Главная", menu=database.getMenu(), posts=database.getPostAnnoce(), page=page, MAX_PAGES=0, ava_empty=open(f'{app.root_path + "/static/avatars/static.png"}', 'rb'), status=status, nick=nick)
        return render_template('index.html', title="Главная", menu=database.getMenu(), posts=database.getPostAnnoce(), page=page, MAX_PAGES=0)
    elif database.getAllPostsId()[-1][0] == 1:
        if 'userlogged' in session:
            filename = str(session['userlogged']) + '.png'
            status = database.getStatus(session['userlogged'])[0]
            nick = database.getProfile(session['userlogged'])[0]['nick']
            for i in os.listdir(f'{app.root_path + "/static/avatars/"}'):
                if filename in i:
                    return render_template('index.html', title="Главная", menu=database.getMenu(), posts=database.getPostAnnoce(), page=page, MAX_PAGES=0, ava=open(f'{app.root_path + "/static/avatars/" + filename}', 'rb'), status=status, nick=nick)
            else:
                return render_template('index.html', title="Главная", menu=database.getMenu(), posts=database.getPostAnnoce(), page=page, MAX_PAGES=0, ava_empty=open(f'{app.root_path + "/static/avatars/static.png"}', 'rb'), status=status, nick=nick)
        else:
            return render_template('index.html', title="Главная", menu=database.getMenu(), posts=database.getPostAnnoce(), page=page, MAX_PAGES=0)
    else:
        if 'userlogged' in session:
            filename = str(session['userlogged']) + '.png'
            status = database.getStatus(session['userlogged'])[0]
            nick = database.getProfile(session['userlogged'])[0]['nick']
            for i in os.listdir(f'{app.root_path + "/static/avatars/"}'):
                if filename in i:
                    return render_template('index.html', title="Главная", menu=database.getMenu(), posts=database.getPostAnnoce(), page=page, MAX_PAGES=1, ava=open(f'{app.root_path + "/static/avatars/" + filename}', 'rb'), status=status, nick=nick)
            else:
                return render_template('index.html', title="Главная", menu=database.getMenu(), posts=database.getPostAnnoce(), page=page, MAX_PAGES=1, ava_empty=open(f'{app.root_path + "/static/avatars/static.png"}', 'rb'), status=status, nick=nick)
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
    return render_template('login.html', title="Вход", menu=database.getMenu())

@app.route('/register', methods=['POST', 'GET'])
def register():
    db = get_db()
    database = FDataBase(db)
    if 'userlogged' in session:
        return redirect(url_for('start_page'))
    if request.method == 'POST':
        if len(request.form['reg_username']) > 0 and len(request.form['reg_password']) > 0 and len(request.form['reg_email']) > 0:
            if request.form['reg_password'] == request.form['reg_password2']:
                if len(request.form['reg_nick']) > 0:
                    if database.addData(request.form["reg_username"], request.form["reg_password"], request.form['reg_email'],''):
                        session['userlogged'] = request.form['reg_username']
                        if 'file' not in request.files:
                            flash('Can not read the file', category='error')
                        file = request.files['file']
                        if file and allowed_file(file.filename):
                            filename = str(session['userlogged']) + '.png'
                            file.save(os.path.join(f'{app.root_path + "/static/avatars/" + filename}'))
                        if database.addProfile(request.form['reg_nick'], '', '', '', session['userlogged']):
                            return redirect(url_for('start_page'))
    return redirect(url_for('login'))

#Admin Page
@app.route('/admin', methods=['POST', 'GET'])
def admin_page():
    db = get_db()
    database = FDataBase(db)
    if 'userlogged' in session:
        filename = str(session['userlogged']) + '.png'
        status = database.getStatus(session['userlogged'])[0]
        nick = database.getProfile(session['userlogged'])[0]['nick']
        if status == 'admin':
            if request.method == 'POST':
                addtodo = database.addTODO(request.form['text'])
                if addtodo:
                    return redirect(url_for('admin_page'))
                else:
                    return redirect(url_for('admin_page'))
            for i in os.listdir(f'{app.root_path + "/static/avatars/"}'):
                if filename in i:
                    return render_template('admin.html', title='Admin Page', menu=database.getMenu(), posts=database.getAllposts(), todo=database.getTODO(), ava=open(f'{app.root_path + "/static/avatars/" + filename}', 'rb'), status=status, nick=nick)
            else:
                return render_template('admin.html', title='Admin Page', menu=database.getMenu(), posts=database.getAllposts(), todo=database.getTODO(), ava_empty=open(f'{app.root_path + "/static/avatars/static.png"}', 'rb'), status=status, nick=nick)
    return redirect(url_for('start_page'))

#Create post
@app.route('/post', methods=['POST', 'GET'])
def post():
    db = get_db()
    database = FDataBase(db)
    ph = connect_photo()
    photobase = Photo(ph)
    if 'userlogged' in session:
        filename = str(session['userlogged']) + '.png'
        status = database.getStatus(session['userlogged'])[0]
        nick = database.getProfile(session['userlogged'])[0]['nick']
        if status == 'admin':
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
            for i in os.listdir(f'{app.root_path + "/static/avatars/"}'):
                if filename in i:
                    return render_template('post.html', title='Добавить статью', menu=database.getMenu(), ava=open(f'{app.root_path + "/static/avatars/" + filename}', 'rb'), status=status, nick=nick)
            else:
                return render_template('post.html', title='Добавить статью', menu=database.getMenu(), ava_empty=open(f'{app.root_path + "/static/avatars/static.png"}', 'rb'), status=status, nick=nick)
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
        if 'userlogged' in session:
            filename = str(session['userlogged']) + '.png'
            status = database.getStatus(session['userlogged'])[0]
            nick = database.getProfile(session['userlogged'])[0]['nick']
            for i in os.listdir(f'{app.root_path + "/static/avatars/"}'):
                if filename in i:
                    return render_template('post_page.html', title=f'Страница {page}', menu=database.getMenu(), posts=database.getPostAnnocePages(last_id), page=page, last_id=last_id, MAX_PAGES=MAX_PAGES, ava=open(f'{app.root_path + "/static/avatars/" + filename}', 'rb'), status=status, nick=nick)
            else:
                return render_template('post_page.html', title=f'Страница {page}', menu=database.getMenu(), posts=database.getPostAnnocePages(last_id), page=page, last_id=last_id, MAX_PAGES=MAX_PAGES, ava_empty=open(f'{app.root_path + "/static/avatars/static.png"}', 'rb'), status=status, nick=nick)
        return render_template('post_page.html', title=f'Страница {page}', menu=database.getMenu(), posts=database.getPostAnnocePages(last_id), page=page, last_id=last_id, MAX_PAGES=MAX_PAGES)
    elif (MAX_PAGES - (database.getAllPostsId()[-1][0] - 1) / 3) != 0:
        MAX_PAGES = math.floor(MAX_PAGES + 1)
        if page > MAX_PAGES:
            return redirect(url_for('post_page', page=MAX_PAGES, last_id=(MAX_PAGES * 3) - 2))
        if 'userlogged' in session:
            filename = str(session['userlogged']) + '.png'
            status = database.getStatus(session['userlogged'])[0]
            nick = database.getProfile(session['userlogged'])[0]['nick']
            for i in os.listdir(f'{app.root_path + "/static/avatars/"}'):
                if filename in i:
                    return render_template('post_page.html', title=f'Страница {page}', menu=database.getMenu(), posts=database.getPostAnnocePages(last_id), page=page, last_id=last_id, MAX_PAGES=MAX_PAGES, ava=open(f'{app.root_path + "/static/avatars/" + filename}', 'rb'), status=status, nick=nick)
            else:
                return render_template('post_page.html', title=f'Страница {page}', menu=database.getMenu(), posts=database.getPostAnnocePages(last_id), page=page, last_id=last_id, MAX_PAGES=MAX_PAGES, ava_empty=open(f'{app.root_path + "/static/avatars/static.png"}', 'rb'), status=status, nick=nick)
        return render_template('post_page.html', title=f'Страница {page}', menu=database.getMenu(), posts=database.getPostAnnocePages(last_id), page=page, last_id=last_id, MAX_PAGES=MAX_PAGES)
    return render_template('post_page.html', title=f'Страница {page}', menu=database.getMenu(), posts=database.getPostAnnocePages(last_id), page=page, last_id=last_id, MAX_PAGES=MAX_PAGES)

#Edit post
@app.route('/editpost/<int:id_post>', methods=['POST', 'GET'])
def post_edit(id_post):
    db = get_db()
    database = FDataBase(db)
    if 'userlogged' in session:
        filename = str(session['userlogged']) + '.png'
        status = database.getStatus(session['userlogged'])[0]
        nick = database.getProfile(session['userlogged'])[0]['nick']
        if status == 'admin':
            if request.method == 'POST':
                if len(request.form['title']) > 3 and len(request.form['text']) > 10:
                    res = database.PostUpdate(request.form['title'], request.form['text'], request.form['photo'], id_post)
                    if not res:
                        return redirect(url_for('post_edit', id_post=id_post))
                    else:
                        return redirect(url_for('start_page'))
                else:
                    return redirect(url_for('post_edit', id_post=id_post))
            for i in os.listdir(f'{app.root_path + "/static/avatars/"}'):
                if filename in i:
                    return render_template('post_edit.html', title='Редактировать статью', menu=database.getMenu(), post=database.getPost(id_post), ava=open(f'{app.root_path + "/static/avatars/" + filename}', 'rb'), status=status, nick=nick)
            else:
                return render_template('post_edit.html', title='Редактировать статью', menu=database.getMenu(), post=database.getPost(id_post), ava_empty=open(f'{app.root_path + "/static/avatars/static.png"}', 'rb'), status=status, nick=nick)
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
        status = database.getStatus(session['userlogged'])[0]
        nick = database.getProfile(session['userlogged'])[0]['nick']
        if status == 'admin':
            delpost = database.delPost(id_post)
            delphoto = photobase.PhotoDelete(post_name)
            if not title:
                abort(404)
            if delpost and delphoto:
                return redirect(url_for('admin_page'))
            return render_template('admin.html', title='title', menu=database.getMenu(), post=aticle, post_title=title, status=status)
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
        filename = str(session['userlogged']) + '.png'
        status = database.getStatus(session['userlogged'])[0]
        nick = database.getProfile(session['userlogged'])[0]['nick']
        if photo:
            for i in os.listdir(f'{app.root_path + "/static/avatars/"}'):
                if filename in i:
                    return render_template('aticle.html', title=title, menu=database.getMenu(), post=Markup(aticle), post_title=title, post_image=photo[2], comments=comments, posts=database.getPostAnnoce(), id_post=id_post, ava=open(f'{app.root_path + "/static/avatars/" + filename}', 'rb'), status=status, nick=nick)
            else:
                return render_template('aticle.html', title=title, menu=database.getMenu(), post=Markup(aticle), post_title=title, post_image=photo[2], comments=comments, posts=database.getPostAnnoce(), id_post=id_post, ava_empty=open(f'{app.root_path + "/static/avatars/static.png"}', 'rb'), status=status, nick=nick)
        if comments:
            if request.method == 'POST':
                if len(request.form['text']) > 3:
                    addcom = database.addComment(session['userlogged'], request.form['text'], id_post)
                    if addcom:
                        return redirect(url_for('showPost', id_post=id_post))
                    for i in os.listdir('static/avatars/'):
                        if filename in i:
                            return render_template('aticle.html', title=title, menu=database.getMenu(), post=Markup(aticle), post_title=title, comments=comments, posts=database.getPostAnnoce(), id_post=id_post, ava=open(f'static/avatars/{filename}', 'rb'), status=status, nick=nick)
                    else:
                        return render_template('aticle.html', title=title, menu=database.getMenu(), post=Markup(aticle), post_title=title, comments=comments, posts=database.getPostAnnoce(), id_post=id_post, ava_empty=open(f'static/avatars/static.png', 'rb'), status=status, nick=nick)
                return render_template('aticle.html', title=title, menu=database.getMenu(), post=Markup(aticle), post_title=title, comments=comments, posts=database.getPostAnnoce(), id_post=id_post, status=status)
        for i in os.listdir(f'{app.root_path + "/static/avatars/"}'):
            if filename in i:
                return render_template('aticle.html', title=title, menu=database.getMenu(), post=Markup(aticle), post_title=title, comments=comments, posts=database.getPostAnnoce(), id_post=id_post, ava=open(f'{app.root_path + "/static/avatars/" + filename}', 'rb'), status=status, nick=nick)
        else:
            return render_template('aticle.html', title=title, menu=database.getMenu(), post=Markup(aticle), post_title=title, comments=comments, posts=database.getPostAnnoce(), id_post=id_post, ava_empty=open(f'{app.root_path + "/static/avatars/static.png"}', 'rb'), status=status, nick=nick)
    if photo:
        return render_template('aticle.html', title=title, menu=database.getMenu(), post=Markup(aticle), post_title=title, post_image=photo[2], comments=comments, posts=database.getPostAnnoce(), id_post=id_post)
    return render_template('aticle.html', title=title, menu=database.getMenu(), post=Markup(aticle), post_title=title, posts=database.getPostAnnoce(), comments=comments, id_post=id_post)

@app.route('/display_image_by_name/<post_name>', methods=['POST', 'GET'])
def display_image_by_name(post_name):
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
        status = database.getStatus(session['userlogged'])[0]
        if status == 'admin':
            delcom = database.delComment(id_post, id_com)
            if delcom:
                return redirect(url_for('showPost', id_post=id_post))
            else:
                return redirect(url_for('showPost', id_post=id_post))
    else:
        return redirect(url_for('start_page'))

#Deleting to-do-list
@app.route('/deltodo/<int:id_todo>/')
def deltodo(id_todo):
    db = get_db()
    database = FDataBase(db)
    if 'userlogged' in session:
        status = database.getStatus(session['userlogged'])[0]
        if status == 'admin':
            deltodo = database.delTODO(id_todo)
            if deltodo:
                return redirect(url_for('admin_page'))
            else:
                flash('Error', category='error')
                return redirect(url_for('admin_page'))
    else:
        return redirect(url_for('start_page'))

@app.route('/settings/', methods=['POST', 'GET'])
def settings():
    db = connect_db()
    database = FDataBase(db)
    if 'userlogged' in session:
        filename = str(session['userlogged']) + '.png'
        status = database.getStatus(session['userlogged'])[0]
        nick = database.getProfile(session['userlogged'])[0]['nick']
        for i in os.listdir(f'{app.root_path + "/static/avatars/"}'):
            if filename in i:
                if database.getProfile(session['userlogged']):
                    return render_template('settings.html', menu=database.getMenu(), title='Настройки', email=database.getEmail(session['userlogged'])[0], ava=open(f'{app.root_path + "/static/avatars/" + filename}', 'rb'), prof=database.getProfile(session['userlogged']), status=status, nick=nick)
                return render_template('settings.html', menu=database.getMenu(), title='Настройки', email=database.getEmail(session['userlogged'])[0], ava=open(f'{app.root_path + "/static/avatars/" + filename}', 'rb'), status=status)
        else:
            if database.getProfile(session['userlogged']):
                return render_template('settings.html', menu=database.getMenu(), title='Настройки', email=database.getEmail(session['userlogged'])[0], ava_empty=open(f'{app.root_path + "/static/avatars/static.png"}', 'rb'), prof=database.getProfile(session['userlogged']), status=status, nick=nick)
            return render_template('settings.html', menu=database.getMenu(), title='Настройки', email=database.getEmail(session['userlogged'])[0], ava_empty=open(f'{app.root_path + "/static/avatars/static.png"}', 'rb'), status=status)
    return redirect(url_for('start_page'))

@app.route('/prfoile', methods=['POST', 'GET'])
def profile():
    db = connect_db()
    database = FDataBase(db)
    if 'userlogged' in session:
        if request.method == 'POST':
            if database.getProfile(session['userlogged']):
                if database.UpdateProfile(request.form['nick'], request.form['name'],  request.form['age'], request.form['about'], session['userlogged']):
                    flash('Profile has been updated', category='success')
                    return redirect(url_for('settings'))
                else:
                    flash('This nickname is already exist', category='error')
                    return redirect(url_for('settings'))
            else:
                if database.addProfile(request.form['nick_reg'], request.form['name_reg'],  request.form['age_reg'], request.form['about_reg'], session['userlogged']):
                    flash('Profile has been updated', category='success')
                    return redirect(url_for('settings'))
                else:
                    flash('Error', category='error')
                    return redirect(url_for('settings'))
        return redirect(url_for('settings'))
    return redirect(url_for('start_page'))

@app.route('/password', methods=['POST', 'GET'])
def password():
    db = connect_db()
    database = FDataBase(db)
    if 'userlogged' in session:
        if request.method == 'POST':
            if len(request.form['cur_psw']) > 0 and len(request.form['psw']) > 0 and len(request.form['psw2']) > 0:
                if database.getData(session['userlogged'], request.form['cur_psw']):
                    if request.form['psw'] == request.form['psw2']:
                        if database.UpdateUserPass(session['userlogged'], request.form['psw']):
                            print('dsf')
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
            else:
                flash('You did not write password', category='error')
                return redirect(url_for('settings'))
    return redirect(url_for('start_page'))

@app.route('/email', methods=['POST', 'GET'])
def email():
    db = connect_db()
    database = FDataBase(db)
    if 'userlogged' in session:
        if request.method == 'POST':
            if len(request.form['email']) > 0:
                if database.UpdateEmail(request.form['email'], session['userlogged']):
                    flash('Email was successfully changed', category='success')
                    return redirect(url_for('settings'))
                else:
                    flash('Error', category='error')
                    return redirect(url_for('settings'))
            return redirect(url_for('settings'))
    return redirect(url_for('start_page'))

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if 'userlogged' in session:
        if request.method == 'POST':
            if 'file' not in request.files:
                flash('Can not read the file', category='error')
            file = request.files['file']
            if file.filename == '':
                flash('No choosen file', category='error')
            if file and allowed_file(file.filename):
                filename = str(session['userlogged']) + '.png'
                file.save(os.path.join(f'{app.root_path + "/static/avatars/" + filename}'))
        return redirect(url_for('settings'))
    return redirect(url_for('start_page'))

@app.route('/userava/<username>', methods=['POST', 'GET'])
def userava(username):
    filename = str(username) + ".png"
    return redirect(url_for('static', filename='avatars/' + filename), code=301)

@app.route('/userava/delete/<filename>')
def userava_delete(filename):
    filename = str(session['userlogged']) + '.png'
    for i in os.listdir(f'{app.root_path + "/static/avatars/"}'):
        if filename in i:
            return redirect(url_for('settings')), os.remove(f'{app.root_path + "/static/avatars/" + filename}')
    else:
        flash("No avatar", category='error')
        return redirect(url_for('settings'))

#Site start
if __name__ == "__main__":
    app.run(debug=True)