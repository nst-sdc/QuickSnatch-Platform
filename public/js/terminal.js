class TerminalEmulator {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.isFullscreen = false;
        this.currentDir = '/home/user';
        this.processes = [
            { pid: 1234, cmd: 'flag_server', port: 8080 },
            { pid: 5678, cmd: 'challenge_service', port: 9999 }
        ];
        this.files = {
            '/home/user': {
                '.flag.txt': 'flag{quick_basics}',
                'level2': {
                    'secret.txt': { content: 'flag{chmod_master}', permissions: '600' }
                },
                'level3': {
                    'file1.txt': 'random content',
                    'file2.txt': 'flag{grep_master_123}',
                    'file3.txt': 'more content'
                },
                'level6': {
                    'large_file.txt': 'flag{bash_wizard}',
                    'small_file.txt': 'not here'
                },
                'level7': {
                    'archive.tar': 'flag{archive_explorer}'
                }
            }
        };
        this.setupTerminal();
    }

    setupTerminal() {
        // Create terminal UI
        this.terminal = document.createElement('div');
        this.terminal.className = 'terminal';
        this.output = document.createElement('div');
        this.output.className = 'terminal-output';
        this.input = document.createElement('input');
        this.input.className = 'terminal-input';
        this.input.setAttribute('type', 'text');
        
        this.terminal.appendChild(this.output);
        this.terminal.appendChild(this.input);
        this.container.appendChild(this.terminal);

        // Setup event listeners
        this.input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                const command = this.input.value;
                this.executeCommand(command);
                this.input.value = '';
            }
        });

        // Add fullscreen button
        this.fullscreenBtn = document.createElement('button');
        this.fullscreenBtn.innerText = '⛶';
        this.fullscreenBtn.className = 'fullscreen-btn';
        this.fullscreenBtn.onclick = () => this.toggleFullscreen();
        this.container.appendChild(this.fullscreenBtn);

        this.printWelcome();
    }

    toggleFullscreen() {
        if (!this.isFullscreen) {
            if (this.container.requestFullscreen) {
                this.container.requestFullscreen();
            }
            this.isFullscreen = true;
            this.fullscreenBtn.innerText = '⮌';
        } else {
            if (document.exitFullscreen) {
                document.exitFullscreen();
            }
            this.isFullscreen = false;
            this.fullscreenBtn.innerText = '⛶';
        }
    }

    executeCommand(cmd) {
        const parts = cmd.trim().split(' ');
        const command = parts[0];
        const args = parts.slice(1);

        this.printCommand(cmd);

        switch (command) {
            case 'ls':
                this.ls(args);
                break;
            case 'cd':
                this.cd(args[0]);
                break;
            case 'cat':
                this.cat(args[0]);
                break;
            case 'chmod':
                this.chmod(args[0], args[1]);
                break;
            case 'ps':
                this.ps();
                break;
            case 'top':
                this.top();
                break;
            case 'netstat':
                this.netstat();
                break;
            case 'grep':
                this.grep(args);
                break;
            case 'find':
                this.find(args);
                break;
            case 'lsof':
                this.lsof();
                break;
            case 'nc':
                this.netcat(args[0], args[1]);
                break;
            case 'help':
                this.help();
                break;
            case 'clear':
                this.clear();
                break;
            default:
                this.println(`Command not found: ${command}`);
        }
    }

    // Command implementations
    ls(args) {
        const files = this.files[this.currentDir];
        if (args.includes('-la') || args.includes('-a')) {
            this.println('. ..');
        }
        Object.keys(files).forEach(file => {
            this.println(file);
        });
    }

    cd(dir) {
        if (dir === '..') {
            this.currentDir = this.currentDir.split('/').slice(0, -1).join('/');
        } else {
            const newPath = `${this.currentDir}/${dir}`;
            if (this.files[newPath]) {
                this.currentDir = newPath;
            } else {
                this.println(`Directory not found: ${dir}`);
            }
        }
    }

    cat(file) {
        const files = this.files[this.currentDir];
        if (files[file]) {
            this.println(files[file]);
        } else {
            this.println(`File not found: ${file}`);
        }
    }

    chmod(mode, file) {
        const files = this.files[this.currentDir];
        if (files[file]) {
            files[file].permissions = mode;
            this.println(`Changed permissions of ${file} to ${mode}`);
        } else {
            this.println(`File not found: ${file}`);
        }
    }

    ps() {
        this.println('  PID TTY          TIME CMD');
        this.processes.forEach(proc => {
            this.println(`${proc.pid.toString().padStart(5)} ?        00:00:00 ${proc.cmd}`);
        });
    }

    top() {
        this.println('Tasks: 2 total, 2 running');
        this.ps();
    }

    netstat() {
        this.println('Active Internet connections (only servers)');
        this.println('Proto Recv-Q Send-Q Local Address           Foreign Address         State');
        this.processes.forEach(proc => {
            this.println(`tcp        0      0 0.0.0.0:${proc.port}            0.0.0.0:*               LISTEN`);
        });
    }

    grep(args) {
        const pattern = args[args.indexOf('-r') + 1] || args[0];
        const files = this.files[this.currentDir];
        Object.entries(files).forEach(([name, content]) => {
            if (content.includes(pattern)) {
                this.println(`${name}: ${content}`);
            }
        });
    }

    find(args) {
        this.println('Simulated find command output');
    }

    lsof() {
        this.processes.forEach(proc => {
            this.println(`${proc.cmd} ${proc.pid} user IPv4 ${proc.port}`);
        });
    }

    netcat(host, port) {
        if (host === 'localhost' && this.processes.some(p => p.port.toString() === port)) {
            this.println('Connection successful');
            if (port === '9999') {
                this.println('flag{network_ninja}');
            }
        } else {
            this.println('Connection failed');
        }
    }

    help() {
        this.println(`
Available commands:
ls [-la]    - List directory contents
cd <dir>    - Change directory
cat <file>  - Display file contents
chmod <mode> <file> - Change file permissions
ps          - List processes
top         - System monitor
netstat     - Network statistics
grep [-r] <pattern> - Search for pattern
find        - Search for files
lsof        - List open files
nc <host> <port> - NetCat utility
clear       - Clear screen
help        - Show this help
        `);
    }

    clear() {
        this.output.innerHTML = '';
    }

    // Utility methods
    println(text) {
        const line = document.createElement('div');
        line.textContent = text;
        this.output.appendChild(line);
        this.output.scrollTop = this.output.scrollHeight;
    }

    printCommand(cmd) {
        this.println(`user@quicksnatch:${this.currentDir}$ ${cmd}`);
    }

    printWelcome() {
        this.println('Welcome to QuickSnatch Terminal Emulator');
        this.println('Type "help" for available commands');
        this.println('');
    }
}
