from datetime import date
from flask import Flask, abort, render_template, redirect, url_for, flash,request
import os
import smtplib
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_gravatar import Gravatar
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user,login_required
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from forms import CreatePostForm,RegisterForm,LoginForm,CommentForm
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
ckeditor = CKEditor(app)
Bootstrap5(app)

gravatar = Gravatar(app,
                    size=100,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)

# admin-only decorator
def admin_only(f):
    @wraps(f)
    def decorated_fuction(*args,**kwargs):
        if current_user.id!=1:
            return abort(403)
        return f(*args,**kwargs)
    return decorated_fuction

#Configure Flask-Login
login_manager=LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, int(user_id))

#DATABASE
class Base(DeclarativeBase):
    pass
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_URI")
db = SQLAlchemy(model_class=Base)
db.init_app(app)

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(100))
        
    #This will act like a List of BlogPost objects attached to each User. 
    #The "author" refers to the author property in the BlogPost class.
    posts = relationship("BlogPost", back_populates="author")

    # one author -> many comments
    comments=relationship('Comment',back_populates='comment_author')
    
class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
        
    # Created Foreign Key, "users.id" the users refers to the tablename of User.
    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    # Created a reference to the User object. The "posts" refers to the posts property in the User class.
    author = relationship("User", back_populates="posts")
    
    # relationship w comment table, one posts many comments
    comments=relationship('Comment',back_populates='parent_post')

    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)

class Comment(db.Model):
    __tablename__='comments'
    id:Mapped[int]=mapped_column(Integer,primary_key=True)

     #*******Child relationship*******#
    #"users.id" The users refers to the tablename of the Users class.
    #"comments" refers to the comments property in the User class.
    author_id:Mapped[int]=mapped_column(Integer,db.ForeignKey('users.id'))
    comment_author=relationship('User',back_populates='comments')

    post_id:Mapped[int]=mapped_column(Integer,db.ForeignKey('blog_posts.id'))
    parent_post=relationship('BlogPost',back_populates='comments')

    text:Mapped[str]=mapped_column(String(250),nullable=False)

with app.app_context():
    db.create_all()

@app.route('/')
def get_all_posts():
    result = db.session.execute(db.select(BlogPost))
    posts = result.scalars().all()
    return render_template("index.html", all_posts=posts,current_user=current_user)

#Werkzeug to hash the user's password when creating a new user.
@app.route('/register',methods=['GET','POST'])
def register():
    register_form=RegisterForm()
    if register_form.validate_on_submit():
        password=register_form.password.data
        hashed_password=generate_password_hash(password,'pbkdf2:sha256',8)
        new_user=User(
            email=register_form.email.data,
            password=hashed_password,
            name=register_form.name.data
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for("get_all_posts"))
    return render_template("register.html",form=register_form,current_user=current_user)


#Retrieved a user from the database based on their email. 
@app.route('/login',methods=['GET','POST'])
def login():
    login_form=LoginForm()
    if login_form.validate_on_submit():
        email=login_form.email.data
        password=login_form.password.data
        user=db.session.execute(db.select(User).where(User.email==email)).scalar()
        if user:
            if check_password_hash(user.password,password):
                login_user(user)
                return redirect(url_for('get_all_posts'))
            else:
                flash('Invalid password, Please try again.')
                return(redirect(url_for('login')))
        else:
            flash('Invalid email address, Please try again.')
            return(redirect(url_for('login')))

    return render_template("login.html",form=login_form,current_user=current_user)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))

# Only logged-in users to comment on posts
@app.route("/post/<int:post_id>",methods=['GET','POST'])
@login_required
def show_post(post_id):
    comment_form=CommentForm()
    requested_post = db.get_or_404(BlogPost, post_id)
    if comment_form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You need to login or register to comment.")
            return redirect(url_for("login"))
        new_comment = Comment(
            text=comment_form.comment.data,
            comment_author=current_user,
            parent_post=requested_post
        )
        db.session.add(new_comment)
        db.session.commit()
    return render_template("post.html", post=requested_post,current_user=current_user,form=comment_form)


# A decorator so only an admin user can create a new post
@app.route("/new-post", methods=["GET", "POST"])
@admin_only
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form,current_user=current_user)


# A decorator so only an admin user can edit a post
@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@admin_only
def edit_post(post_id):
    post = db.get_or_404(BlogPost, post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = current_user
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))
    return render_template("make-post.html", form=edit_form, is_edit=True,current_user=current_user)


# A decorator so only an admin user can delete a post
@app.route("/delete/<int:post_id>")
@admin_only
def delete_post(post_id):
    post_to_delete = db.get_or_404(BlogPost, post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


@app.route("/about")
def about():
    return render_template("about.html",current_user=current_user)


MAIL_ADDRESS = os.environ.get("EMAIL_KEY")
MAIL_APP_PW = os.environ.get("PASSWORD_KEY")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        data = request.form
        send_email(data["name"], data["email"], data["phone"], data["message"])
        return render_template("contact.html", msg_sent=True)
    return render_template("contact.html", msg_sent=False, current_user=current_user)


def send_email(name, email, phone, message):
    email_message = f"Subject:New Message\n\nName: {name}\nEmail: {email}\nPhone: {phone}\nMessage:{message}"
    with smtplib.SMTP("smtp.gmail.com") as connection:
        connection.starttls()
        connection.login(MAIL_ADDRESS, MAIL_APP_PW)
        connection.sendmail(MAIL_ADDRESS, MAIL_ADDRESS, email_message)

