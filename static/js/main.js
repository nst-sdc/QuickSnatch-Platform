// Add smooth scroll behavior
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});

// Terminal functionality
document.addEventListener('DOMContentLoaded', function() {
    const terminals = document.querySelectorAll('.terminal');
    
    terminals.forEach(terminal => {
        const input = terminal.querySelector('.terminal-input');
        const output = terminal.querySelector('.terminal-output');
        const currentDir = terminal.dataset.currentDir || '/home/user';
        
        // Define available commands for the terminal
        const files = {
            '.secret_file': 'flag{quick_basics}',
            'secret.txt': 'flag{chmod_master}',
            'logs/server.log.gz': 'flag{grep_master_123}',
            'flag_service': 'flag{process_hunter}',
            'localhost:8080': 'flag{network_ninja}',
            'script_result.txt': 'flag{bash_wizard}',
            'mystery.tar.gz': 'flag{archive_explorer}',
            'PROCESS_ENV': 'flag{system_stalker}',
            'cron.log': 'flag{cron_master}',
            'encrypted_service': 'flag{ultimate_champion}'
        };

        const filePermissions = {
            'secret.txt': '000',  // Initially no permissions
            'documents/note.txt': '644',
            'downloads/script.sh': '755',
            'pictures/vacation.jpg': '644'
        };

        const helpText = {
            'general': `
╭──────────────── Quick-Snatch Help ────────────────╮
│ Available Commands:                                 │
│                                                    │
│  File Operations:                                  │
│    ls        - List directory contents             │
│    ls -a     - List all files (including hidden)   │
│    ls -l     - List with detailed information      │
│    cat       - Display file contents               │
│    pwd       - Print working directory             │
│    cd        - Change directory                    │
│    mkdir     - Create new directory                │
│    touch     - Create empty file                   │
│    rm        - Remove file                         │
│                                                    │
│  Permissions:                                      │
│    chmod     - Change file permissions             │
│                                                    │
│  System:                                           │
│    clear     - Clear terminal screen               │
│    date      - Show current date/time              │
│    whoami    - Show current user                   │
│    echo      - Display a message                   │
│                                                    │
│  Help:                                            │
│    help              - Show this help              │
│    help <command>    - Show command help           │
╰────────────────────────────────────────────────────╯`,
            'ls': `
Usage: ls [OPTION]
List directory contents
Options:
  -a    Show all files (including hidden)
  -l    Use long listing format`,
            'cat': `
Usage: cat [FILE]
Display file contents
Example: cat file.txt`,
            'chmod': `
Usage: chmod [MODE] FILE
Change file permissions
Mode: [user][group][others]
Example: chmod 644 file.txt
  6 (rw-) for user
  4 (r--) for group
  4 (r--) for others`
        };

        const levelConfig = {
            '3': {
                'find /logs -name "*.gz"': 'logs/server.log.gz',
                'zcat logs/server.log.gz': files['logs/server.log.gz']
            },
            '4': {
                'ps aux': 'user     1234  13.5  0.0   4567  1234 ?     S+   12:00  0:00 flag_service',
                'cat /proc/1234/cmdline': files['flag_service']
            },
            '5': {
                'netstat -tulpn': 'tcp     0    0 127.0.0.1:8080    0.0.0.0:*     LISTEN',
                'curl localhost:8080': files['localhost:8080']
            },
            '6': {
                './find_secret.sh': files['script_result.txt']
            },
            '7': {
                'tar xzf mystery.tar.gz': 'Extracting...',
                'cat flag.txt': files['mystery.tar.gz']
            },
            '8': {
                'ps aux | grep 13.37': 'user     5678  13.37 0.0   8901  5678 ?     S+   12:00  0:00 flag_process',
                'cat /proc/5678/environ': files['PROCESS_ENV']
            },
            '9': {
                'tail -f /var/log/cron.log': files['cron.log']
            },
            '10': {
                'netstat -tulpn': 'tcp     0    0 127.0.0.1:RANDOM_PORT    0.0.0.0:*     LISTEN',
                'nc localhost RANDOM_PORT': 'base64_encoded_flag',
                'echo "base64_encoded_flag" | base64 -d': files['encrypted_service']
            }
        };

        input.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                const command = this.value.trim();
                let response = '';
                const args = command.split(' ');
                const cmd = args[0];

                // Get terminal number from ID
                const terminalNum = terminal.querySelector('.terminal-input').id.split('-')[2];
                
                // Common commands for all levels
                switch(cmd) {
                    case 'clear':
                        output.innerHTML = '';
                        this.value = '';
                        return;
                    case 'date':
                        response = new Date().toString();
                        break;
                    case 'whoami':
                        response = 'user';
                        break;
                    case 'echo':
                        response = args.slice(1).join(' ');
                        break;
                    case 'pwd':
                        response = currentDir;
                        break;
                    case 'help':
                        if (args.length > 1 && helpText[args[1]]) {
                            response = helpText[args[1]];
                        } else {
                            response = helpText['general'];
                        }
                        break;
                }

                if (response) {
                    output.innerHTML += `<div class="terminal-prompt">${currentDir}$ ${command}</div>`;
                    output.innerHTML += `<div class="terminal-response">${response}</div>`;
                    this.value = '';
                    terminal.scrollTop = terminal.scrollHeight;
                    return;
                }

                // Level-specific commands
                if (levelConfig[terminalNum] && levelConfig[terminalNum][command]) {
                    response = levelConfig[terminalNum][command];
                } else {
                    // Handle default commands for each level
                    switch(terminalNum) {
                        case '1':
                            // Level 1 commands
                            switch(command) {
                                case 'ls':
                                    response = 'documents  downloads  pictures';
                                    break;
                                case 'ls -a':
                                    response = '.  ..  .secret_file  documents  downloads  pictures';
                                    break;
                                case 'ls -l':
                                    response = `total 3
drwxr-xr-x  2 user user  4096 Jan 15 12:00 documents
drwxr-xr-x  2 user user  4096 Jan 15 12:00 downloads
drwxr-xr-x  2 user user  4096 Jan 15 12:00 pictures`;
                                    break;
                                case 'cat .secret_file':
                                    response = files['.secret_file'];
                                    break;
                                default:
                                    if (cmd === 'cd') {
                                        response = 'Directory access restricted in this level';
                                    } else if (cmd === 'mkdir' || cmd === 'touch' || cmd === 'rm') {
                                        response = 'File modification restricted in this level';
                                    } else {
                                        response = 'Command not found: ' + command;
                                    }
                            }
                            break;
                        case '2':
                            // Level 2 commands
                            switch(command) {
                                case 'ls':
                                    response = 'secret.txt';
                                    break;
                                case 'ls -l':
                                    const perms = filePermissions['secret.txt'];
                                    response = perms === '000' ? 
                                        '----------  1 user user     20 Jan 15 12:00 secret.txt' :
                                        '-rw-r--r--  1 user user     20 Jan 15 12:00 secret.txt';
                                    break;
                                case 'chmod 644 secret.txt':
                                    filePermissions['secret.txt'] = '644';
                                    response = 'File permissions updated';
                                    break;
                                case 'cat secret.txt':
                                    if (filePermissions['secret.txt'] === '644') {
                                        response = files['secret.txt'];
                                    } else {
                                        response = 'Permission denied';
                                    }
                                    break;
                                default:
                                    if (cmd === 'cd') {
                                        response = 'Directory access restricted in this level';
                                    } else if (cmd === 'mkdir' || cmd === 'touch' || cmd === 'rm') {
                                        response = 'File modification restricted in this level';
                                    } else {
                                        response = 'Command not found: ' + command;
                                    }
                            }
                            break;
                        default:
                            response = 'Command not found: ' + command;
                    }
                }

                output.innerHTML += `<div class="terminal-prompt">${currentDir}$ ${command}</div>`;
                output.innerHTML += `<div class="terminal-response">${response}</div>`;
                this.value = '';
                terminal.scrollTop = terminal.scrollHeight;
            }
        });

        // Focus input when clicking anywhere in the terminal
        terminal.addEventListener('click', () => {
            input.focus();
        });

        // Add typing animation for terminal outputs
        function typeText(element, text, speed = 50) {
            let index = 0;
            element.innerHTML = '';
            
            function type() {
                if (index < text.length) {
                    element.innerHTML += text.charAt(index);
                    index++;
                    setTimeout(type, speed);
                } else {
                    // Add blinking cursor at the end
                    const cursor = document.createElement('span');
                    cursor.className = 'cursor';
                    element.appendChild(cursor);
                }
            }
            
            type();
        }

        // Initialize tooltips and popovers
        document.addEventListener('DOMContentLoaded', function() {
            // Initialize Bootstrap tooltips
            const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
            tooltipTriggerList.map(function (tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl);
            });

            // Initialize Bootstrap popovers
            const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
            popoverTriggerList.map(function (popoverTriggerEl) {
                return new bootstrap.Popover(popoverTriggerEl);
            });
        });
    });
});

