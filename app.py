from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
import pytz
import os
import bcrypt
import shlex
from riddles import riddle_manager
import io
import math
import json
from config.flags import LEVEL_FLAGS

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
    level_times = db.relationship('LevelTime', backref='user', lazy=True)

    def get_level_time(self, level):
        level_time = LevelTime.query.filter_by(user_id=self.id, level=level).order_by(LevelTime.start_time.desc()).first()
        if level_time:
            return level_time.calculate_time_spent()
        return None

    def format_time_spent(self, level):
        time_spent = self.get_level_time(level)
        if not time_spent:
            return "Not started"
        
        total_seconds = int(time_spent.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"

class LevelTime(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    level = db.Column(db.Integer, nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=True)
    time_spent = db.Column(db.Interval, nullable=True)

    def calculate_time_spent(self):
        if self.end_time and self.start_time:
            return self.end_time - self.start_time
        elif self.start_time:
            return datetime.now(pytz.UTC) - self.start_time
        return None

class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    level = db.Column(db.Integer, nullable=False)
    submitted_at = db.Column(db.DateTime, nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False)

# Challenge answers (in production, these should be stored securely)
ANSWERS = {
    1: "flag{file_explorer_pro}",
    2: "flag{chmod_master}",
    3: "flag{grep_master_123}",
    4: "flag{process_hunter}",
    5: "flag{network_ninja}"
}

# Level sections and their corresponding hints
LEVEL_SECTIONS = {
    1: {
        'title': 'Hidden in Plain Sight',
        'description': """A secret is hidden in plain sight, though not immediately obvious. Can you find the hidden file within this directory and reveal its contents?

Hint: Sometimes what you can't see is just as important as what you can see.""",
        'curl_command': 'curl -s https://raw.githubusercontent.com/nst-sdc/cli_ctf/refs/heads/main/level1.sh | bash',
        'flag': 'QS{B3g1nn3r_Expl0r3r_2024}',
        'location_hint': {
            'title': 'The Silent Guardian',
            'description': """A silent guardian bides her time.   
Seek the lady, her story profound,  
A mother, a founder, forever renowned.  
Who is she, and what wisdom does she share?  
Her presence whispers a legacy rare.""",
            'code': 'HTML5GoldRush'
        }
    },
    2: {
        'title': 'The Hidden Path',
        'description': """A flag is tucked away, hidden from a simple list of files. It's said that a special directory hides the key. Can you navigate your way through and find what lies within and reveal the flag?

Hint: Some directories prefer to stay out of sight, but they can't hide from the right command.""",
        'curl_command': 'curl -s https://raw.githubusercontent.com/nst-sdc/cli_ctf/refs/heads/main/level2.sh | bash',
        'flag': 'QS{N3tw0rk_N1nj4_2024}',
        'location_hint': {
            'title': 'The Rising Temple',
            'description': """At the edge where paths converge and bend,  
A temple is rising, on which peace depends.  
Cradled by green, with a view so vast,  
A quiet refuge, where moments last.  

What place is blooming, serene and bright,  
A haven of calm, bathed in light?""",
            'code': 'CSSMysticTrail'
        }
    },
    3: {
        'title': 'Following the Links',
        'description': """A complex path leads to the flag. The flag itself is hidden in a file, and its path includes a symbolic link. Your job is to navigate through the file structure, follow the link and then obtain the flag.

Hint: Not all paths are what they seem. Some are just pointers to the real destination.""",
        'curl_command': 'curl -s https://raw.githubusercontent.com/nst-sdc/cli_ctf/refs/heads/main/level3.sh | bash',
        'flag': 'QS{Crypt0_M4st3r_2024}',
        'location_hint': {
            'title': 'The Humble Shade',
            'description': """A humble shade stands, quiet and blessed.  
In front of the place where smiles are made,  
A simple retreat, in the shade.  
What is this spot, serene and small,  
A peaceful corner, welcoming all?""",
            'code': 'DecodeTheDOM'
        }
    },
    4: {
        'title': 'Permission Granted',
        'description': """A direct path is needed, but you must use special permissions to read the content. You have to read the contents of the script to understand how to access the flag.

Hint: Sometimes you need the right permissions to access what you seek. The script holds the key to gaining access.""",
        'curl_command': 'curl -s https://raw.githubusercontent.com/nst-sdc/cli_ctf/refs/heads/main/level4.sh | bash',
        'flag': 'QS{B1n4ry_Wh1sp3r3r_2024}',
        'location_hint': {
            'title': 'The Sholay Scene',
            'description': """Right by the halls, where footsteps fade,  
A patch of green, like a scene in *Sholay*'s shade.  
Amidst the hustle, a quiet space,  
Like a tale, full of grace.  
What spot is this, where calm is found,  
A green escape, where peace resounds?""",
            'code': 'JSPathfinder'
        }
    },
    5: {
        'title': 'Decode the Message',
        'description': """A message has been encoded, and the key is available within the directory. You must use command line tools to decode the message. Explore the directory, find the message and decode it.

Hint: The message may look like gibberish, but with the right decoding tool, its true meaning will be revealed.""",
        'curl_command': 'curl -s https://raw.githubusercontent.com/nst-sdc/cli_ctf/refs/heads/main/level5.sh | bash',
        'flag': 'QS{Qu1ckSn4tch_Ch4mp10n_2024}',
        'location_hint': {
            'title': 'The Field Haven',
            'description': """Beside the field where the ball does fly,  
A quiet refuge, where footsteps lie.  
A hidden haven where knowledge aligns.  
What place is this, where echoes cease,  
A secret shelter, a moment of peace?""",
            'code': 'APIExplorer22'
        }
    }
}

# Location hints and their QR codes
LOCATION_HINTS = {
    1: {
        'title': 'The Silent Guardian',
        'description': """A silent guardian bides her time.   
Seek the lady, her story profound,  
A mother, a founder, forever renowned.  
Who is she, and what wisdom does she share?  
Her presence whispers a legacy rare.""",
        'code': 'HTML5GoldRush'
    },
    2: {
        'title': 'The Rising Temple',
        'description': """At the edge where paths converge and bend,  
A temple is rising, on which peace depends.  
Cradled by green, with a view so vast,  
A quiet refuge, where moments last.  

What place is blooming, serene and bright,  
A haven of calm, bathed in light?""",
        'code': 'CSSMysticTrail'
    },
    3: {
        'title': 'The Humble Shade',
        'description': """A humble shade stands, quiet and blessed.  
In front of the place where smiles are made,  
A simple retreat, in the shade.  
What is this spot, serene and small,  
A peaceful corner, welcoming all?""",
        'code': 'DecodeTheDOM'
    },
    4: {
        'title': 'The Sholay Scene',
        'description': """Right by the halls, where footsteps fade,  
A patch of green, like a scene in *Sholay*'s shade.  
Amidst the hustle, a quiet space,  
Like a tale, full of grace.  
What spot is this, where calm is found,  
A green escape, where peace resounds?""",
        'code': 'JSPathfinder'
    },
    5: {
        'title': 'The Field Haven',
        'description': """Beside the field where the ball does fly,  
A quiet refuge, where footsteps lie.  
A hidden haven where knowledge aligns.  
What place is this, where echoes cease,  
A secret shelter, a moment of peace?""",
        'code': 'APIExplorer22'
    },
    6: {
        'title': 'The Proud Monument',
        'description': """In front of the building where the name stands tall,  
A statue of pride, a symbol for all.  
Beside the waters, where ripples play,  
A quiet corner to end your day.  
What place is this, where stillness flows,  
A monument of pride where calmness grows?""",
        'code': 'APIExplorer22'
    },
    7: {
        'title': 'The Gateway',
        'description': """At the gate where daily steps converge,  
A threshold where journeys and minds emerge.    
Yet here, a stillness, softly embraced.  
What is this space, where time slows down,  
A fleeting moment, just beyond the town?""",
        'code': 'CodeQuest2025'
    },
    8: {
        'title': 'The Cozy Corner',
        'description': """Where the cobblestones meet the sea breeze, and the quiet hum of the city fades, 
a warm corner invites with the scent of roasted beans and a touch of something fresh from the oven, 
waiting to be discovered.""",
        'code': 'XtremeDebugger'
    },
    9: {
        'title': 'The Peaceful Path',
        'description': """Where worth rest and shadows blend,  
Beside the lot where pathways end.  
Facing knowledge, calm and wide,  
What is this place where peace resides?""",
        'code': 'BugBountyHunt'
    },
    10: {
        'title': 'The Student Hub',
        'description': """Where hunger meets a daily need,  
A bustling spot where students feed.  
Coupons in hand, the rule is clear,  
What is this place we hold so dear?""",
        'code': 'NirmaanKnights'
    },
    11: {
        'title': 'The Silent Space',
        'description': """Once alive with chatter and cheer,  
Now silent, its purpose unclear.  
A lone printer hums where meals once lay,  
What is this place of a bygone day?""",
        'code': 'NirmaanKnights'
    },
    12: {
        'title': 'The Serene Jewel',
        'description': """A heaven of calm, both deep and wide,
Where whispers and silence collide.
A place for the bold, a retreat for the still,
A shimmering jewel that tests your will.
What is this space, so serene and grand?""",
        'code': 'DOMVoyagers'
    },
    13: {
        'title': 'The Colorful Steps',
        'description': """Steps of color, bright and rare,
A lively path beyond compare.
A place of cheer, where stories unfold,
What is this spot so vibrant and bold?""",
        'code': 'TreasureInCode'
    },
    14: {
        'title': 'The Elegant Haven',
        'description': """Where whispers of luxury fill the air,
And every corner breathes beauty rare.
A place where elegance and taste collide,
With each sip, a world unfolds,
A treasure trove that quietly holds.
What is this space, where time stands still,
A haven of grace, both rich and tranquil?""",
        'code': 'BackendBandits'
    },
    15: {
        'title': 'The Arena Lot',
        'description': """Where the arena roars, but wheels stand still,
A parking lot where calmness fills.
In front of the game, where energy flows,
What is this spot where quietness grows?""",
        'code': 'FullStackFury'
    },
    16: {
        'title': 'The Guarded Gate',
        'description': """Entry and exits with proof in hand,
A threshold where all must make their stand.
Guarded and quiet, yet paths unfold,
Where is the spot, both strict and bold?""",
        'code': 'CipherCrafters'
    },
    17: {
        'title': 'The Patient Path',
        'description': """Patience Is All The Strength That Man Need's""",
        'code': 'FrontendFrenzy'
    }
}

# User progress tracking
user_progress = {}

class UserProgress:
    def __init__(self):
        self.current_level = 1
        self.at_hint = False
        self.completed_levels = set()

def get_user_progress(user_id='default'):
    if user_id not in user_progress:
        user_progress[user_id] = UserProgress()
    return user_progress[user_id]

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    if current_user.is_authenticated:
        progress = get_user_progress(current_user.id)
        return redirect(url_for('level', level_number=progress.current_level))
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
            flash('Successfully logged in!', 'success')
            progress = get_user_progress(user.id)
            return redirect(url_for('level', level_number=progress.current_level))
        
        flash('Invalid username or password', 'danger')
        print("Thios")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Passwords do not match', 'warning')
            return render_template('register.html')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'warning')
            return render_template('register.html')
        
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        user = User(username=username, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/level/<int:level_number>')
def level(level_number):
    progress = get_user_progress(current_user.id)
    
    # If user is at hint page, redirect back to hint
    if progress.at_hint:
        return redirect(url_for('location_hint', level=progress.current_level))
    
    # Ensure level number is valid
    if level_number < 1 or level_number > 17:
        flash('Invalid level number!', 'danger')
        return redirect(url_for('level', level_number=progress.current_level))
    
    # Only allow access to current level
    if level_number != progress.current_level:
        flash('You can only access your current level!', 'danger')
        return redirect(url_for('level', level_number=progress.current_level))
    
    level_data = LEVEL_SECTIONS.get(level_number, {})
    return render_template(f'challenges/level_{level_number}.html', 
                         level=level_number,
                         level_data=level_data)

@app.route('/leaderboard')
@login_required
def leaderboard():
    users = User.query.order_by(User.current_level.desc(), User.username).all()
    return render_template('leaderboard.html', users=users)

@app.route('/check_flag/<int:level>', methods=['POST'])
def check_flag(level):
    progress = get_user_progress(current_user.id)
    data = request.get_json()
    submitted_flag = data.get('flag', '').strip()
    
    if not submitted_flag:
        return jsonify({'success': False, 'message': 'No flag submitted'})
    
    if level not in LEVEL_FLAGS:
        return jsonify({'success': False, 'message': 'Invalid level'})
    
    if submitted_flag == LEVEL_FLAGS[level]:
        progress.at_hint = True  # Mark that user should be at hint page
        return jsonify({
            'success': True,
            'message': 'Flag correct! Proceed to find the location.',
            'redirect': f'/location_hint/{level}'
        })
    
    return jsonify({
        'success': False,
        'message': 'Incorrect flag. Try again!'
    })

@app.route('/level/<int:level>/complete', methods=['GET', 'POST'])
@login_required
def level_complete(level):
    # Ensure user has actually completed the level
    if level != get_user_progress(current_user.id).current_level:
        flash('Please complete the current level first!', 'error')
        return redirect(url_for('level', level_number=get_user_progress(current_user.id).current_level))
    
    if request.method == 'POST':
        answer = request.form.get('answer', '').strip()
        if riddle_manager.check_answer(current_user.id, answer):
            # Clear the riddle and progress to next level
            riddle_manager.clear_riddle(current_user.id)
            progress = get_user_progress(current_user.id)
            progress.current_level = level + 1
            db.session.commit()
            flash('Congratulations! You\'ve completed this level!', 'success')
            
            # If user completed level 5, redirect to congratulations page
            if level == 5:
                return redirect(url_for('congratulations'))
                
            return redirect(url_for('level', level_number=level + 1))
        else:
            riddle = riddle_manager.user_riddles[current_user.id]['current_riddle']['riddle']
            flash('Incorrect answer. Try again!', 'error')
            return render_template('riddle.html', level=level, riddle=riddle, 
                                error="Incorrect answer. Try again!")

    # Check if user already has a riddle assigned
    if current_user.id in riddle_manager.user_riddles and \
       riddle_manager.user_riddles[current_user.id].get('level') == level:
        riddle = riddle_manager.user_riddles[current_user.id]['current_riddle']['riddle']
    else:
        # Assign a new riddle for this level
        riddle_data = riddle_manager.assign_riddle(current_user.id, level)
        riddle = riddle_data['riddle']
    
    return render_template('riddle.html', level=level, riddle=riddle)

@app.route('/commands')
def commands():
    return render_template('commands.html')

@app.route('/execute_command', methods=['POST'])
@login_required
def execute_command():
    data = request.get_json()
    command = data.get('command')
    cwd = data.get('cwd', '/home/user')
    
    if not command:
        return jsonify({'error': 'No command provided'})

    try:
        # Split command into parts
        parts = shlex.split(command)
        cmd = parts[0]
        args = parts[1:] if len(parts) > 1 else []

        # Handle built-in commands
        if cmd == 'cd':
            if not args:
                new_cwd = '/home/user'
            else:
                new_cwd = os.path.abspath(os.path.join(cwd, args[0]))
            return jsonify({
                'output': '',
                'cwd': new_cwd
            })
        
        # Execute command in sandbox environment
        result = sandbox.execute_command(cmd, args, cwd)
        
        return jsonify({
            'output': result.stdout,
            'error': result.stderr if result.returncode != 0 else None,
            'cwd': result.cwd
        })

    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/tab_complete', methods=['POST'])
def tab_complete():
    data = request.get_json()
    partial = data.get('partial', '')
    cwd = data.get('cwd', '/home/user')

    try:
        # Get possible completions based on current directory and partial input
        completions = sandbox.get_completions(partial, cwd)
        return jsonify({'matches': completions})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/get_processes', methods=['GET'])
def get_processes():
    """Get process information for level 4"""
    try:
        processes = sandbox.get_process_list()
        return jsonify(processes)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/get_network_stats', methods=['GET'])
def get_network_stats():
    """Get network statistics for level 5"""
    try:
        stats = sandbox.get_network_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)})

