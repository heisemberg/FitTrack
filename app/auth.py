import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from werkzeug.security import check_password_hash, generate_password_hash

from app.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        nombres = request.form['nombres']
        apellidos = request.form['apellidos']
        fecha_nacimiento = request.form['fecha_nacimiento']
        db, c = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        else:
            c.execute('SELECT id FROM usuario WHERE usuario = %s', (username,))
            usuario = c.fetchone()
            if usuario is not None:
                error = 'User {} is already registered.'.format(username)

        if error is None:
            c.execute(
                'INSERT INTO usuario (usuario, password, email, nombres, apellidos, fecha_nacimiento) VALUES (%s, %s, %s, %s, %s, %s)',
                (username, generate_password_hash(password), email, nombres, apellidos, fecha_nacimiento)
            )
            db.commit()
            return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db, c = get_db()
        error = None
        c.execute('SELECT * FROM usuario WHERE usuario = %s', (username,))
        usuario = c.fetchone()

        if usuario is None:
            error = 'Incorrect username or password.'
        elif not check_password_hash(usuario['password'], password):
            error = 'Incorrect username or password.'

        if error is None:
            session.clear()
            session['user_id'] = usuario['id']

        # Check if the user has a profile
            c.execute('SELECT * FROM perfil_usuario WHERE usuario_id = %s', (usuario['id'],))
            perfil = c.fetchone()
            
            if perfil is None:
                return redirect(url_for('auth.register_profile'))

            return redirect(url_for('fittrack.index'))

        flash(error)

    return render_template('auth/login.html')

@bp.route('/profile', methods=('GET', 'POST'))
def register_profile():
    if request.method == 'POST':
        sexo = request.form['sexo']
        peso_inicial = request.form['peso_inicial']
        estatura = request.form['estatura']
        objetivo = request.form['objetivo']
        usuario_id = session.get('user_id')
        db, c = get_db()
        error = None

        if not sexo:
            error = 'Sexo is required.'
        elif not peso_inicial:
            error = 'Peso inicial is required.'
        elif not estatura:
            error = 'Estatura is required.'
        elif not objetivo:
            error = 'Objetivo is required.'

        if error is None:
            c.execute(
                'INSERT INTO perfil_usuario (usuario_id, sexo, peso_inicial, estatura, objetivo) VALUES (%s, %s, %s, %s, %s)',
                (usuario_id, sexo, peso_inicial, estatura, objetivo)
            )
            db.commit()
            return redirect(url_for('fittrack.index'))

        flash(error)

    return render_template('auth/register_profile.html')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.usuario = None
    else:
        db, c = get_db()
        c.execute('SELECT * FROM usuario WHERE id = %s', (user_id,))
        g.usuario = c.fetchone()

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.usuario is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))