// Add terminal styling
document.addEventListener('DOMContentLoaded', function() {
    const style = document.createElement('style');
    style.textContent = `
        .terminal {
            background-color: #1e1e1e;
            color: #f0f0f0;
            padding: 15px;
            font-family: 'Courier New', monospace;
            border-radius: 5px;
            margin-bottom: 20px;
            height: 400px;
            overflow-y: auto;
        }

        .terminal-prompt {
            color: #4CAF50;
            margin: 5px 0;
        }

        .terminal-response {
            color: #f0f0f0;
            white-space: pre;
            margin: 5px 0 15px 0;
        }

        .terminal-input {
            background-color: transparent;
            border: none;
            color: #f0f0f0;
            width: 100%;
            font-family: 'Courier New', monospace;
            outline: none;
        }

        .terminal-response:empty {
            display: none;
        }
    `;
    document.head.appendChild(style);
});

// Add loading animation for form submissions
document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', function() {
        const submitBtn = this.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...';
        }
    });
});

// Add fade-in animation for challenge cards
const observerOptions = {
    threshold: 0.1
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

document.querySelectorAll('.challenge-card').forEach(card => {
    card.style.opacity = '0';
    card.style.transform = 'translateY(20px)';
    card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
    observer.observe(card);
});

// Add typing animation for terminal outputs
function typeText(element, text, speed = 50) {
    let index = 0;
    element.innerHTML = '';
    
    function type() {
        if (index < text.length) {
            element.innerHTML += text.charAt(index);
            index++;
            setTimeout(type, speed);
        } else {
            // Add blinking cursor at the end
            const cursor = document.createElement('span');
            cursor.className = 'cursor';
            element.appendChild(cursor);
        }
    }
    
    type();
}

// Initialize tooltips and popovers
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize Bootstrap popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
});
