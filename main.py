from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:buildblog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'kjdfOIEWUR09832RLJFof'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256))
    #TODO figure out how many characters i can put in my blog
    body = db.Column(db.String(256))
    #TODO figure out if strings work with textarea html

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/')
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
            new_post = Blog(title, body)
            db.session.add(new_post)
            db.session.commit()
            
            id_post = '/blog?id=' + str(new_post.id)
            return redirect(id_post)      

        else:    
            return render_template('newpost.html', title_error=title_error, body_error=body_error)
    else:
        return render_template('newpost.html')    

#@app.route('/blog/?=' + Blog.id, methods=['POST', 'GET'])
#def blog_id():
#    blog_id = request.args.get('id')
#    User.query.filter_by(id=id).first()

#    return render_template('blog.html',  )
 

if __name__ == '__main__':
    app.run()