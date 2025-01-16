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
        "ls": "logs  system.log",
        "ls -l": """total 8
drwxr-xr-x 2 user user 4096 Jan 16 14:49 logs
-rw-r--r-- 1 user user 2048 Jan 16 14:49 system.log""",
        "cd logs": "",
        "ls logs": "error.log  access.log  debug.log",
        "cat logs/error.log": """[ERROR] 14:30:00 - Critical system failure
[ERROR] 14:30:15 - Database connection lost
[ERROR] 14:30:30 - flag{grep_master_123} - Authentication failed
[ERROR] 14:30:45 - Memory allocation error""",
        "cat logs/access.log": """192.168.1.100 - - [16/Jan/2025:14:30:00 +0530] "GET /admin HTTP/1.1" 403 287
192.168.1.101 - - [16/Jan/2025:14:30:15 +0530] "POST /login HTTP/1.1" 401 401
192.168.1.102 - - [16/Jan/2025:14:30:30 +0530] "GET /flag HTTP/1.1" 404 289""",
        "cat logs/debug.log": """DEBUG: Initializing system components...
DEBUG: Loading configuration from /etc/config.json
DEBUG: Starting background services
DEBUG: flag{grep_master_123} found in memory
DEBUG: Cleanup routine started""",
        "cat system.log": """System startup completed
Services initialized
Background tasks running
Security audit in progress
No critical issues found""",
        "grep flag logs/error.log": "[ERROR] 14:30:30 - flag{grep_master_123} - Authentication failed",
        "grep -r flag logs": """logs/error.log:[ERROR] 14:30:30 - flag{grep_master_123} - Authentication failed
logs/debug.log:DEBUG: flag{grep_master_123} found in memory""",
        "grep flag": "ERROR: flag{grep_master_123} - Critical system error at 14:30:00",
        "help": """Available commands:
ls          - List directory contents
cd          - Change directory
cat         - Display file contents
grep        - Search for patterns
grep -r     - Search recursively""",
        "pwd": "/home/user"
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
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin""",
        "cat /proc/1337/status": """Name:   flag_service
State:  S (sleeping)
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
        "cat /proc/1337/cmdline": "flag_service--secret--flag=flag{process_hunter}"
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
    if current_user.is_authenticated:
        return redirect(url_for('level', level_number=current_user.current_level))
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
            return redirect(url_for('level', level_number=user.current_level))
        
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

@app.route('/level/<int:level_number>')
@login_required
def level(level_number):
    # Ensure user can't access levels beyond their current level
    if level_number > current_user.current_level:
        flash('You have not unlocked this level yet!', 'danger')
        return redirect(url_for('level', level_number=current_user.current_level))
    
    # Ensure level number is valid
    if level_number < 1 or level_number > 10:
        flash('Invalid level number!', 'danger')
        return redirect(url_for('level', level_number=current_user.current_level))
    
    return render_template(f'challenges/level_{level_number}.html', level=level_number)

@app.route('/leaderboard')
@login_required
def leaderboard():
    users = User.query.order_by(User.current_level.desc(), User.username).all()
    return render_template('leaderboard.html', users=users)

@app.route('/check_flag/<int:level>', methods=['POST'])
@login_required
def check_flag(level):
    if level != current_user.current_level:
        return jsonify({'success': False, 'message': 'Invalid level!'})
    
    submitted_flag = request.json.get('flag', '').strip()
    if not submitted_flag:
        return jsonify({'success': False, 'message': 'Please enter a flag'})

    expected_flag = ANSWERS.get(level)
    
    if submitted_flag == expected_flag:
        # Redirect to riddle instead of next level
        return jsonify({
            'success': True,
            'redirect': url_for('level_complete', level=level)
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Incorrect flag. Try again!'
        })

@app.route('/level/<int:level>/complete', methods=['GET', 'POST'])
@login_required
def level_complete(level):
    # Ensure user has actually completed the level
    if level != current_user.current_level:
        flash('Please complete the current level first!', 'error')
        return redirect(url_for('level', level_number=current_user.current_level))
    
    if request.method == 'POST':
        answer = request.form.get('answer', '').strip()
        if riddle_manager.check_answer(current_user.id, answer):
            # Clear the riddle and progress to next level
            riddle_manager.clear_riddle(current_user.id)
            current_user.current_level = level + 1
            db.session.commit()
            flash('Congratulations! You\'ve completed this level!', 'success')
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

class Sandbox:
    def __init__(self):
        self.setup_sandbox()

    def setup_sandbox(self):
        """Set up sandbox environment for each level"""
        self.environments = {
            1: {
                'files': {
                    '.hidden_flag': 'flag{basic_file_navigation}',
                    'README.txt': 'Welcome to level 1! Use ls and cat commands.',
                    'hint.txt': 'Remember to look for hidden files (ls -a)'
                }
            },
            2: {
                'files': {
                    'secret.txt': {'content': 'flag{permission_master}', 'mode': 0o000},
                    'instructions.txt': 'Change file permissions to read the flag',
                    'hint.txt': 'Use chmod to modify permissions'
                }
            },
            3: {
                'files': {
                    'logs/error.log': 'ERROR: Invalid flag attempt\nERROR: System crash\nflag{grep_master_2023}',
                    'logs/access.log': '192.168.1.1 - GET /admin [200]\n10.0.0.1 - POST /login [401]',
                    'logs/system.log': 'System started\nService initialized\nBackup completed'
                }
            },
            4: {
                'processes': [
                    {'pid': 1234, 'name': 'flag_service', 'cpu': 2.5, 'memory': 156,
                     'env': {'FLAG': 'flag{process_hunter}'}},
                    {'pid': 5678, 'name': 'nginx', 'cpu': 0.8, 'memory': 234},
                    {'pid': 9012, 'name': 'mysql', 'cpu': 1.2, 'memory': 456}
                ]
            },
            5: {
                'network': {
                    'connections': [
                        {'source': '127.0.0.1:12345', 'destination': '127.0.0.1:80', 'type': 'TCP', 'state': 'ESTABLISHED'},
                        {'source': '127.0.0.1:54321', 'destination': '127.0.0.1:1337', 'type': 'TCP', 'state': 'LISTEN'}
                    ],
                    'stats': {
                        'activeConnections': 2,
                        'listeningPorts': 3,
                        'bytesIn': '1.2MB',
                        'bytesOut': '0.8MB'
                    }
                }
            }
        }

    def execute_command(self, cmd, args, cwd):
        """Execute command in sandbox environment"""
        # Implement command execution logic here
        # Return a named tuple with stdout, stderr, returncode, and cwd
        pass

    def get_completions(self, partial, cwd):
        """Get possible completions for tab completion"""
        # Implement tab completion logic here
        # Return list of possible completions
        pass

    def get_process_list(self):
        """Get list of processes for level 4"""
        return self.environments[4]['processes']

    def get_network_stats(self):
        """Get network statistics for level 5"""
        return self.environments[5]['network']

# Initialize sandbox
sandbox = Sandbox()

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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=7771, debug=True)
