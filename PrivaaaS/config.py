import os.path
basedir = os.path.abspath(os.path.dirname(__file__))
from flask.ext.script import Manager, Server
from privacy import app

DEBUG = True

SQLALCHEMY_DATABASE_URI = 'sqlite:///'+os.path.join(basedir, 'storage.db')
SQLALCHEMY_TRACK_MODIFICATIONS = True

UPLOAD_FOLDER = os.path.join(basedir, '/privacy/static/up_dir/')
#ALLOWED_EXTENSIONS = set(['json', 'xml', 'csv'])

SECRET_KEY ='uma-chave-bem-segura'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#manager = Manager(app)

 # Turn on debugger by default and reloader 
#manager.add_command("runserver", Server(
#    use_debugger = True,
#    use_reloader = True,
#    host = 'localhost') )
