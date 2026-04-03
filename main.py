import os
from werkzeug.security import check_password_hash, generate_password_hash
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, redirect, url_for, session
from sqlalchemy.sql import func

app = Flask(__name__)
load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))

# app config
app.secret_key = os.getenv("SECRET_KEY") 
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # disable for less memory use

db = SQLAlchemy(app)

# declare a table in database.db by making a model via inheritance of the db.Model class
class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    article_title = db.Column(db.String(100), nullable=False)

    article = db.Column(db.Text) # will be the content of the article (raw markdown string) t

    def __repr__(self):
        return f'<Article: {self.article_title}>'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    username = db.Column(db.String(25))
    hash_key = db.Column(db.Text)

    def __repr__(self):
        return f'<username: {self.username}>'



with app.app_context(): # without this, it wouldn't know where to look to create the database!
    db.create_all()

    # if there is no data in database, then create 1 new user (me!)
    # db.session.execute(db.select(User)).first() returns None if the table is empty
    if not db.session.execute(db.select(User)).first():
        password = generate_password_hash(os.getenv("PASSWORD", default="shehwaz")) # add a default password incase something fails
        username = os.getenv("USERNAME")

        if password != 'shehwaz':
            admin_data = User(hash_key=password, username=username) # type: ignore

            db.session.add(admin_data)
            db.session.commit()


@app.route("/")
def main():
    articles = Article.query.order_by(Article.id.desc()).all()
    return render_template('index.html', articles=articles, admin=session.get("logged_in"))


@app.route("/create", methods=["GET", "POST"])
def create():
    # .get() returns none if no key is found, else it returns the value of the key. 
    # Therefore, we don't have to worry about the logged_in being flask or username being empty 
    if not session.get("logged_in") or not session.get("username"): 
        return "<h1>this is for admins only</h1>", 400

    if request.method == "GET": # just load the create page
        return render_template('create.html')
    
    elif request.method == "POST":
        title = request.form.get("title")
        article = request.form.get("article")
        data = Article(article_title=title, article=article)
        db.session.add(data)
        db.session.commit()
        return redirect(url_for('main'))

    return "record not found", 400




@app.route("/delete", methods=["POST"])
def delete():
    if not request.form.get("article_id"):
        return "<h1>Must be a valid article number</h1>"
        
    if session.get("logged_in") and request.method == "POST":
        id = request.form.get("article_id")
        db.session.execute(db.delete(Article).where(Article.id == id))
        db.session.commit()
        return redirect(url_for("main"))

    return "<h1>Must be a valid article number</h1>"




@app.route("/view")
def view():
    id = request.args.get('id')
    requested_article = db.get_or_404(Article, id) # this is the article object, not the raw data
    raw_text = requested_article.article # index into the raw text of the article

    return render_template('view.html', raw_text=raw_text)



@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username=request.form.get("username")
        password=request.form.get("password")
        
        user = db.one_or_404(db.select(User).filter_by(username=username))
        
        if user and check_password_hash(user.hash_key, password):
            session["logged_in"] = True
            session["username"] = username
            return "<h1>Successfully Logged In!</h1>"
        else:
            return "<h1>Invalid username or password</h1>"

    return render_template('login.html')
