# @Author  : baiyu
# @Time    : 2023/4/20 16:32
# @File    : login.py
# @Description
import random
import string

from flask import Blueprint, render_template, jsonify, redirect, url_for, session
from flask import request
from models import UserModel, EmailCaptchaModel
from forms import LoginForm, RegisterForm
from werkzeug.security import generate_password_hash, check_password_hash
from exts import db, mail
from flask_mail import Message

bp = Blueprint("auth", __name__, url_prefix="/auth")

@bp.route("/")
def index():
    return redirect(url_for("auth.login"))

# 登录路由
@bp.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html")
    else:
        print(request.form)
        form = LoginForm(request.form)
        if form.validate():
            email = form.email.data
            password = form.password.data
            user = UserModel.query.filter_by(email=email).first()
            if not user:
                print("邮箱在数据库中不存在！")
                return redirect(url_for("auth.login"))
            if check_password_hash(user.password, password):
                # cookie：
                # cookie中不适合存储太多的数据，只适合存储少量的数据
                # cookie一般用来存放登录授权的东西
                # flask中的session，是经过加密后存储在cookie中的
                session['user_id'] = user.id
                print("进入")
                return redirect(url_for("mainpage.index"))
            else:
                print("密码错误！")
                return redirect(url_for("auth.login"))
        else:
            print(form.errors)
            return redirect(url_for("auth.login"))


# 注册路由
@bp.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template("register.html")
    else:
        # 验证用户提交的邮箱和验证码是否对应且正确
        # 表单验证：flask-wtf: wtforms
        form = RegisterForm(request.form)
        if form.validate():
            email = form.email.data
            username = form.username.data
            password = form.password.data
            user = UserModel(email=email, username=username, password=generate_password_hash(password))
            db.session.add(user)
            db.session.commit()
            print("注册成功！")
            return redirect(url_for("auth.login"))
        else:
            print(form.errors)
            return redirect(url_for("auth.register"))


# 退出路由
@bp.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# 获取邮箱验证码
# bp.route：如果没有指定methods参数，默认就是GET请求
@bp.route("/captcha/email")
def get_email_captcha():
    email = request.args.get("email")
    # 4/6：随机数组、字母、数组和字母的组合
    source = string.digits * 4
    captcha = random.sample(source, 4)
    captcha = "".join(captcha)
    # I/O：Input/Output
    message = Message(subject="风力预测发电系统", recipients=[email], body=f"您的验证码是:{captcha}")
    mail.send(message)
    # memcached/redis
    # 用数据库表的方式存储
    email_captcha = EmailCaptchaModel(email=email, captcha=captcha)
    db.session.add(email_captcha)
    db.session.commit()
    # RESTful API
    # {code: 200/400/500, message: "", data: {}}
    return jsonify({"code": 200, "message": "", "data": None})
