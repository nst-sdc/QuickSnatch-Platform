class VirtualFileSystem {
    constructor(level) {
        this.currentPath = '/home/user';
        this.level = level;
        this.levelInfo = null;
        this.fileSystem = {};
        this.loadLevelInfo().then(() => {
            this.setupFileSystem();
            terminal.writeOutput(this.getLevelInstructions());
        });
    }

    async loadLevelInfo() {
        try {
            const response = await fetch(`/challenges/level${this.level}/level_info.json`);
            this.levelInfo = await response.json();
        } catch (error) {
            console.error('Error loading level info:', error);
            this.levelInfo = {
                prompt: "user@quicksnatch",
                files: {},
                hints: ["Level info not available"]
            };
        }
    }

    setupFileSystem() {
        // Base structure common to all levels
        this.fileSystem = {
            'home': {
                'user': {}
            },
            'etc': {},
            'var': {
                'log': {}
            },
            'proc': {},
            'tmp': {},
            'usr': {
                'bin': {},
                'local': {
                    'bin': {}
                }
            }
        };

        // Add level-specific files
        if (this.levelInfo && this.levelInfo.files) {
            for (const [path, content] of Object.entries(this.levelInfo.files)) {
                this.createFile(path, content);
            }
        }
    }

    createFile(path, content) {
        const parts = path.split('/').filter(p => p);
        let current = this.fileSystem;
        
        for (let i = 0; i < parts.length - 1; i++) {
            const part = parts[i];
            if (!current[part]) {
                current[part] = {};
            }
            current = current[part];
        }
        
        const fileName = parts[parts.length - 1];
        current[fileName] = content;
    }

    getPrompt() {
        return `${this.levelInfo?.prompt || "user@quicksnatch"}:${this.currentPath}$ `;
    }

    getLevelInstructions() {
        if (!this.levelInfo) return "Loading level information...";
        
        return `Level ${this.levelInfo.level}: ${this.levelInfo.title}\n` +
               `Difficulty: ${this.levelInfo.difficulty}\n\n` +
               `${this.levelInfo.description}\n\n` +
               `Available commands: ${this.levelInfo.commands.join(', ')}\n\n` +
               `Type 'hint' for hints or 'help' for available commands.`;
    }

    getHint() {
        if (!this.levelInfo || !this.levelInfo.hints.length === 0) {
            return "No hints available.";
        }
        const randomIndex = Math.floor(Math.random() * this.levelInfo.hints.length);
        return `Hint: ${this.levelInfo.hints[randomIndex]}`;
    }

    ls(path = this.currentPath) {
        const dir = this.getDirectory(path);
        if (!dir) return `ls: cannot access '${path}': No such file or directory`;
        return Object.keys(dir).join('  ');
    }

    cd(path) {
        if (!path || path === '~') {
            this.currentPath = '/home/user';
            return '';
        }

        const newPath = this.resolvePath(path);
        const dir = this.getDirectory(newPath);
        
        if (!dir) {
            return `cd: ${path}: No such file or directory`;
        }
        
        if (typeof dir !== 'object') {
            return `cd: ${path}: Not a directory`;
        }

        this.currentPath = newPath;
        return '';
    }

    pwd() {
        return this.currentPath;
    }

    cat(path) {
        if (!path) return 'cat: missing operand';
        
        const resolvedPath = this.resolvePath(path);
        const file = this.getFile(resolvedPath);

        if (file === null) {
            return `cat: ${path}: No such file or directory`;
        }
        
        if (typeof file === 'object') {
            return `cat: ${path}: Is a directory`;
        }

        return file;
    }

    resolvePath(path) {
        if (path.startsWith('/')) {
            return path;
        }
        
        const current = this.currentPath.split('/').filter(Boolean);
        const parts = path.split('/').filter(Boolean);
        
        for (const part of parts) {
            if (part === '..') {
                current.pop();
            } else if (part !== '.') {
                current.push(part);
            }
        }
        
        return '/' + current.join('/');
    }

    getDirectory(path) {
        const parts = path.split('/').filter(Boolean);
        let current = this.fileSystem;
        
        for (const part of parts) {
            if (!current || typeof current !== 'object') return null;
            current = current[part];
        }
        
        return current;
    }

    getFile(path) {
        const parts = path.split('/').filter(Boolean);
        let current = this.fileSystem;
        
        for (let i = 0; i < parts.length - 1; i++) {
            if (!current || typeof current !== 'object') return null;
            current = current[parts[i]];
        }
        
        if (!current) return null;
        return current[parts[parts.length - 1]];
    }

    async verifyFlag(flag) {
        try {
            const response = await fetch('/verify_flag', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    level: this.level,
                    flag: flag
                })
            });
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error verifying flag:', error);
            return { success: false, message: 'Error verifying flag' };
        }
    }

    submitFlag(flag) {
        if (!flag) {
            return 'submit: missing flag';
        }
        if (!flag.startsWith('flag{') || !flag.endsWith('}')) {
            return 'Invalid flag format. Flags should be in the format flag{...}';
        }
        return this.verifyFlag(flag);
    }
}