class CommandResult:
    def __init__(self, stdout="", stderr="", returncode=0):
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode

class BashCompiler:
    def __init__(self):
        self.command_history = []

    def execute_command(self, command, level):
        base_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "challenges/bash_compiler")

        # Level 1 - File Explorer
        if level == 1:
            # Basic file listing
            if command == "ls":
                return self.CommandResult(stdout="Documents/  Downloads/  Pictures/  README.txt  hello.sh")
            elif command == "ls -a":
                return self.CommandResult(stdout=".  ..  .bash_history  .bashrc  .hidden_flag.txt  Documents/  Downloads/  Pictures/  README.txt  hello.sh")
            elif command == "ls -l":
                return self.CommandResult(stdout="""total 28
drwxr-xr-x 2 user user 4096 Jan 18 05:55 Documents
drwxr-xr-x 2 user user 4096 Jan 18 05:55 Downloads
drwxr-xr-x 2 user user 4096 Jan 18 05:55 Pictures
-rw-r--r-- 1 user user  158 Jan 18 05:55 README.txt
-rwxr-xr-x 1 user user  237 Jan 18 05:55 hello.sh""")
            elif command == "ls -la":
                return self.CommandResult(stdout="""total 48
drwxr-xr-x 6 user user 4096 Jan 18 05:55 .
drwxr-xr-x 3 user user 4096 Jan 18 05:55 ..
-rw------- 1 user user    0 Jan 18 05:55 .bash_history
-rw-r--r-- 1 user user  220 Jan 18 05:55 .bashrc
-rw-r--r-- 1 user user   52 Jan 18 05:55 .hidden_flag.txt
drwxr-xr-x 2 user user 4096 Jan 18 05:55 Documents
drwxr-xr-x 2 user user 4096 Jan 18 05:55 Downloads
drwxr-xr-x 2 user user 4096 Jan 18 05:55 Pictures
-rw-r--r-- 1 user user  158 Jan 18 05:55 README.txt
-rwxr-xr-x 1 user user  237 Jan 18 05:55 hello.sh""")
            
            # Directory listings
            elif command == "ls Documents":
                return self.CommandResult(stdout="notes.txt  project.md")
            elif command == "ls Downloads":
                return self.CommandResult(stdout="archive.zip  data.csv")
            elif command == "ls Pictures":
                return self.CommandResult(stdout="profile.jpg  screenshot.png")
            
            # File contents
            elif command == "cat README.txt":
                return self.CommandResult(stdout="Welcome to Level 1!\nTry using different ls commands to find hidden files.\nHint: Some files might be hidden with a dot (.)")
            elif command == "cat hello.sh":
                return self.CommandResult(stdout="""#!/bin/bash
# QuickSnatch Bash Challenge Level 1
# Find the hidden flag!

echo "Welcome to Level 1"
echo "Can you find the hidden flag?"

# Hidden flag: QUICK{b4sh_c0mp1l3r_b3g1nn3r}

function check_flag() {
    echo "Checking for flag..."
}

check_flag""")
            elif command == "cat .hidden_flag.txt":
                return self.CommandResult(stdout="Good job finding this hidden file!\nThe flag is: QUICK{b4sh_c0mp1l3r_b3g1nn3r}")
            elif command == "cat .bashrc":
                return self.CommandResult(stdout=r"""# ~/.bashrc
alias ls='ls --color=auto'
alias grep='grep --color=auto'
PS1='[\u@\h \W]\$ '""")
            
            # Navigation and info commands
            elif command == "pwd":
                return self.CommandResult(stdout="/home/user")
            elif command == "whoami":
                return self.CommandResult(stdout="user")
            elif command == "id":
                return self.CommandResult(stdout="uid=1000(user) gid=1000(user) groups=1000(user)")
            elif command == "date":
                return self.CommandResult(stdout="Sat Jan 18 05:55:53 IST 2025")
            elif command == "help":
                return self.CommandResult(stdout="""Available commands:
ls          - List directory contents
ls -a       - List all files including hidden
ls -l       - List files in long format
ls -la      - List all files in long format
cat         - Display file contents
pwd         - Print working directory
whoami      - Print current user
id          - Print user ID info
date        - Show current date/time""")
            elif command == "clear":
                return self.CommandResult(stdout="")
            
            # Error cases
            elif command.startswith("cd "):
                return self.CommandResult(stderr="cd: Permission denied", returncode=1)
            elif command.startswith("rm "):
                return self.CommandResult(stderr="rm: Permission denied", returncode=1)
            elif command.startswith("mv "):
                return self.CommandResult(stderr="mv: Permission denied", returncode=1)
            elif command.startswith("cp "):
                return self.CommandResult(stderr="cp: Permission denied", returncode=1)
            elif command.startswith("mkdir "):
                return self.CommandResult(stderr="mkdir: Permission denied", returncode=1)
            elif command.startswith("touch "):
                return self.CommandResult(stderr="touch: Permission denied", returncode=1)
            else:
                return self.CommandResult(stderr=f"Command not found: {command}", returncode=1)

        # Level 2 - Permissions
        elif level == 2:
            if command == "ls":
                return self.CommandResult(stdout="instructions.txt  permissions_info.txt  secret.txt")
            elif command == "ls -l":
                return self.CommandResult(stdout="""total 16
-rw-r--r-- 1 user user  158 Jan 18 05:55 instructions.txt
-rw-r--r-- 1 user user  237 Jan 18 05:55 permissions_info.txt
-rw------- 1 user user   21 Jan 18 05:55 secret.txt""")
            elif command == "cat instructions.txt":
                return self.CommandResult(stdout="""Welcome to Level 2!
You need to understand file permissions to proceed.
Check permissions_info.txt for more details.""")
            elif command == "cat permissions_info.txt":
                return self.CommandResult(stdout="""File permissions in Linux:
r (read) = 4
w (write) = 2
x (execute) = 1

Example: chmod 644 file
6 (rw-) for owner
4 (r--) for group
4 (r--) for others""")
            elif command == "chmod 644 secret.txt":
                return self.CommandResult(stdout="")
            elif command == "cat secret.txt":
                if "chmod 644 secret.txt" in self.command_history:
                    return self.CommandResult(stdout="flag{chmod_master}")
                else:
                    return self.CommandResult(stderr="Permission denied", returncode=1)

        # Level 3 - Log Explorer
        elif level == 3:
            if command == "ls":
                return self.CommandResult(stdout="logs  system.log")
            elif command == "ls logs":
                return self.CommandResult(stdout="error.log  access.log  debug.log")
            elif command == "cat logs/error.log":
                return self.CommandResult(stdout="""[ERROR] 14:30:00 - Critical system failure
[ERROR] 14:30:15 - Database connection lost
[ERROR] 14:30:30 - flag{grep_master_123} - Authentication failed
[ERROR] 14:30:45 - Memory allocation error""")
            elif command == "cat logs/access.log":
                return self.CommandResult(stdout="""192.168.1.100 - - [16/Jan/2025:14:30:00 +0530] "GET /admin HTTP/1.1" 403 287
192.168.1.101 - - [16/Jan/2025:14:30:15 +0530] "POST /login HTTP/1.1" 401 401
192.168.1.102 - - [16/Jan/2025:14:30:30 +0530] "GET /flag HTTP/1.1" 404 289""")
            elif command == "cat logs/debug.log":
                return self.CommandResult(stdout="""DEBUG: Initializing system components...
DEBUG: Loading configuration from /etc/config.json
DEBUG: Starting background services
DEBUG: flag{grep_master_123} found in memory
DEBUG: Cleanup routine started""")
            elif command == "grep -r flag logs":
                return self.CommandResult(stdout="""logs/error.log:[ERROR] 14:30:30 - flag{grep_master_123} - Authentication failed
logs/debug.log:DEBUG: flag{grep_master_123} found in memory""")

        # Level 4 - Process Hunter
        elif level == 4:
            if command == "ps aux":
                return self.CommandResult(stdout="""USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root         1  0.0  0.0   2384   668 ?        Ss   14:30   0:00 /sbin/init
root       423  0.0  0.0   2880   712 ?        S    14:30   0:00 sshd
user      1234  0.0  0.1   5984  1024 pts/0    S+   14:30   0:00 suspicious_process
user      1337  0.0  0.1  10240  1024 pts/0    S+   14:30   0:00 flag_service""")
            elif command == "cat /proc/1337/cmdline":
                return self.CommandResult(stdout="flag_service--secret--flag=flag{process_hunter}")
            elif command == "strings /proc/1337/environ":
                return self.CommandResult(stdout="""SHELL=/bin/bash
PWD=/home/user
FLAG=flag{process_hunter}
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin""")

        # Level 5 - Network Ninja
        elif level == 5:
            if command == "netstat -tuln":
                return self.CommandResult(stdout="""Active Internet connections (only servers)
Proto Recv-Q Send-Q Local Address           Foreign Address         State      
tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN     
tcp        0      0 0.0.0.0:1337            0.0.0.0:*               LISTEN""")
            elif command == "nc localhost 1337" or command == "curl localhost:1337":
                return self.CommandResult(stdout="Welcome! The flag is: flag{network_ninja}")

        # Default error for unknown commands
        return self.CommandResult(stderr=f"Command not found: {command}", returncode=1)

    def get_completions(self, partial, cwd):
        """Get possible completions for tab completion"""
        # Implement tab completion logic here
        # Return list of possible completions
        pass

    def get_process_list(self):
        """Get list of processes for level 4"""
        # Implement process listing logic here
        pass

    def get_network_stats(self):
        """Get network statistics for level 5"""
        # Implement network statistics logic here
        pass

