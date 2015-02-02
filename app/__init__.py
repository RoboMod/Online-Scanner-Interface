import os
from flask import Flask
from flask_bootstrap import Bootstrap
import flask_sijax

# create app
app = Flask(__name__)

# install Bootstrap extension
app.config['BOOTSTRAP_SERVE_LOCAL'] = True
Bootstrap(app)

# install Sijax extension
sijax_path = os.path.join(app.root_path, 'static/js/sijax/')
app.config['SIJAX_STATIC_PATH'] = sijax_path
app.config['SIJAX_JSON_URI'] = '/static/js/sijax/json2.js'
flask_sijax.Sijax(app)

# load views
from app import views