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
    1: "flag{file_explorer_pro}",
    2: "flag{chmod_master}",
    3: "flag{grep_master_123}",
    4: "flag{process_hunter}",
    5: "flag{network_ninja}",
    6: "flag{bash_wizard}",
    7: "flag{archive_master_explorer}",
    8: "flag{system_monitor_pro}",
    9: "flag{cr0n_master_detective}",
    10: "flag{ultimate_hacker_pro}"
}

# Command outputs for each level
COMMAND_OUTPUTS = {
    1: {
        "ls": "Documents  Downloads  Pictures  secret.txt",
        "ls -a": ".  ..  .bash_history  .bashrc  Documents  Downloads  Pictures  secret.txt",
        "ls -l": """total 28
drwxr-xr-x 2 user user 4096 Jan 16 14:44 Documents
drwxr-xr-x 2 user user 4096 Jan 16 14:44 Downloads
drwxr-xr-x 2 user user 4096 Jan 16 14:44 Pictures
-rw-r--r-- 1 user user   52 Jan 16 14:44 secret.txt""",
        "cat secret.txt": "flag{file_explorer_pro}",
        "pwd": "/home/user",
        "help": """Available commands:
ls      - List directory contents
ls -a   - List all files including hidden
ls -l   - List files in long format
cat     - Display file contents
pwd     - Print working directory""",
        "clear": ""
    },
    2: {
        "ls -l": """total 16
-rw-r--r-- 1 user user  158 Jan 16 14:30 instructions.txt
-rw-r--r-- 1 user user  237 Jan 16 14:30 permissions_info.txt
-rw------- 1 user user   21 Jan 16 14:30 secret.txt""",
        "cat instructions.txt": """Welcome to Level 2!
You need to understand file permissions to proceed.
Check permissions_info.txt for more details.""",
        "cat permissions_info.txt": """File permissions in Linux:
r (read) = 4
w (write) = 2
x (execute) = 1

Example: chmod 644 file
6 (rw-) for owner
4 (r--) for group
4 (r--) for others""",
        "chmod 644 secret.txt": "",
        "cat secret.txt": "flag{chmod_master}"
    },
    3: {
        "ls": "logs",
        "cd logs": "",
        "ls logs": "access.log.gz  error.log  system.log",
        "grep ERROR error.log": "ERROR: flag{grep_master_123} - Critical system error at 14:30:00",
        "zcat access.log.gz": """127.0.0.1 - - [16/Jan/2025:14:30:00 +0530] "GET /admin HTTP/1.1" 403 123
127.0.0.1 - - [16/Jan/2025:14:30:01 +0530] "GET /login HTTP/1.1" 200 456""",
        "cat system.log": """[2025-01-16 14:30:00] System started
[2025-01-16 14:30:01] User authentication successful
[2025-01-16 14:30:02] Database connection established"""
    },
    4: {
        "ps aux": """USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root         1  0.0  0.0   2384   668 ?        Ss   14:30   0:00 /sbin/init
root       423  0.0  0.0   2880   712 ?        S    14:30   0:00 sshd
user      1234  0.0  0.1   5984  1024 pts/0    S+   14:30   0:00 suspicious_process
user      1337  0.0  0.1  10240  1024 pts/0    S+   14:30   0:00 flag_service""",
        "ps -p 1337": """  PID TTY      STAT   TIME COMMAND
 1337 pts/0    S+     0:00 flag_service""",
        "cat /proc/1337/cmdline": "flag_service--secret--flag=flag{process_hunter}",
        "strings /proc/1337/environ": """SHELL=/bin/bash
PWD=/home/user
FLAG=flag{process_hunter}
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin"""
    },
    5: {
        "ifconfig": """eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 192.168.1.100  netmask 255.255.255.0  broadcast 192.168.1.255
        ether 00:11:22:33:44:55  txqueuelen 1000  (Ethernet)""",
        "netstat -tuln": """Active Internet connections (only servers)
Proto Recv-Q Send-Q Local Address           Foreign Address         State      
tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN     
tcp        0      0 0.0.0.0:1337            0.0.0.0:*               LISTEN""",
        "nc localhost 1337": "Welcome! The flag is: flag{network_ninja}",
        "curl localhost:1337": "Welcome! The flag is: flag{network_ninja}"
    },
    6: {
        "ls": "data.txt  process.sh",
        "cat data.txt": """user1,100
user2,200
user3,300
admin,flag{bash_wizard}
user4,400""",
        "cat process.sh": """#!/bin/bash
# This script processes data.txt
grep "admin" data.txt | cut -d',' -f2""",
        "chmod +x process.sh": "",
        "./process.sh": "flag{bash_wizard}"
    },
    7: {
        "ls -l mystery.tar.gz": "-rw-r--r-- 1 user user 2048 Jan 16 14:30 mystery.tar.gz",
        "file mystery.tar.gz": "mystery.tar.gz: gzip compressed data, from Unix, original size 10240",
        "tar xzf mystery.tar.gz": "",
        "ls -l": """total 8
-rw-r--r-- 1 user user 2048 Jan 16 14:30 mystery.tar.gz
-rw-r--r-- 1 user user 4096 Jan 16 14:30 secret.zip""",
        "file secret.zip": "secret.zip: Zip archive data, at least v2.0 to extract",
        "unzip secret.zip": """Archive:  secret.zip
  inflating: hidden.bz2""",
        "file hidden.bz2": "hidden.bz2: bzip2 compressed data, block size = 900k",
        "bzip2 -d hidden.bz2": "",
        "ls -l hidden": "-rw-r--r-- 1 user user 32 Jan 16 14:30 hidden",
        "cat hidden": "flag{archive_master_explorer}"
    },
    8: {
        "top": """top - 14:30:00 up 0 min,  1 user,  load average: 0.15, 0.05, 0.01
Tasks: 105 total,   1 running, 103 sleeping,   0 stopped,   1 zombie
%Cpu(s):  5.9 us,  2.0 sy,  0.0 ni, 91.2 id,  0.0 wa,  0.0 hi,  0.9 si,  0.0 st
MiB Mem :   7950.8 total,   7450.8 free,    300.0 used,    200.0 buff/cache
MiB Swap:   2048.0 total,   2048.0 free,      0.0 used.   7450.8 avail Mem 

  PID USER      PR  NI    VIRT    RES    SHR S  %CPU  %MEM     TIME+ COMMAND
 1337 user      20   0   10240   1024    512 R  13.37  0.1   0:01.23 suspicious_svc
  423 root      20   0    2880    712    644 S   0.0   0.0   0:00.00 sshd
    1 root      20   0    2384    668    612 S   0.0   0.0   0:00.00 init""",
        "ps aux | grep suspicious": """user     1337  13.37  0.1  10240  1024 pts/0    R    14:30   0:01 suspicious_svc --secret
user     1338   0.0  0.0   5504   832 pts/0    S+   14:30   0:00 grep suspicious""",
        "cat /proc/1337/status": """Name:   suspicious_svc
State:  R (running)
Tgid:   1337
Pid:    1337
PPid:   1
Uid:    1000    1000    1000    1000
Gid:    1000    1000    1000    1000
FDSize: 256
Groups: 4 24 27 30 46 113 128
VmPeak:    10240 kB
VmSize:    10240 kB
VmLck:         0 kB
VmRSS:      1024 kB""",
        "strings /proc/1337/environ": """SHELL=/bin/bash
PWD=/home/user
LOGNAME=user
HOME=/home/user
LANG=en_US.UTF-8
SECRET_FLAG=flag{system_monitor_pro}
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin""",
        "cat /proc/1337/cmdline": "suspicious_svc--secret--flag=flag{system_monitor_pro}"
    },
    9: {
        "systemctl status flag-service": """● flag-service.service - Flag Exposure Service
     Loaded: loaded (/etc/systemd/system/flag-service.service; enabled; vendor preset: enabled)
     Active: active (running) since Thu 2025-01-16 14:30:00 IST; 1min ago
   Main PID: 1234 (flag_exposer)
      Tasks: 1 (limit: 4915)
     Memory: 1.2M
     CGroup: /system.slice/flag-service.service
             └─1234 /usr/local/bin/flag_exposer --interval=60

Jan 16 14:30:00 quicksnatch systemd[1]: Started Flag Exposure Service.
Jan 16 14:30:00 quicksnatch flag_exposer[1234]: Service started, exposing flag every minute""",
        "crontab -l": """# Flag exposure cron job
* * * * * /usr/local/bin/expose_flag.sh
# Clean up exposed flags
*/2 * * * * /usr/local/bin/cleanup_flags.sh""",
        "cat /usr/local/bin/expose_flag.sh": """#!/bin/bash
# This script exposes the flag temporarily
echo "flag{cr0n_master_detective}" > /tmp/exposed_flag
logger "Flag has been exposed in /tmp/exposed_flag\"""",
        "tail -f /var/log/syslog": """Jan 16 14:30:00 quicksnatch systemd[1]: Started Flag Exposure Service.
Jan 16 14:30:00 quicksnatch flag_exposer[1234]: Service started
Jan 16 14:30:00 quicksnatch CRON[1235]: (user) CMD (/usr/local/bin/expose_flag.sh)
Jan 16 14:30:00 quicksnatch user: Flag has been exposed in /tmp/exposed_flag
Jan 16 14:30:00 quicksnatch CRON[1236]: (user) CMD (/usr/local/bin/cleanup_flags.sh)""",
        "cat /tmp/exposed_flag": "flag{cr0n_master_detective}",
        "journalctl -u flag-service": """-- Logs begin at Thu 2025-01-16 14:30:00 IST, end at Thu 2025-01-16 14:30:00 IST. --
Jan 16 14:30:00 quicksnatch systemd[1]: Started Flag Exposure Service.
Jan 16 14:30:00 quicksnatch flag_exposer[1234]: Service started, exposing flag every minute
Jan 16 14:30:00 quicksnatch flag_exposer[1234]: Flag value: flag{cr0n_master_detective}"""
    },
    10: {
        "netstat -tuln": """Active Internet connections (only servers)
Proto Recv-Q Send-Q Local Address           Foreign Address         State      
tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN     
tcp        0      0 0.0.0.0:31337           0.0.0.0:*               LISTEN     
tcp6       0      0 :::22                   :::*                    LISTEN     
tcp6       0      0 :::31337                :::*                    LISTEN""",
        "nc localhost 31337": """Welcome to the Flag Service!
Here's your encrypted flag:
SGVyZSdzIHlvdXIgZmxhZzogZmxhZ3t1bHRpbWF0ZV9oYWNrZXJfcHJvfQo=""",
        'echo "SGVyZSdzIHlvdXIgZmxhZzogZmxhZ3t1bHRpbWF0ZV9oYWNrZXJfcHJvfQo=" | base64 -d': "Here's your flag: flag{ultimate_hacker_pro}"
    }
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
            flash('Successfully logged in!', 'success')
            return redirect(url_for('challenge', level=user.current_level))
        
        flash('Invalid username or password', 'danger')
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
            flash('Correct! Moving to next level.', 'success')
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
            flash('Incorrect answer. Try again!', 'danger')
    
    return render_template(f'challenges/level_{level}.html')

@app.route('/leaderboard')
def leaderboard():
    users = User.query.order_by(User.current_level.desc(), User.last_submission).all()
    return render_template('leaderboard.html', users=users)

@app.route('/commands')
def commands():
    return render_template('commands.html')

@app.route('/execute_command', methods=['POST'])
@login_required
def execute_command():
    data = request.get_json()
    if not data or 'command' not in data or 'level' not in data:
        return jsonify({'error': 'Invalid request data'}), 400

    command = data['command'].strip()
    level = int(data['level'])

    # Get level-specific command outputs
    level_outputs = COMMAND_OUTPUTS.get(level, {})
    
    # First try exact command match
    output = level_outputs.get(command)
    
    if output is None:
        # If no exact match, try to match command with arguments
        # Split command and try common variations
        cmd_parts = command.split()
        base_cmd = cmd_parts[0]
        
        # Try to match commands with arguments
        for cmd_key in level_outputs.keys():
            if cmd_key.startswith(command):
                output = level_outputs[cmd_key]
                break
    
    if output is not None:
        return jsonify({'output': output})
    else:
        # Handle common commands
        if command == 'clear':
            return jsonify({'output': ''})
        elif command == 'help':
            # Get list of available commands for the level
            available_commands = '\n'.join(sorted(level_outputs.keys()))
            return jsonify({'output': f'Available commands:\n{available_commands}'})
        else:
            return jsonify({'error': f'Command not found: {command}'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=7771, debug=True)
