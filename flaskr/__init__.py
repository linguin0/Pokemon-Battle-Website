import os

from flask import Flask
from flask import render_template
from . import db
from . import auth

def create_app(test_config=None): # create & configure app
    # instance_relative_config = True tells the app that the config files are relative to the instance folder
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY = 'dev', # keeps data safe
        DATABASE = os.path.join(app.instance_path, 'flaskr.sqlite') # database path
    )

    if test_config is None:
        # loads the instance config (if it exists), when not testing
        app.config.from_pyfile('config.py', silent=True) # allows tests to be configured independently
    else:
        # loads the test config if it's passed in
        app.config.from_mapping(test_config) # test_config used instead of instance config

    # Ensures the instance folder exists
    try:
        os.makedirs(app.instance_path) # makes sure paths exist
    except OSError:
        pass

    db.init_app(app)
    app.register_blueprint(auth.bp)

    @app.route("/")
    def home():
        return render_template("home.html")
    
    return app