# Initialize sandbox
sandbox = BashCompiler()

@app.route('/get_hint', methods=['POST'])
@login_required
def get_hint():
    hint = riddle_manager.get_hint(current_user.id)
    return jsonify({'hint': hint})

# Binary Analysis Level Routes
@app.route('/get_binary_data')
def get_binary_data():
    if not session.get('level') == 7:
        return jsonify({'error': 'Unauthorized'}), 403
        
    # Generate a binary file with embedded flag
    binary_data = generate_binary_with_flag()
    return send_file(
        io.BytesIO(binary_data),
        mimetype='application/octet-stream'
    )

@app.route('/analyze_binary', methods=['POST'])
def analyze_binary():
    if not session.get('level') == 7:
        return jsonify({'error': 'Unauthorized'}), 403
        
    tool = request.json.get('tool')
    results = []
    
    if tool == 'find-strings':
        results = analyze_strings()
    elif tool == 'check-headers':
        results = analyze_headers()
    elif tool == 'entropy-analysis':
        results = analyze_entropy()
        
    return jsonify(results)

def generate_binary_with_flag():
    # Create a simple ELF binary structure
    binary = bytearray()
    
    # ELF Header
    binary.extend(b'\x7fELF')  # Magic number
    binary.extend(b'\x02')     # 64-bit
    binary.extend(b'\x01')     # Little endian
    binary.extend(b'\x01')     # Version
    binary.extend(b'\x00' * 9) # Padding
    
    # Embed the flag in a way that requires analysis
    flag = "flag{b1n4ry_4n4ly515_pr0}"
    encoded_flag = ''.join(chr((ord(c) + 13) % 256) for c in flag)
    binary.extend(encoded_flag.encode())
    
    # Add some decoy strings
    decoys = [
        b"This is not the flag you're looking for",
        b"Try harder!",
        b"Almost there...",
        b"Look deeper into the binary",
        b"Remember to check the headers"
    ]
    
    for decoy in decoys:
        binary.extend(decoy)
        binary.extend(b'\x00' * 16)
    
    return bytes(binary)

