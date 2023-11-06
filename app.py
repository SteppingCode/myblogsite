# taskkill /f /im python.exe

# Imports
import git, os, sqlite3, math, smtplib, random, secrets

from datetime import timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import render_template, Flask, request, redirect, url_for, session, g, abort, flash, Markup
from config import Config
from database.sqldb import FDataBase
from database.photos_db import Photo
from werkzeug.utils import secure_filename

# Upload folder
UPLOAD_FOLDER = 'static/photos/'
# Allowed extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config.from_object(Config)
# Creating main DataBase
app.config.update(dict(DATABASE=os.path.join(app.root_path, 'posts.db')))
# Creating DataBase for photos
app.config.update(dict(PHOTOBASE=os.path.join(app.root_path, 'photo.db')))
app.permanent_session_lifetime = timedelta(days=365)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000

# Connecting main DataBase
def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

# Connecting DataBase for photos
def connect_photo():
    photo = sqlite3.connect(app.config['PHOTOBASE'])
    photo.row_factory = sqlite3.Row
    return photo

# Get data from DataBase
def get_db():
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
        return g.link_db

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

code = None

# Confirm code generator
def generate_code():
    digits = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    random.shuffle(digits)
    digit = random.randint(1, 9)
    code = int(''.join(digits)) * digit
    return code

# Server updating
@app.route('/update_server', methods=['POST', 'GET'])
def webhook():
    if request.method == 'POST':
        repo = git.Repo('/home/myblogweb/myblogsite')
        origin = repo.remotes.origin
        origin.pull()
        return 'Сайт обновился', 200
    else:
        return 'Возникла ошибка', 400

# Email send function
def send_email(receiver_email: str, subject: str, body: str):
    # Creating object MIMEMultipart
    message = MIMEMultipart()
    message["From"] = 'dodik337.github@gmail.com'
    message["To"] = receiver_email
    message["Subject"] = subject

    # Add text to message
    message.attach(MIMEText(body, "plain"))

    # Message send
    smtpObj = smtplib.SMTP('smtp.gmail.com', 587)
    smtpObj.starttls()
    smtpObj.login('dodik337.github@gmail.com', 'nrgz ctgo ignr upwv')
    smtpObj.sendmail('dodik337.github@gmail.com', receiver_email, message.as_string())

