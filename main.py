import os
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, redirect, url_for

from sqlalchemy.sql import func

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TACK_MODIFICATIONS'] = False # disable for less memory use

db = SQLAlchemy(app)

# declare a table in database.db by making a model via inheritance of the db.Model class
class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    article_title = db.Column(db.String(100), nullable=False)

    article = db.Column(db.Text) # will be the content of the article (raw markdown string) t

    def __repr__(self):
        return f'<Article: {self.article_title}>'

@app.route("/")
def main():
    articles = Article.query.order_by(Article.id.desc()).all()
    return render_template('index.html', articles=articles)


@app.route("/create", methods=["GET", "POST"])
def create():
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

@app.route("/view")
def view():
    id = request.args.get('id')
    requested_article = db.get_or_404(Article, id) # this is the article object, not the raw data
    raw_text = requested_article.article # index into the raw text of the article

    return render_template('view.html', raw_text=raw_text)

    