def analyze_strings():
    binary = generate_binary_with_flag()
    strings = []
    current_string = bytearray()
    
    for byte in binary:
        if 32 <= byte <= 126:  # Printable ASCII
            current_string.append(byte)
        elif current_string:
            if len(current_string) >= 4:  # Only include strings of 4+ chars
                strings.append(current_string.decode())
            current_string = bytearray()
    
    return [
        {
            'type': 'Strings Analysis',
            'content': '\n'.join(strings)
        }
    ]

def analyze_headers():
    binary = generate_binary_with_flag()
    header_info = []
    
    # Basic header analysis
    if binary.startswith(b'\x7fELF'):
        header_info.append("File Type: ELF Binary")
        header_info.append(f"Architecture: {'64-bit' if binary[4] == 2 else '32-bit'}")
        header_info.append(f"Endianness: {'Little Endian' if binary[5] == 1 else 'Big Endian'}")
    
    return [
        {
            'type': 'Header Analysis',
            'content': '\n'.join(header_info)
        }
    ]

def analyze_entropy():
    binary = generate_binary_with_flag()
    chunk_size = 16
    chunks = [binary[i:i+chunk_size] for i in range(0, len(binary), chunk_size)]
    
    entropy_data = []
    for i, chunk in enumerate(chunks):
        # Calculate Shannon entropy for the chunk
        entropy = 0
        byte_count = {}
        for byte in chunk:
            byte_count[byte] = byte_count.get(byte, 0) + 1
        
        for count in byte_count.values():
            probability = count / len(chunk)
            entropy -= probability * math.log2(probability)
            
        entropy_data.append(f"Chunk {i}: {entropy:.2f}")
    
    return [
        {
            'type': 'Entropy Analysis',
            'content': '\n'.join(entropy_data)
        }
    ]

