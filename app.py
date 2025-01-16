from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
import pytz
import os
import bcrypt

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ctf.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    current_level = db.Column(db.Integer, default=1)
    start_time = db.Column(db.DateTime, nullable=True)
    last_submission = db.Column(db.DateTime, nullable=True)

class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    level = db.Column(db.Integer, nullable=False)
    submitted_at = db.Column(db.DateTime, nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False)

# Challenge answers (in production, these should be stored securely)
ANSWERS = {
    1: "flag{quick_basics}",
    2: "flag{chmod_master}",
    3: "flag{grep_master_123}",
    4: "flag{process_hunter}",
    5: "flag{network_ninja}",
    6: "flag{bash_wizard}",
    7: "flag{archive_explorer}",
    8: "flag{system_stalker}",
    9: "flag{cron_master}",
    10: "flag{ultimate_champion}"
}

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user.password):
            login_user(user)
            if not user.start_time:
                user.start_time = datetime.now(pytz.UTC)
                db.session.commit()
            return redirect(url_for('challenge', level=user.current_level))
        
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Passwords do not match')
            return render_template('register.html')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return render_template('register.html')
        
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        user = User(username=username, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/challenge/<int:level>', methods=['GET', 'POST'])
@login_required
def challenge(level):
    if level > current_user.current_level:
        flash('You must complete previous levels first!')
        return redirect(url_for('challenge', level=current_user.current_level))
    
    if request.method == 'POST':
        answer = request.form.get('answer')
        if answer == ANSWERS.get(level):
            submission = Submission(
                user_id=current_user.id,
                level=level,
                submitted_at=datetime.now(pytz.UTC),
                is_correct=True
            )
            db.session.add(submission)
            if level == current_user.current_level:
                current_user.current_level += 1
            current_user.last_submission = datetime.now(pytz.UTC)
            db.session.commit()
            flash('Correct! Moving to next level.')
            return redirect(url_for('challenge', level=level+1))
        else:
            submission = Submission(
                user_id=current_user.id,
                level=level,
                submitted_at=datetime.now(pytz.UTC),
                is_correct=False
            )
            db.session.add(submission)
            db.session.commit()
            flash('Incorrect answer. Try again!')
    
    return render_template(f'challenges/level_{level}.html')

@app.route('/leaderboard')
def leaderboard():
    users = User.query.order_by(User.current_level.desc(), User.last_submission).all()
    return render_template('leaderboard.html', users=users)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
