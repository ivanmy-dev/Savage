from flask import( render_template, Blueprint, flash, g, redirect, request, session, url_for, Response)
import functools
from werkzeug.security import check_password_hash, generate_password_hash
from savage.models.user import User, Img
from werkzeug.utils import secure_filename
from savage import db

auth = Blueprint('auth', __name__, url_prefix='')

#g.user
@auth.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    img_id = session.get('img_id')

    if user_id is None:
        g.user = None
    else:
        g.user = User.query.get_or_404(user_id)
    
    if img_id is None:
        g.img = None
    else:
        g.img = Img.query.get_or_404(img_id)

#req usuario registrado
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view

#req usuario admin
def admin_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        vemail = 'admin@gmail.com' 
        if g.user.email != vemail:
            return redirect(url_for('auth.home'))
        return view(**kwargs)
    return wrapped_view

#landingpage
@auth.route('/')
def index():
    return redirect(url_for('auth.i'))

@auth.route('/i')
def i():
    return render_template('public/landing.html')


@auth.route('/perfil')
def perfil():
    return render_template('public/perfil.html')

@auth.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.i'))

@auth.route('/home')
@login_required
def home():
        return render_template('public/home.html')

@auth.route('/cP')
@login_required
def cP():
        return render_template('auth/cP.html')

#Register
@auth.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        user = User(username, email, generate_password_hash(password))

        error = None
        if not username:
            error = 'Se requiere un nombre de usuario'
        elif not email:
            error = 'Se requiere un correo electronico'
        elif not password:
            error = 'Se requiere una contraseña'
        
        user_name = User.query.filter_by(email = email).first()
        if user_name == None:
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('auth.login'))
        else:
            error = f'{email}, ya existe!'
        flash(error)
    return render_template('auth/register.html')

#Iniciar Sesión
@auth.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email = email).first()
        error = None

        if user == None:
            error = 'Correo electrónico incorrecto'
        elif not check_password_hash(user.password, password):
             error = 'Contraseña incorrecta'

        if error is None:
            session['user_id'] = user.id
            return redirect(url_for('auth.home'))
        
        flash(error)
    return render_template('auth/login.html') 

#Antes de continuar completa tu perfil...
@auth.route('/upload', methods=['POST'])
@login_required
def upload():

    pic = request.files['pic']

    if not pic:
        flash('No se ha subido ninguna foto!')
        return redirect(url_for('auth.cP'))
    
    filename = secure_filename(pic.filename)
    mimetype = pic.mimetype
    if not filename or not mimetype:
        flash('La foto se ha subido incorrectamente!')
        return redirect(url_for('auth.cP'))
    img = Img(img=pic.read(), name=filename, mimetype=mimetype)
    session['img_id'] = img.id
    db.session.add(img)
    db.session.commit()
    flash('La foto se ha subido correctamente!')
    return redirect(url_for('auth.home'))


@auth.route('/<int:id>')
@login_required
@admin_required
def get_img(id):
    img = Img.query.filter_by(id=id).first()
    if not img:
        flash('No se encuentra la Foto!')
        return redirect(url_for('auth.cP'))

    return Response(img.img, mimetype=img.mimetype)


