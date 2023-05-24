from flask import Flask
from exts import db, mail
from flask_migrate import Migrate
from flask import Flask, session, g
from models import UserModel
from blueprints.login import bp as login_bp
from blueprints.mainpage import bp as mainpage_bp
import config

app = Flask(__name__)
app.config.from_object(config)
db.init_app(app)
mail.init_app(app)
migrate = Migrate(app, db)

# 注册蓝图
app.register_blueprint(login_bp)
app.register_blueprint(mainpage_bp)

@app.before_request
def my_before_request():
    user_id = session.get("user_id")
    if user_id:
        user = UserModel.query.get(user_id)
        setattr(g, "user", user)
    else:
        setattr(g, "user", None)


@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