@app.route('/terminal/<int:level>')
@login_required
def terminal(level):
    if level < 1 or level > 5 or level > get_user_progress(current_user.id).current_level:
        return redirect(url_for('level', level_number=get_user_progress(current_user.id).current_level))
    
    # Start timing for this level if not already started
    level_time = LevelTime.query.filter_by(
        user_id=current_user.id, 
        level=level, 
        end_time=None
    ).first()
    
    if not level_time:
        level_time = LevelTime(
            user_id=current_user.id,
            level=level,
            start_time=datetime.now(pytz.UTC)
        )
        db.session.add(level_time)
        db.session.commit()
    
    time_spent = current_user.format_time_spent(level)
    return render_template(f'level{level}_terminal.html', level=level, time_spent=time_spent)

@app.route('/level_time/<int:level>')
@login_required
def level_time(level):
    time_spent = current_user.format_time_spent(level)
    return jsonify({'time_spent': time_spent})

@app.route('/challenges/level<int:level>/level_info.json')
@login_required
def level_info(level):
    try:
        with open(f'challenges/level{level}/level_info.json', 'r') as f:
            return jsonify(json.load(f))
    except FileNotFoundError:
        return jsonify({
            'level': level,
            'title': 'Unknown Level',
            'description': 'Level information not available.',
            'prompt': 'user@quicksnatch',
            'files': {},
            'hints': ['Level information not available']
        })