class Terminal {
    constructor(elementId, level) {
        this.element = document.getElementById(elementId);
        this.fs = new VirtualFileSystem(level);
        this.history = [];
        this.historyIndex = 0;
        this.setupTerminal();
    }

    setupTerminal() {
        this.createNewLine();
        this.element.addEventListener('keydown', this.handleKeyDown.bind(this));
        this.focusCommandLine();
    }

    createNewLine() {
        const line = document.createElement('div');
        line.className = 'line';
        
        const prompt = document.createElement('span');
        prompt.className = 'prompt';
        prompt.textContent = this.fs.getPrompt();
        
        const command = document.createElement('span');
        command.className = 'command';
        command.contentEditable = 'true';
        command.spellcheck = false;
        
        line.appendChild(prompt);
        line.appendChild(command);
        this.element.appendChild(line);
        
        return command;
    }

    async handleCommand(commandText) {
        if (!commandText) return;
        
        const [cmd, ...args] = commandText.trim().split(/\s+/);
        
        const commands = {
            ls: () => this.fs.ls(args[0]),
            cd: () => this.fs.cd(args[0]),
            pwd: () => this.fs.pwd(),
            cat: () => this.fs.cat(args[0]),
            clear: () => {
                this.element.innerHTML = '';
                return '';
            },
            help: () => `Available commands:
  ls [path]      - List directory contents
  cd [path]      - Change directory
  pwd            - Print working directory
  cat [file]     - View file contents
  clear          - Clear terminal screen
  help           - Show this help message
  hint           - Show a random hint
  submit [flag]  - Submit a flag (format: flag{...})`,
            hint: () => this.fs.getHint(),
            submit: async () => {
                const result = await this.fs.submitFlag(args[0]);
                if (result.success && result.next_level) {
                    setTimeout(() => {
                        window.location.href = `/terminal/${result.next_level}`;
                    }, 2000);
                }
                return result.message;
            }
        };

        if (commands[cmd]) {
            const output = await commands[cmd]();
            if (output) {
                this.writeOutput(output);
            }
        } else {
            this.writeOutput(`Command not found: ${cmd}`);
        }

        this.history.push(commandText);
        this.historyIndex = this.history.length;
        this.createNewLine();
        this.focusCommandLine();
    }

    writeOutput(text) {
        const output = document.createElement('div');
        output.className = 'output';
        output.textContent = text;
        this.element.appendChild(output);
    }

    focusCommandLine() {
        const commandLines = this.element.getElementsByClassName('command');
        const lastCommand = commandLines[commandLines.length - 1];
        lastCommand.focus();
    }

    handleKeyDown(event) {
        const commandLines = this.element.getElementsByClassName('command');
        const currentCommand = commandLines[commandLines.length - 1];
        
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            const commandText = currentCommand.textContent;
            currentCommand.contentEditable = 'false';
            this.handleCommand(commandText);
        }
        else if (event.key === 'ArrowUp') {
            event.preventDefault();
            if (this.historyIndex > 0) {
                this.historyIndex--;
                currentCommand.textContent = this.history[this.historyIndex];
            }
        }
        else if (event.key === 'ArrowDown') {
            event.preventDefault();
            if (this.historyIndex < this.history.length) {
                this.historyIndex++;
                currentCommand.textContent = this.history[this.historyIndex] || '';
            }
        }
        this.element.scrollTop = this.element.scrollHeight;
    }
}
