class Terminal {
    constructor() {
        this.currentDirectory = '~';
        this.username = 'player';
        this.hostname = 'quicksnatch';
        this.history = [];
        this.historyIndex = -1;
        this.commandBuffer = '';
        this.fileSystem = {
            '~': {
                type: 'dir',
                contents: {
                    'documents': { type: 'dir', contents: {} },
                    'downloads': { type: 'dir', contents: {} },
                    'readme.txt': { type: 'file', content: 'Welcome to QuickSnatch Terminal!' }
                }
            }
        };
    }

    init() {
        this.terminalOutput = document.querySelector('.terminal-output');
        this.terminalInput = document.getElementById('terminal-input');
        this.prompt = document.querySelector('.prompt');
        this.setupEventListeners();
        this.showWelcomeMessage();
        this.updatePrompt();
    }

    setupEventListeners() {
        this.terminalInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                this.handleCommand();
            } else if (e.key === 'ArrowUp' || e.key === 'ArrowDown') {
                e.preventDefault();
                this.navigateHistory(e.key === 'ArrowUp' ? -1 : 1);
            } else if (e.key === 'Tab') {
                e.preventDefault();
                this.handleTabCompletion();
            } else if (e.key === 'c' && e.ctrlKey) {
                e.preventDefault();
                this.handleCtrlC();
            } else if (e.key === 'l' && e.ctrlKey) {
                e.preventDefault();
                this.clearScreen();
            }
        });

        // Terminal window controls
        document.querySelector('.control.close').addEventListener('click', () => {
            this.appendOutput('Terminal session closed. Refresh to restart.');
            this.terminalInput.disabled = true;
        });
    }

    showWelcomeMessage() {
        const now = new Date();
        const welcomeMsg = [
            '\x1b[1;32m  ___        _      _    ____             _       _     \x1b[0m',
            '\x1b[1;32m / _ \\ _   _(_) ___| | _/ ___| _ __   __ _| |_ ___| |__  \x1b[0m',
            '\x1b[1;32m| | | | | | | |/ __| |/ \\___ \\| \'_ \\ / _` | __/ __| \'_ \\ \x1b[0m',
            '\x1b[1;32m| |_| | |_| | | (__|   < ___) | | | | (_| | || (__| | | |\x1b[0m',
            '\x1b[1;32m \\__\\_\\\\__,_|_|\\___|_|\\_\\____/|_| |_|\\__,_|\\__\\___|_| |_|\x1b[0m',
            '',
            '\x1b[1;37mWelcome to QuickSnatch Terminal v1.0.0\x1b[0m',
            `System time: ${now.toLocaleString()}`,
            'Type \x1b[1;33mhelp\x1b[0m for a list of available commands.',
            ''
        ].join('\n');
        this.appendOutput(welcomeMsg);
    }

    updatePrompt() {
        const promptText = `${this.username}@${this.hostname}:${this.currentDirectory}$ `;
        this.prompt.textContent = promptText;
    }

    appendOutput(text, className = '') {
        const output = document.createElement('div');
        output.className = `output-line ${className}`;
        
        // Handle ANSI color codes
        text = text.replace(/\x1b\[([0-9;]*)m/g, (match, p1) => {
            const codes = p1.split(';');
            let classes = [];
            
            codes.forEach(code => {
                switch(code) {
                    case '0': return '</span>';
                    case '1': classes.push('bold'); break;
                    case '31': classes.push('ansi-red'); break;
                    case '32': classes.push('ansi-green'); break;
                    case '33': classes.push('ansi-yellow'); break;
                    case '37': classes.push('ansi-white'); break;
                }
            });
            
            return `<span class="${classes.join(' ')}">`;
        });
        
        output.innerHTML = text;
        this.terminalOutput.appendChild(output);
        this.scrollToBottom();
    }

    handleCommand() {
        const command = this.terminalInput.value.trim();
        if (command) {
            this.appendOutput(`${this.prompt.textContent}${command}`);
            this.history.push(command);
            this.historyIndex = this.history.length;
            this.processCommand(command);
        }
        this.terminalInput.value = '';
    }

    processCommand(command) {
        const [cmd, ...args] = command.split(' ');
        
        const commands = {
            help: () => this.showHelp(),
            clear: () => this.clearScreen(),
            ls: () => this.listDirectory(args[0]),
            cd: () => this.changeDirectory(args[0]),
            pwd: () => this.printWorkingDirectory(),
            cat: () => this.catFile(args[0]),
            echo: () => this.appendOutput(args.join(' ')),
            date: () => this.appendOutput(new Date().toLocaleString()),
            whoami: () => this.appendOutput(this.username)
        };

        if (commands[cmd]) {
            commands[cmd]();
        } else if (cmd) {
            this.appendOutput(`Command not found: ${cmd}. Type 'help' for available commands.`, 'error-output');
        }
    }

    showHelp() {
        const helpText = [
            '\x1b[1;37mAvailable Commands:\x1b[0m',
            '',
            '\x1b[1;33mhelp\x1b[0m     - Show this help message',
            '\x1b[1;33mclear\x1b[0m    - Clear the terminal screen',
            '\x1b[1;33mls\x1b[0m       - List directory contents',
            '\x1b[1;33mcd\x1b[0m       - Change directory',
            '\x1b[1;33mpwd\x1b[0m      - Print working directory',
            '\x1b[1;33mcat\x1b[0m      - View file contents',
            '\x1b[1;33mecho\x1b[0m     - Print text to terminal',
            '\x1b[1;33mdate\x1b[0m     - Show current date/time',
            '\x1b[1;33mwhoami\x1b[0m   - Show current user',
            '',
            'Keyboard Shortcuts:',
            'Ctrl+C    - Cancel current command',
            'Ctrl+L    - Clear screen',
            'Tab       - Auto-complete commands',
            'Up/Down   - Navigate command history',
            ''
        ].join('\n');
        this.appendOutput(helpText);
    }

    navigateHistory(direction) {
        if (this.history.length === 0) return;
        
        this.historyIndex += direction;
        
        if (this.historyIndex >= this.history.length) {
            this.historyIndex = this.history.length;
            this.terminalInput.value = this.commandBuffer;
            return;
        }
        
        if (this.historyIndex < 0) {
            this.historyIndex = 0;
        }
        
        if (this.historyIndex === this.history.length - 1) {
            this.commandBuffer = this.terminalInput.value;
        }
        
        this.terminalInput.value = this.history[this.historyIndex];
        // Move cursor to end
        setTimeout(() => {
            this.terminalInput.selectionStart = this.terminalInput.selectionEnd = this.terminalInput.value.length;
        }, 0);
    }

    handleTabCompletion() {
        const input = this.terminalInput.value;
        const commands = ['help', 'clear', 'ls', 'cd', 'pwd', 'cat', 'echo', 'date', 'whoami'];
        
        const matches = commands.filter(cmd => cmd.startsWith(input));
        
        if (matches.length === 1) {
            this.terminalInput.value = matches[0];
        } else if (matches.length > 1) {
            this.appendOutput(`\n${matches.join('  ')}`);
            this.appendOutput(`${this.prompt.textContent}${input}`);
        }
    }

    handleCtrlC() {
        this.appendOutput('^C');
        this.terminalInput.value = '';
        this.updatePrompt();
    }

    clearScreen() {
        this.terminalOutput.innerHTML = '';
        this.updatePrompt();
    }

    scrollToBottom() {
        this.terminalOutput.scrollTop = this.terminalOutput.scrollHeight;
    }

    listDirectory(path) {
        const dir = this.getDirectory(path);
        if (!dir) {
            this.appendOutput(`Directory not found: ${path}`, 'error-output');
            return;
        }

        const contents = Object.keys(dir.contents);
        if (contents.length === 0) {
            this.appendOutput('Directory is empty.');
        } else {
            this.appendOutput(contents.join('  '));
        }
    }

    changeDirectory(path) {
        const dir = this.getDirectory(path);
        if (!dir) {
            this.appendOutput(`Directory not found: ${path}`, 'error-output');
            return;
        }

        this.currentDirectory = path;
        this.updatePrompt();
    }

    printWorkingDirectory() {
        this.appendOutput(this.currentDirectory);
    }

    catFile(path) {
        const file = this.getFile(path);
        if (!file) {
            this.appendOutput(`File not found: ${path}`, 'error-output');
            return;
        }

        this.appendOutput(file.content);
    }

    getDirectory(path) {
        const parts = path.split('/');
        let dir = this.fileSystem;

        for (const part of parts) {
            if (part === '') continue;
            if (!dir.contents[part]) return null;
            dir = dir.contents[part];
        }

        return dir;
    }

    getFile(path) {
        const dir = this.getDirectory(path);
        if (!dir) return null;

        const parts = path.split('/');
        const fileName = parts[parts.length - 1];

        if (!dir.contents[fileName]) return null;
        return dir.contents[fileName];
    }
}

// Initialize terminal when document is ready
document.addEventListener('DOMContentLoaded', () => {
    window.terminal = new Terminal();
    terminal.init();
});