# Main PAGE
@app.route('/', methods=['GET', 'POST'])
def start_page():
    db = get_db()
    database = FDataBase(db)
    page = 0
    if database.getAllPostsId() == []:
        if 'userlogged' not in session:
            return render_template('index.html',
                                           title="Main",
                                           menu=database.getMenu(),
                                           posts=database.getPostAnnoce(),
                                           page=page,
                                           MAX_PAGES=0)
        filename = str(session['userlogged']) + '.png'
        status = database.getStatus(session['userlogged'])[0]
        nick = database.getProfile(session['userlogged'])[0]['nick']
        for i in os.listdir(f'{app.root_path + "/static/avatars/"}'):
            if filename in i:
                return render_template('index.html',
                                           title="Main",
                                           menu=database.getMenu(),
                                           posts=database.getPostAnnoce(),
                                           page=page,
                                           MAX_PAGES=0,
                                           ava=open(f'{app.root_path + "/static/avatars/" + filename}', 'rb'),
                                           status=status,
                                           nick=nick)
        else:
            return render_template('index.html',
                                           title="Main",
                                           menu=database.getMenu(),
                                           posts=database.getPostAnnoce(),
                                           page=page,
                                           MAX_PAGES=0,
                                           ava_empty=open(f'{app.root_path + "/static/avatars/static.png"}', 'rb'),
                                           status=status,
                                           nick=nick)
    elif database.getAllPostsId()[-1][0] == 1:
        if 'userlogged' not in session:
            return render_template('index.html',
                                           title="Main",
                                           menu=database.getMenu(),
                                           posts=database.getPostAnnoce(),
                                           page=page,
                                           MAX_PAGES=0)
        filename = str(session['userlogged']) + '.png'
        status = database.getStatus(session['userlogged'])[0]
        nick = database.getProfile(session['userlogged'])[0]['nick']
        for i in os.listdir(f'{app.root_path + "/static/avatars/"}'):
            if filename in i:
                return render_template('index.html',
                                           title="Main",
                                           menu=database.getMenu(),
                                           posts=database.getPostAnnoce(),
                                           page=page,
                                           MAX_PAGES=0,
                                           ava=open(f'{app.root_path + "/static/avatars/" + filename}', 'rb'),
                                           status=status,
                                           nick=nick)
        else:
            return render_template('index.html',
                                           title="Main",
                                           menu=database.getMenu(),
                                           posts=database.getPostAnnoce(),
                                           page=page,
                                           MAX_PAGES=0,
                                           ava_empty=open(f'{app.root_path + "/static/avatars/static.png"}', 'rb'),
                                           status=status,
                                           nick=nick)
    else:
        if 'userlogged' not in session:
            return render_template('index.html',
                                           title="Main",
                                           menu=database.getMenu(),
                                           posts=database.getPostAnnoce(),
                                           page=page,
                                           MAX_PAGES=1)
        filename = str(session['userlogged']) + '.png'
        status = database.getStatus(session['userlogged'])[0]
        nick = database.getProfile(session['userlogged'])[0]['nick']
        for i in os.listdir(f'{app.root_path + "/static/avatars/"}'):
            if filename in i:
                return render_template('index.html',
                                           title="Main",
                                           menu=database.getMenu(),
                                           posts=database.getPostAnnoce(),
                                           page=page,
                                           MAX_PAGES=1,
                                           ava=open(f'{app.root_path + "/static/avatars/" + filename}', 'rb'),
                                           status=status,
                                           nick=nick)
        else:
            return render_template('index.html',
                                           title="Main",
                                           menu=database.getMenu(),
                                           posts=database.getPostAnnoce(),
                                           page=page,
                                           MAX_PAGES=1,
                                           ava_empty=open(f'{app.root_path + "/static/avatars/static.png"}', 'rb'),
                                           status=status,
                                           nick=nick)

# Login PAGE
@app.route('/login', methods=['POST', 'GET'])
def login():
    db = get_db()
    database = FDataBase(db)
    if 'userlogged' in session:
        return redirect(url_for('start_page'))
    if request.method == 'POST':
        if len(request.form['username']) > 0 and len(request.form['password']) > 0:
            if database.getData(request.form['username'], request.form['password']):
                session.permanent = True
                session['userlogged'] = database.getData(request.form['username'], request.form['password'])[0][0]
                return redirect(url_for('start_page'))
    return render_template('login.html',
                                           title="Log in",
                                           menu=database.getMenu())

# Register
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
                    if database.addData(request.form["reg_username"], request.form["reg_password"], request.form['reg_email'],'', 'unconfirmed'):
                        session.permanent = True
                        session['userlogged'] = request.form['reg_username']
                        if 'file' not in request.files:
                            flash('Can not read the file', category='error')
                        file = request.files['file']
                        if file and allowed_file(file.filename):
                            filename = str(session['userlogged']) + '.png'
                            file.save(os.path.join(f'{app.root_path + "/static/avatars/" + filename}'))
                        if database.addProfile(request.form['reg_nick'], '', '', '', session['userlogged']):
                            return redirect(url_for('confirm_email', login=session['userlogged']))
    return redirect(url_for('login'))

# Sending message to user
@app.route('/send_email/<login>', methods=['POST', 'GET'])
def confirm_email_sending(login: str):
    db = connect_db()
    database = FDataBase(db)
    if 'userlogged' not in session or session['userlogged'] != login:
        return redirect(url_for('start_page'))
    email = database.getEmail(login)[0]
    global code
    code = generate_code()
    msg = f"""
        
        From: Evgeniu Stepin
        To: {login}
        
        Please confirm your register on website https://myblogweb.pythonanywhere.com/
        
        To confirm registration enter this code in special field


                {code}


        Best wishes,
        Evgeniu Stepin
        https://myblogweb.pythonanywhere.com/

    """
    send_email(email, 'Confirm Email', msg)
    return redirect(url_for('confirm_email', login=login))

