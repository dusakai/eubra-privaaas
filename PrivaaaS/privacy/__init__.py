from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from privacy.models.models import db

app = Flask (__name__)
app.config.from_object('config')
db.init_app(app)

migrate = Migrate (app, db)

manager = Manager (app)
manager.add_command ('db', MigrateCommand)


from privacy.controllers import default
from privacy.models import models, forms