@app.route('/location_hint/<int:level>')
@login_required
def location_hint(level):
    progress = get_user_progress(current_user.id)
    
    # Only allow access to current level's hint
    if level != progress.current_level:
        return redirect(url_for('level', level_number=progress.current_level))
    
    # If not marked as at_hint, redirect to level
    if not progress.at_hint:
        return redirect(url_for('level', level_number=progress.current_level))
    
    hint_data = LOCATION_HINTS.get(level, {})
    
    return render_template('location_hint.html', 
                         level=level,
                         hint_title=hint_data.get('title', ''),
                         location_hint=hint_data.get('description', ''))

@app.route('/verify_location/<int:level>', methods=['POST'])
@login_required
def verify_location(level):
    progress = get_user_progress(current_user.id)
    data = request.get_json()
    submitted_code = data.get('code', '').strip()
    
    if not submitted_code:
        return jsonify({
            'success': False,
            'message': 'No location code provided'
        })
    
    hint_data = LOCATION_HINTS.get(level)
    if not hint_data:
        return jsonify({
            'success': False,
            'message': 'Invalid level'
        })
    
    expected_code = hint_data['code']
    if submitted_code == expected_code:
        # Mark current level as completed
        progress.completed_levels.add(level)
        progress.at_hint = False  # Reset hint status
        
        # Move to next level
        next_level = level + 1
        if next_level > 17:
            return jsonify({
                'success': True,
                'message': 'Congratulations! You have completed all levels!',
                'redirect': '/congratulations'
            })
            
        progress.current_level = next_level
        return jsonify({
            'success': True,
            'message': f'Location verified! Moving to level {next_level}',
            'redirect': f'/level/{next_level}'
        })
    
    return jsonify({
        'success': False,
        'message': 'Incorrect location code. Try again!'
    })

@app.route('/congratulations')
def congratulations():
    return render_template('congratulations.html')

@app.route('/levels')
def levels():
    progress = get_user_progress()
    return render_template('levels.html', progress=progress)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=7771, debug=True)