# Confirm email PAGE
@app.route('/confirm_email/<login>', methods=['POST', 'GET'])
def confirm_email(login: str):
    db = connect_db()
    database = FDataBase(db)
    if 'userlogged' not in session or session['userlogged'] != login:
        return redirect(url_for('login'))
    filename = str(session['userlogged']) + '.png'
    status = database.getStatus(session['userlogged'])[0]
    nick = database.getProfile(session['userlogged'])[0]['nick']
    if request.method == 'POST':
        if len(request.form['code']) == 0 or int(request.form['code']) != int(code):
            return redirect(url_for('confirm_email', login=login))
        database.UpdateEmailStatus(login, 'confirm')
        email = database.getEmail(login)[0]
        msg = f"""
            
            From: Evgeniu Stepin
            To: {login}
            
            
            Thank you for registration on my website!
            
            I hope you have a great time!
            
            
            Best wishes,
            Evgeniu Stepin
            https://myblogweb.pythonanywhere.com/
            
        """
        send_email(email, 'Thank you for registration!', msg)
        return redirect(url_for('settings'))
    for i in os.listdir(f'{app.root_path + "/static/avatars/"}'):
        if filename in i:
            return render_template('confirm.html',
                                           title='Confirm Email',
                                           menu=database.getMenu(),
                                           ava=open(f'{app.root_path + "/static/avatars/" + filename}', 'rb'),
                                           status=status,
                                           nick=nick)
    else:
        return render_template('confirm.html',
                                           title='Confirm Email',
                                           menu=database.getMenu(),
                                           ava_empty=open(f'{app.root_path + "/static/avatars/static.png"}', 'rb'),
                                           status=status,
                                           nick=nick)

# Admin PAGE
@app.route('/admin', methods=['POST', 'GET'])
def admin_page():
    db = get_db()
    database = FDataBase(db)
    if 'userlogged' not in session:
        filename = str(session['userlogged']) + '.png'
        status = database.getStatus(session['userlogged'])[0]
        nick = database.getProfile(session['userlogged'])[0]['nick']
        if status == 'admin':
            if request.method == 'POST':
                addtodo = database.addTODO(request.form['text'])
                if addtodo:
                    return redirect(url_for('admin_page'))
                return redirect(url_for('admin_page'))
            for i in os.listdir(f'{app.root_path + "/static/avatars/"}'):
                if filename in i:
                    return render_template('admin.html',
                                           title='Admin Page',
                                           menu=database.getMenu(),
                                           posts=database.getAllposts(),
                                           todo=database.getTODO(),
                                           ava=open(f'{app.root_path + "/static/avatars/" + filename}', 'rb'),
                                           status=status,
                                           nick=nick)
            else:
                return render_template('admin.html',
                                           title='Admin Page',
                                           menu=database.getMenu(),
                                           posts=database.getAllposts(),
                                           todo=database.getTODO(),
                                           ava_empty=open(f'{app.root_path + "/static/avatars/static.png"}', 'rb'),
                                           status=status,
                                           nick=nick)
    return redirect(url_for('start_page'))

# Creating post PAGE
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
                    return render_template('post.html',
                                           title='Add post',
                                           menu=database.getMenu(),
                                           ava=open(f'{app.root_path + "/static/avatars/" + filename}', 'rb'),
                                           status=status,
                                           nick=nick)
            else:
                return render_template('post.html',
                                           title='Add post',
                                           menu=database.getMenu(),
                                           ava_empty=open(f'{app.root_path + "/static/avatars/static.png"}', 'rb'),
                                           status=status,
                                           nick=nick)
    return redirect(url_for('start_page'))

