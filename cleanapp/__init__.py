from flask import Flask
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from flask_mail import Mail, Message

csrf= CSRFProtect() #the one below is the same
mail=Mail()



def create_app():
    """Keeping all imports that would have caused conflict wuthin this function so that anytime we write from develop.. import..none of these statements will be executed"""
    from cleanapp.models import db
    from cleanapp import config


    app = Flask(__name__,instance_relative_config=True)


    app.config.from_pyfile('config.py',silent=True)
    app.config.from_object(config.DevelopmentConfig)


    db.init_app(app) #we moved the instantiation of db to models.py
    csrf.init_app(app) #initializing the app with CSRFprotect object
    mail.init_app(app)
    migrate= Migrate(app,db)
    return app

app = create_app() #called create_app to make app available here
from cleanapp import user_routes, admin_routes,forms, models


# class Meta:
#     csrf=True
#     csrf_time_limit=7200




