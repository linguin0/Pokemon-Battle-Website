import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST')) # associated /regsiter with the register view function
def register():
    if request.method == 'POST': # if user submitted the form
        # request.form is a special dict that maps submitted form keys and values
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        # validates that username and password aren't empty
        if not username:
            error = 'Username is required!'
        elif not password:
            error = 'Password is required!'

        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)) # not the most secure but it's ok for now
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("auth.login"))

        flash(error) # if validation fails, flash() stores the error messages that can be recieved when rendering the template

    return render_template('register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username'
        elif not check_password_hash(user['password'], password): # hashes the same password
            error = 'Incorrect password'

        if error is None:
            session.clear()
            session['user_id'] = user['id'] # data is stored in a cookie, which is sent to the browser.
            return redirect(url_for('index'))
        
        flash(error)

    return render_template('login.html')

@bp.before_app_request # registers a function that returns before the view function
def load_logged_in_user():
    user_id = session.get('user_id') # checks if user id is stored in session

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

@bp.route('/logout')
def logout():
    session.clear() # clears user id from session
    return redirect(url_for('index'))

def login_required(view):
    '''
    Checks to see if a user is loaded, redirect to login page if otherwise
    Will be used when user wants to battle or change their team
    '''
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    
    return wrapped_view