# Posts PAGES
@app.route('/post/page/<int:page>/<int:last_id>')
def post_page(page: int, last_id: int):
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
                    return render_template('post_page.html',
                                           title=f'Page {page}',
                                           menu=database.getMenu(),
                                           posts=database.getPostAnnocePages(last_id),
                                           page=page,
                                           last_id=last_id,
                                           MAX_PAGES=MAX_PAGES,
                                           ava=open(f'{app.root_path + "/static/avatars/" + filename}', 'rb'),
                                           status=status,
                                           nick=nick)
            else:
                return render_template('post_page.html',
                                           title=f'Page {page}',
                                           menu=database.getMenu(),
                                           posts=database.getPostAnnocePages(last_id),
                                           page=page,
                                           last_id=last_id,
                                           MAX_PAGES=MAX_PAGES,
                                           ava_empty=open(f'{app.root_path + "/static/avatars/static.png"}', 'rb'),
                                           status=status,
                                           nick=nick)
        return render_template('post_page.html',
                                           title=f'Page {page}',
                                           menu=database.getMenu(),
                                           posts=database.getPostAnnocePages(last_id),
                                           page=page,
                                           last_id=last_id,
                                           MAX_PAGES=MAX_PAGES)
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
                    return render_template('post_page.html',
                                           title=f'Page {page}',
                                           menu=database.getMenu(),
                                           posts=database.getPostAnnocePages(last_id),
                                           page=page,
                                           last_id=last_id,
                                           MAX_PAGES=MAX_PAGES,
                                           ava=open(f'{app.root_path + "/static/avatars/" + filename}', 'rb'),
                                           status=status,
                                           nick=nick)
            else:
                return render_template('post_page.html',
                                           title=f'Page {page}',
                                           menu=database.getMenu(),
                                           posts=database.getPostAnnocePages(last_id),
                                           page=page,
                                           last_id=last_id,
                                           MAX_PAGES=MAX_PAGES,
                                           ava_empty=open(f'{app.root_path + "/static/avatars/static.png"}', 'rb'),
                                           status=status,
                                           nick=nick)
        return render_template('post_page.html',
                                           title=f'Page {page}',
                                           menu=database.getMenu(),
                                           posts=database.getPostAnnocePages(last_id),
                                           page=page,
                                           last_id=last_id,
                                           MAX_PAGES=MAX_PAGES)
    return render_template('post_page.html',
                                           title=f'Page {page}',
                                           menu=database.getMenu(),
                                           posts=database.getPostAnnocePages(last_id),
                                           page=page,
                                           last_id=last_id,
                                           MAX_PAGES=MAX_PAGES)

# Edit post PAGE
@app.route('/editpost/<int:id_post>', methods=['POST', 'GET'])
def post_edit(id_post: int):
    db = get_db()
    database = FDataBase(db)
    if 'userlogged' not in session:
        return redirect(url_for('start_page'))
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
                return render_template('post_edit.html',
                                           title='Edit post',
                                           menu=database.getMenu(),
                                           post=database.getPost(id_post),
                                           ava=open(f'{app.root_path + "/static/avatars/" + filename}', 'rb'),
                                           status=status,
                                           nick=nick)
        else:
            return render_template('post_edit.html',
                                           title='Edit post',
                                           menu=database.getMenu(),
                                           post=database.getPost(id_post),
                                           ava_empty=open(f'{app.root_path + "/static/avatars/static.png"}', 'rb'),
                                           status=status,
                                           nick=nick)

# Quit
@app.route('/quit', methods=['GET', 'POST'])
def quit_login():
    if 'userlogged' not in session:
        return redirect(url_for('start_page'))
    return redirect(url_for('start_page')), session.clear()


# Deleting post
@app.route('/delpost/<int:id_post>')
def delpost_page(id_post: int):
    db = get_db()
    database = FDataBase(db)
    ph = connect_photo()
    photobase = Photo(ph)
    title = database.getPostAnnoce()
    aticle = database.getPostAnnoce()
    post_name = database.getPost(id_post)[0]
    if 'userlogged' not in session:
        return redirect(url_for('start_page'))
    status = database.getStatus(session['userlogged'])[0]
    nick = database.getProfile(session['userlogged'])[0]['nick']
    if status == 'admin':
        delpost = database.delPost(id_post)
        delphoto = photobase.PhotoDelete(post_name)
        if not title:
            abort(404)
        if delpost and delphoto:
            return redirect(url_for('admin_page'))
        return render_template('admin.html',
                                           menu=database.getMenu(),
                                           post=aticle,
                                           post_title=title,
                                           status=status)

