from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:Welcome1@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(500))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self,username,password):
        self.username = username
        self.password = password


@app.route('/')
def index():
    return redirect('/blog')

@app.route('/blog', methods=['POST', 'GET'])
def blog():

    blog_posts = Blog.query.all()
    return render_template('/blog.html', blog_posts=blog_posts)

def is_empty(text):
    if not len(text) > 0:
        return True
    else:
        return False

def valid_length(text):
    if len(text) < 3 or len(text) > 20:
        return False
    else:
        return True

@app.route('/login', methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            session['email'] = email
            flash('Logged in')
            return redirect('/')
        else:
            flash('User password doesn\'t match','error' )

    return render_template('login.html')

@app.route('/signup', methods = ['POST', 'GET'])
def register():
    #Validation
    username_error = ''
    password_error =''
    verify_error = ''
    

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        #Username validation
        if is_empty(username) or not valid_length(username):
            username_error = 'That\'s not a valid username'
        #Password validation   
        if is_empty(password) or not valid_length(password):
            password_error = 'That\'s not a valid password'
        #Verify password validation
        if is_empty(verify) or password != verify:
            verify_error = 'Passwords don\'t match'

    existing_user = User.query.filter_by(username=username).first()

    if request.method == 'POST' and not username_error and not password_error and not verify_error and not username_error and not existing_user:       
        new_user = User(username, password)
        db.session.add(new_user)
        db.session.commit()
        session['username'] = username
        return redirect('/')
    else:
        #TODO - user already exist
        return render_template('/signup.html', username_error = username_error, password_error = password_error, verify_error = verify_error)


@app.route('/newpost', methods=['POST','GET'])
def new_blog():

    error_title = "Please fill in the title"
    error_body = "Please fill in the body"
    empty_title_error = ''
    empty_body_error = ''
    owner = User.query.filter_by(username=session['username']).first()

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        if is_empty(title):
            empty_title_error = error_title
        if is_empty(body):
            empty_body_error = error_body

    if request.method == 'POST' and empty_body_error == '' and empty_title_error == '':
        new_post = Blog(title,body,owner)
        db.session.add(new_post)
        db.session.commit()
        post_id = Blog.query.get(new_post.id)
        return render_template('post.html', post_id=post_id)
    else:
        return render_template('/newpost.html',empty_title_error=empty_title_error,empty_body_error=empty_body_error)


@app.route('/post')
def post():

    id = request.args.get('id')
    post_id = Blog.query.get(id)
    return render_template('/post.html',post_id=post_id)

if __name__ == '__main__':
    app.run()

