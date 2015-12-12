from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_login import LoginManager
from flask_mail import Mail
from flaskext.uploads import UploadSet, IMAGES, configure_uploads

app = Flask(__name__)
app.config.from_object('config')

# Enable logins
lm = LoginManager(app)
lm.login_view = 'login'

# DB setup
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Mail setup
mail = Mail(app)

# CLI setup
manager = Manager(app)
manager.add_command('db', MigrateCommand)

team_icons = UploadSet('teamicons', IMAGES)
configure_uploads(app, [team_icons])

# Load our actual app
from app import views, models

# Run the app if we need to
if __name__ == '__main__':
    manager.run()