# Post PAGE
@app.route('/posts/<int:id_post>', methods=['POST', 'GET'])
def showPost(id_post: int):
    db = get_db()
    database = FDataBase(db)
    ph = connect_photo()
    photobase = Photo(ph)
    title, aticle = database.getPost(id_post)
    photo = photobase.getPhoto(title)
    comments = database.getComments(id_post)
    if 'userlogged' not in session:
        if photo:
            return render_template('aticle.html',
                                           title=title,
                                           menu=database.getMenu(),
                                           post=Markup(aticle),
                                           post_title=title,
                                           post_image=photo[2],
                                           comments=comments,
                                           posts=database.getPostAnnoce(),
                                           id_post=id_post)
        return render_template('aticle.html',
                                           title=title,
                                           menu=database.getMenu(),
                                           post=Markup(aticle),
                                           post_title=title,
                                           posts=database.getPostAnnoce(),
                                           comments=comments,
                                           id_post=id_post)
    filename = str(session['userlogged']) + '.png'
    status = database.getStatus(session['userlogged'])[0]
    nick = database.getProfile(session['userlogged'])[0]['nick']
    if photo:
        for i in os.listdir(f'{app.root_path + "/static/avatars/"}'):
            if filename in i:
                return render_template('aticle.html',
                                           title=title,
                                           menu=database.getMenu(),
                                           post=Markup(aticle),
                                           post_title=title,
                                           post_image=photo[2],
                                           comments=comments,
                                           posts=database.getPostAnnoce(),
                                           id_post=id_post,
                                           ava=open(f'{app.root_path + "/static/avatars/" + filename}', 'rb'),
                                           status=status,
                                           nick=nick)
        else:
            return render_template('aticle.html',
                                           title=title,
                                           menu=database.getMenu(),
                                           post=Markup(aticle),
                                           post_title=title,
                                           post_image=photo[2],
                                           comments=comments,
                                           posts=database.getPostAnnoce(),
                                           id_post=id_post,
                                           ava_empty=open(f'{app.root_path + "/static/avatars/static.png"}', 'rb'),
                                           status=status,
                                           nick=nick)
    if comments:
        if request.method == 'POST':
            if len(request.form['text']) > 3:
                addcom = database.addComment(session['userlogged'], request.form['text'], id_post)
                if addcom:
                    return redirect(url_for('showPost', id_post=id_post))
                for i in os.listdir('static/avatars/'):
                    if filename in i:
                        return render_template('aticle.html',
                                           title=title,
                                           menu=database.getMenu(),
                                           post=Markup(aticle),
                                           post_title=title,
                                           comments=comments,
                                           posts=database.getPostAnnoce(),
                                           id_post=id_post,
                                           ava=open(f'static/avatars/{filename}', 'rb'),
                                           status=status,
                                           nick=nick)
                else:
                    return render_template('aticle.html',
                                           title=title,
                                           menu=database.getMenu(),
                                           post=Markup(aticle),
                                           post_title=title,
                                           comments=comments,
                                           posts=database.getPostAnnoce(),
                                           id_post=id_post,
                                           ava_empty=open(f'static/avatars/static.png', 'rb'),
                                           status=status,
                                           nick=nick)
            return render_template('aticle.html',
                                           title=title,
                                           menu=database.getMenu(),
                                           post=Markup(aticle),
                                           post_title=title,
                                           comments=comments,
                                           posts=database.getPostAnnoce(),
                                           id_post=id_post,
                                           status=status)
    for i in os.listdir(f'{app.root_path + "/static/avatars/"}'):
        if filename in i:
            return render_template('aticle.html',
                                           title=title,
                                           menu=database.getMenu(),
                                           post=Markup(aticle),
                                           post_title=title,
                                           comments=comments,
                                           posts=database.getPostAnnoce(),
                                           id_post=id_post,
                                           ava=open(f'{app.root_path + "/static/avatars/" + filename}', 'rb'),
                                           status=status,
                                           nick=nick)
    else:
        return render_template('aticle.html',
                                           title=title,
                                           menu=database.getMenu(),
                                           post=Markup(aticle),
                                           post_title=title,
                                           comments=comments,
                                           posts=database.getPostAnnoce(),
                                           id_post=id_post,
                                           ava_empty=open(f'{app.root_path + "/static/avatars/static.png"}', 'rb'),
                                           status=status,
                                           nick=nick)

