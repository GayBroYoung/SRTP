from flask import Flask
from flask_script import Manager
from flask_script.commands import Shell
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate,MigrateCommand
import os

base_dir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'sqlite:///' + os.path.join(base_dir,'..','database/course_system.db')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
# app.config['SQLALCHEMY_ECHO'] = True
app.url_map.strict_slashes = False
db = SQLAlchemy(app)
migrate = Migrate(app,db)
manager = Manager(app)
def make_shell_context():
    from application import model
    return dict(app=app,db=db,model=model)
manager.add_command("shell",Shell(make_context=make_shell_context))
manager.add_command('db',MigrateCommand)
