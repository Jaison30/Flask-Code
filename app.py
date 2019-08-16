from flask import Flask, render_template, redirect, url_for, session, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, login_user, logout_user, UserMixin, current_user
import os

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)


login_manager = LoginManager()

login_manager.init_app(app) 


class User(db.Model, UserMixin):
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    email = db.Column(db.String(120))
    password = db.Column(db.String(80))

    def __repr__(self):
        return '<User %r>' % self.username


class Movies(db.Model):
    __tablename__ = 'movies'
    id = db.Column(db.Integer, primary_key=True)   
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'))
    title = db.Column(db.String(80))
    rating = db.Column(db.String(80))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect('/login?next=' + request.path)


@app.route("/")
@login_required
def Home():

    username = current_user.username      # logged in user name
    user_id = current_user.id             # logged in user id
    movies = Movies.query.filter_by(user_id=user_id)
    
    return render_template("index.html", username=username, movies=movies)


@app.route('/add-movie', methods=["GET", "POST"])
@login_required
def addMovie():
    username = current_user.username   
    if request.method == "POST":
        title = request.form['title']
        rating = request.form['rating']
        user_id = current_user.id

        movies = Movies(title=title.strip(), rating=rating, user_id=user_id)
        db.session.add(movies)
        db.session.commit()
        return redirect(url_for("Home"))

    return render_template('add-movies.html', username=username)


@app.route('/movie-rating/<movie_name>')
@login_required
def movieRating(movie_name):
    user_id = current_user.id           # logged in user id
    username = current_user.username    # logged in user name
    movie_rating = Movies.query.filter_by(user_id=user_id, title=str(movie_name))
    return render_template("movie-rating.html", username=username, movie_rating=movie_rating)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        uname = request.form["uname"]
        passw = request.form["passw"]
        
        user = User.query.filter_by(username=uname, password=passw).first()
        if user is not None:
            login_user(user)
            return redirect(url_for("Home"))
        else:
            error = 'Invalid credentials'
            return render_template("login.html", error=error)
    return render_template("login.html")


@app.route("/logout")
def logout():
    """Logout the current user."""
    logout_user()
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        uname = request.form['uname']
        mail = request.form['mail']
        passw = request.form['passw']

        user = User(username=uname, email=mail, password=passw)
        user.authenticated = True
        db.session.add(user)
        db.session.commit()

        return redirect(url_for("login"))
    return render_template("register.html")


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)