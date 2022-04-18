import os

from flask import Flask
from flask_session import Session
app = Flask(__name__, instance_relative_config=True, static_url_path='')
# Ensure templates are autoreloaded
app.config['TEMPLATES_AUTO_RELOAD'] = True
# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
from flask_sslify import SSLify
if 'DYNO' in os.environ:  # only trigger SSLify if the app is running on Heroku
    sslify = SSLify(app)
from app.controller import pwa, main
app.register_blueprint(main.bp)
app.register_blueprint(pwa.bp)




