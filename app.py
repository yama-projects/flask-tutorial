from crypt import methods
from email.policy import default
from ensurepip import bootstrap
from enum import unique
from turtle import title
from flask import Flask
from flask import render_template,request,redirect
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required
import os
from flask_bootstrap import Bootstrap

from datetime import datetime
import pytz


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SECRET_KEY'] = os.urandom(24)
db = SQLAlchemy(app)
bootstrap = Bootstrap(app)

# ログイン情報保持
loginManager = LoginManager()
loginManager.init_app(app)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    body = db.Column(db.String(300), nullable=False)
    create_at = db.Column(db.DateTime, nullable=False, default=datetime.now(pytz.timezone('Asia/Tokyo')))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False, unique=True)
    password = db.Column(db.String(12))

@loginManager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ホーム
@app.route("/")
@login_required
def index():
    if request.method == 'GET':
        posts = Post.query.all()
        return render_template('index.html', posts=posts)

# サインアップ
@app.route("/signup", methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User(username=username, password=generate_password_hash(password, method='sha256'))

        db.session.add(user)
        # 変更をコミットする
        db.session.commit()
        # ログイン画面に遷移する
        return redirect('/login')
    else:
        return render_template('signup.html')

# ログイン
@app.route("/login", methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if check_password_hash(user.password, password):
            login_user(user)
            return redirect('/')
    else:
        return render_template('login.html')

# ログアウト
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')


# 新規登録
@app.route("/create", methods=['GET','POST'])
@login_required
def create():
    if request.method == 'POST':
        title = request.form.get('title')
        body = request.form.get('body')

        post = Post(title=title, body=body)

        db.session.add(post)
        # 変更をコミットする
        db.session.commit()
        return redirect('/')
    else:
        return render_template('create.html')

# 編集
@app.route("/<int:id>/update", methods=['GET','POST'])
@login_required
def upate(id):
    post= Post.query.get(id)
    if request.method == 'GET':
        return render_template('update.html', post=post)
    else:
        post.title = request.form.get('title')
        post.body = request.form.get('body')

        # 変更をコミットする
        db.session.commit()
        return redirect('/')

# 削除
@app.route("/<int:id>/delete", methods=['GET'])
@login_required
def delete(id):
    post= Post.query.get(id)

    db.session.delete(post)
    db.session.commit()
    return redirect('/')