# Display image
@app.route('/display_image_by_name/<post_name>', methods=['POST', 'GET'])
def display_image_by_name(post_name: str):
    ph = connect_photo()
    photobase = Photo(ph)
    filename = photobase.getPhoto(post_name)[3]
    return redirect(url_for('static', filename='photos/' + filename), code=301)

# Deleting comment
@app.route('/delcom/<int:id_post>/<int:id_com>')
def delcom_page(id_post: int, id_com: int):
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

# Deleting to-do-list
@app.route('/deltodo/<int:id_todo>/')
def deltodo(id_todo: int):
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

# Settings PAGE
@app.route('/settings/', methods=['POST', 'GET'])
def settings():
    db = connect_db()
    database = FDataBase(db)
    if 'userlogged' not in session:
        return redirect(url_for('start_page'))
    filename = str(session['userlogged']) + '.png'
    status = database.getStatus(session['userlogged'])[0]
    nick = database.getProfile(session['userlogged'])[0]['nick']
    email_status = database.getEmailStatus(session['userlogged'])[0]
    for i in os.listdir(f'{app.root_path + "/static/avatars/"}'):
        if filename in i:
            if database.getProfile(session['userlogged']):
                return render_template('settings.html',
                                           menu=database.getMenu(),
                                           title='Settings',
                                           email=database.getEmail(session['userlogged'])[0],
                                           ava=open(f'{app.root_path + "/static/avatars/" + filename}', 'rb'),
                                           prof=database.getProfile(session['userlogged']),
                                           status=status,
                                           nick=nick,
                                           email_status=email_status)
            return render_template('settings.html',
                                           menu=database.getMenu(),
                                           title='Settings',
                                           email=database.getEmail(session['userlogged'])[0],
                                           ava=open(f'{app.root_path + "/static/avatars/" + filename}', 'rb'),
                                           status=status,
                                           email_status=email_status)
    else:
        if database.getProfile(session['userlogged']):
            return render_template('settings.html',
                                           menu=database.getMenu(),
                                           title='Settings',
                                           email=database.getEmail(session['userlogged'])[0],
                                           ava_empty=open(f'{app.root_path + "/static/avatars/static.png"}', 'rb'),
                                           prof=database.getProfile(session['userlogged']),
                                           status=status,
                                           nick=nick,
                                           email_status=email_status)
        return render_template('settings.html',
                                           menu=database.getMenu(),
                                           title='Settings',
                                           email=database.getEmail(session['userlogged'])[0],
                                           ava_empty=open(f'{app.root_path + "/static/avatars/static.png"}', 'rb'),
                                           status=status,
                                           email_status=email_status)

# Profile editing
@app.route('/prfoile', methods=['POST', 'GET'])
def profile():
    db = connect_db()
    database = FDataBase(db)
    if 'userlogged' not in session:
        return redirect(url_for('start_page'))
    if request.method == 'POST':
        if database.getProfile(session['userlogged']):
            if 0 < len(request.form['nick']) < 15:
                if database.UpdateProfile(request.form['nick'], request.form['name'],  request.form['age'], request.form['about'], session['userlogged']):
                    flash('Profile has been updated', category='success')
                    return redirect(url_for('settings'))
                else:
                    flash('This nickname is already exist', category='error')
                    return redirect(url_for('settings'))
            else:
                flash('This nickname is incorrect', category='error')
                return redirect(url_for('settings'))
        else:
            if 0 < len(request.form['nick_reg']) < 15:
                if database.addProfile(request.form['nick_reg'], request.form['name_reg'],  request.form['age_reg'], request.form['about_reg'], session['userlogged']):
                    flash('Profile has been updated', category='success')
                    return redirect(url_for('settings'))
                else:
                    flash('Error', category='error')
                    return redirect(url_for('settings'))
            else:
                flash('This nickname is incorrect', category='error')
                return redirect(url_for('settings'))

# Password editing
@app.route('/password', methods=['POST', 'GET'])
def password():
    db = connect_db()
    database = FDataBase(db)
    if 'userlogged' not in session:
        return redirect(url_for('start_page'))
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

