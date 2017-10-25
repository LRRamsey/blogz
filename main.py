from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import cgi
import os

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogzPass@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'kjdfOIEWUR09832RLJFof'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256))
    body = db.Column(db.String(256))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
   
    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['index', '/', 'blog', 'login', 'signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = str(request.form['username'])
        username_from_form = username
        username_error = ''

        if len(username_from_form) <= 0:
            username_error = "user name must contain at least 3 characters"

        if len(username_from_form) < 3:
            username_error = "user name must be longer than 3 charachters"

        if len(username_from_form) > 20:
            username_error = "user name cannot be longer than 20 characters"

        if " " in username_from_form:
            username_error = "user name may not contain spaces"


        
        password = str(request.form['password'])
        verify = str(request.form['verify'])
        password_error = ''
        

        if password != verify:
            password_error = "passwords do not match, please re enter."

        if len(password) <= 0:
            password_error = "password must contain at least 3 characters"

        if len(password) < 3:
            password_error = "password must be longer than 3 charachters"

        if len(password) > 20:
            password_error = "password cannot be longer than 20 characters"

        if " " in password:
            password_error = "password may not contain spaces"

        #TODO -  validate users data

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            username_error = "This user name is already in use"

        if not existing_user and not password_error and not username_error:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')

        else:
            return render_template('signup.html', 
            password_error=password_error, username_error=username_error, 
            username=username_from_form)

    return render_template('signup.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            session['username'] = username
            flash("logged in")
            return redirect('/newpost')
        
        else:
            flash("User password incorrect, or user does not exist", "error")
        
    return render_template('login.html')

@app.route('/logout')
def logout():
    del session['username']
    flash('logged out')
    return redirect('/')
#
#
#
#

#TODO make index an index of authors, possibly using the blog class not the user class,
#the same i got the written by section to work
@app.route('/')
@app.route('/index', methods=['POST', 'GET'])
def index():
    if request.args:
        blog_id = request.args.get('id')
        blog_query = Blog.query.get(blog_id)
        return render_template('singleuser.html', blog_query=blog_query)
    else:
        blogs = Blog.query.all()
        return render_template('index.html', blogs=blogs)


@app.route('/blog', methods=['POST', 'GET'])
def blog():
    if request.args:
        blog_id = request.args.get('id')
        blog_query = Blog.query.get(blog_id)
        return render_template('single-post.html', blog_query=blog_query)
    else:
        blogs = Blog.query.all()
        return render_template('blog.html', blogs=blogs)

    
@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    
    owner = User.query.filter_by(username=session['username']).first()

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        title_error = ''
        body_error = ''

        if len(title) == 0:
            title_error = "title cannot be blank"

        if len(body) == 0:
            body_error = "body cannot be empty"
                
        
        #TODO handle errors\
        if not title_error and not body_error: 
            new_post = Blog(title, body, owner)
            db.session.add(new_post)
            db.session.commit()
            
            id_post = '/blog?id=' + str(new_post.id)
            return redirect(id_post)      

        else:    
            return render_template('newpost.html', title_error=title_error, body_error=body_error)
    else:
        return render_template('newpost.html')    


if __name__ == '__main__':
    app.run()