#Email editing
@app.route('/email', methods=['POST', 'GET'])
def email():
    db = connect_db()
    database = FDataBase(db)
    if 'userlogged' not in session:
        return redirect(url_for('start_page'))
    if request.method == 'POST':
        if len(request.form['email']) > 0:
            if database.UpdateEmail(request.form['email'], session['userlogged']):
                database.UpdateEmailStatus(session['userlogged'], 'unconfirmed')
                flash('Email was successfully changed', category='success')
                return redirect(url_for('settings'))
            else:
                flash('Error', category='error')
                return redirect(url_for('settings'))
        return redirect(url_for('settings'))

# Account deleting
@app.route('/delete_account/<login>', methods=['POST', 'GET'])
def delete_account(login: str):
    db = connect_db()
    database = FDataBase(db)
    if 'userlogged' not in session or session['userlogged'] != login or not database.deleteAccount(login):
        return redirect(url_for('settings'))
    return redirect(url_for('start_page')), session.clear()

# Upload some file
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if 'userlogged' not in session:
        return redirect(url_for('start_page'))
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

# Loading user avatar
@app.route('/userava/<username>', methods=['POST', 'GET'])
def userava(username: str):
    filename = str(username) + ".png"
    return redirect(url_for('static', filename='avatars/' + filename), code=301)

# Deleting user avatar
@app.route('/userava/delete/<filename>')
def userava_delete(filename: str):
    filename = str(session['userlogged']) + '.png'
    for i in os.listdir(f'{app.root_path + "/static/avatars/"}'):
        if filename in i:
            return redirect(url_for('settings')), os.remove(f'{app.root_path + "/static/avatars/" + filename}')
    else:
        flash("No avatar", category='error')
        return redirect(url_for('settings'))

# Forget psw
@app.route('/forget_psw/', methods=['POST', 'GET'])
def forget_psw():
    db = connect_db()
    database = FDataBase(db)
    if 'userlogged' in session:
        return redirect(url_for('start_page'))
    if request.method == 'POST':
        if len(request.form['login']) == 0:
            return redirect(url_for('forget_psw'))
        if '@' not in request.form['login'] and database.getEmail(request.form['login']):
            login = request.form['login']
            return redirect(url_for('reset_password', login=login))
    return render_template('forget_psw.html',
                                            menu=database.getMenu(),
                                            title='Forget password')

# Send reset code
@app.route('/reset_code_send/<login>', methods=['POST', 'GET'])
def reset_code_send(login: str):
    db = connect_db()
    database = FDataBase(db)
    email = database.getEmail(login)[0]
    global code
    code = generate_code()
    msg = f"""

        From: Evgeniu Stepin
        To: {login}

        To reset password, you need to fill this code in special field
        If you don't want to reset password, ignore this message

            {code}

        Best wishes,
        Evgeniu Stepin
        https://myblogweb.pythonanywhere.com/

    """
    send_email(email, 'Reset password', msg)
    return redirect(url_for('reset_password', login=login))

# Reset password
@app.route('/reset_password/<login>', methods=['POST', 'GET'])
def reset_password(login: str):
    db = connect_db()
    database = FDataBase(db)
    email_fst = database.getEmail(login)[0]
    if request.method == 'POST':
        if int(request.form['code']) == int(code):
            session['userlogged'] = login
            email = database.getEmail(login)[0]
            new_psw = secrets.token_hex(16)
            msg = f"""
                
                From: Evgeniu Stepin
                To: {login}
                
                Your password was changed.
                Now your current password is:
                    
                    {new_psw}
                
                Best wishes,
                Evgeniu Stepin
                https://myblogweb.pythonanywhere.com/
                
            """
            database.UpdateUserPass(login, new_psw)
            send_email(email, 'Password was changed', msg)
            return redirect(url_for('settings'))
        return render_template('reset_password.html',
                               menu=database.getMenu(),
                               title='Reset password',
                               login=login)
    return render_template('reset_password.html',
                           menu=database.getMenu(),
                           title='Reset password',
                           login=login,
                           email=email_fst)

# Website start
if __name__ == "__main__":
    app.run(debug=True)