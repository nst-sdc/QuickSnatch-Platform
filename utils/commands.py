import os
import subprocess
import shutil
from datetime import datetime
import stat
from typing import Dict, List, Optional, Tuple

class CommandExecutor:
    """Handle command execution and provide help information"""
    
    def __init__(self):
        self.commands = {
            'ls': {
                'function': self.list_directory,
                'category': 'File Operations',
                'description': 'List directory contents',
                'usage': 'ls [-la] [directory]',
                'examples': [
                    'ls',
                    'ls -la',
                    'ls /etc'
                ],
                'requires_root': False
            },
            'cat': {
                'function': self.concatenate,
                'category': 'File Operations',
                'description': 'Display file contents',
                'usage': 'cat [file]',
                'examples': [
                    'cat /etc/passwd',
                    'cat file.txt'
                ],
                'requires_root': False
            },
            'pwd': {
                'function': self.print_working_directory,
                'category': 'File Operations',
                'description': 'Print working directory',
                'usage': 'pwd',
                'examples': ['pwd'],
                'requires_root': False
            },
            'cd': {
                'function': self.change_directory,
                'category': 'File Operations',
                'description': 'Change directory',
                'usage': 'cd [directory]',
                'examples': [
                    'cd /etc',
                    'cd ~'
                ],
                'requires_root': False
            },
            'mkdir': {
                'function': self.make_directory,
                'category': 'File Operations',
                'description': 'Create new directory',
                'usage': 'mkdir [-p] [directory]',
                'examples': [
                    'mkdir newdir',
                    'mkdir -p /path/to/dir'
                ],
                'requires_root': False
            },
            'touch': {
                'function': self.touch_file,
                'category': 'File Operations',
                'description': 'Create empty file',
                'usage': 'touch [file]',
                'examples': ['touch newfile.txt'],
                'requires_root': False
            },
            'rm': {
                'function': self.remove_file,
                'category': 'File Operations',
                'description': 'Remove file or directory',
                'usage': 'rm [-rf] [file/directory]',
                'examples': [
                    'rm file.txt',
                    'rm -rf directory'
                ],
                'requires_root': False
            },
            'chmod': {
                'function': self.change_permissions,
                'category': 'Permissions',
                'description': 'Change file permissions',
                'usage': 'chmod [mode] [file]',
                'examples': [
                    'chmod 755 file.txt',
                    'chmod +x script.sh'
                ],
                'requires_root': False
            },
            'chown': {
                'function': self.change_owner,
                'category': 'Permissions',
                'description': 'Change file owner and group',
                'usage': 'chown [user:group] [file]',
                'examples': [
                    'chown root:root file.txt',
                    'chown www-data:www-data /var/www'
                ],
                'requires_root': True
            },
            'sudo': {
                'function': self.sudo_command,
                'category': 'System',
                'description': 'Execute command as superuser',
                'usage': 'sudo [command]',
                'examples': [
                    'sudo ls /root',
                    'sudo cat /etc/shadow'
                ],
                'requires_root': True
            },
            'apt': {
                'function': self.apt_command,
                'category': 'System',
                'description': 'Package management',
                'usage': 'apt [install|remove|update] [package]',
                'examples': [
                    'apt update',
                    'apt install nginx'
                ],
                'requires_root': True
            },
            'systemctl': {
                'function': self.systemctl_command,
                'category': 'System',
                'description': 'Control system services',
                'usage': 'systemctl [start|stop|status] [service]',
                'examples': [
                    'systemctl status nginx',
                    'systemctl start mysql'
                ],
                'requires_root': True
            },
            'find': {
                'function': self.find_files,
                'category': 'Search',
                'description': 'Search for files',
                'usage': 'find [path] [options]',
                'examples': [
                    'find / -name "*.txt"',
                    'find /var -type f -mtime -7'
                ],
                'requires_root': False
            },
            'grep': {
                'function': self.grep_search,
                'category': 'Search',
                'description': 'Search file contents',
                'usage': 'grep [pattern] [file]',
                'examples': [
                    'grep "error" /var/log/syslog',
                    'grep -r "TODO" /home'
                ],
                'requires_root': False
            },
            'ps': {
                'function': self.process_status,
                'category': 'System',
                'description': 'Show process status',
                'usage': 'ps [options]',
                'examples': [
                    'ps aux',
                    'ps -ef | grep nginx'
                ],
                'requires_root': False
            },
            'netstat': {
                'function': self.network_status,
                'category': 'Network',
                'description': 'Network connections',
                'usage': 'netstat [options]',
                'examples': [
                    'netstat -tulpn',
                    'netstat -an'
                ],
                'requires_root': True
            }
        }
        self.current_directory = '/home/ubuntu'
        self.username = 'ubuntu'
        self.is_root = False
        self.command_history = []
        self.challenge_progress = {
            'total_steps': 10,
            'completed_steps': 0,
            'points': 0,
            'max_points': 100,
            'hints_used': 0,
            'time_started': datetime.now()
        }

    def execute(self, command: str) -> Tuple[bool, str]:
        """Execute a command and return result"""
        parts = command.strip().split()
        if not parts:
            return False, "No command provided"

        cmd_name = parts[0]
        args = parts[1:] if len(parts) > 1 else []

        # Handle sudo command specially
        if cmd_name == 'sudo':
            if not args:
                return False, "sudo: command required"
            cmd_name = args[0]
            args = args[1:]
            self.is_root = True

        if cmd_name not in self.commands:
            return False, f"Command not found: {cmd_name}. Type 'help' for available commands."

        # Check if command requires root
        if self.commands[cmd_name]['requires_root'] and not self.is_root:
            return False, f"Permission denied: '{cmd_name}' requires root privileges. Use sudo."

        try:
            result = self.commands[cmd_name]['function'](args)
            self.is_root = False  # Reset root status after command
            return result
        except Exception as e:
            self.is_root = False  # Reset root status on error
            return False, f"Error executing {cmd_name}: {str(e)}"

    def sudo_command(self, args: List[str]) -> Tuple[bool, str]:
        """Execute command with root privileges"""
        if not args:
            return False, "sudo: command required"
        
        cmd = args[0]
        if cmd not in self.commands:
            return False, f"Command not found: {cmd}"
            
        self.is_root = True
        result = self.commands[cmd]['function'](args[1:])
        self.is_root = False
        return result

    def apt_command(self, args: List[str]) -> Tuple[bool, str]:
        """Package management"""
        if not args:
            return False, "Usage: apt [install|remove|update] [package]"
            
        action = args[0]
        if action not in ['install', 'remove', 'update']:
            return False, f"Invalid action: {action}"
            
        if action == 'update':
            return True, "Reading package lists... Done"
        elif len(args) < 2:
            return False, f"apt {action}: package name required"
            
        package = args[1]
        return True, f"Package '{package}' {action}ed successfully"

    def systemctl_command(self, args: List[str]) -> Tuple[bool, str]:
        """Control system services"""
        if not args:
            return False, "Usage: systemctl [start|stop|status] [service]"
            
        action = args[0]
        if action not in ['start', 'stop', 'status']:
            return False, f"Invalid action: {action}"
            
        if len(args) < 2:
            return False, "Service name required"
            
        service = args[1]
        if action == 'status':
            return True, f"● {service}.service - {service.title()} Server\\n   Active: active (running)"
        return True, f"Service '{service}' {action}ed successfully"

    def process_status(self, args: List[str]) -> Tuple[bool, str]:
        """Show process status"""
        header = "USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND"
        processes = [
            "root         1  0.0  0.1 169240  9164 ?        Ss   Jan15   0:02 /sbin/init",
            "root       123  0.0  0.1  94772  7796 ?        Ss   Jan15   0:00 /usr/sbin/sshd",
            "ubuntu     456  0.0  0.2 116924 10256 pts/0    Ss   04:01   0:00 bash"
        ]
        return True, header + "\\n" + "\\n".join(processes)

    def network_status(self, args: List[str]) -> Tuple[bool, str]:
        """Show network connections"""
        header = "Proto Recv-Q Send-Q Local Address           Foreign Address         State"
        connections = [
            "tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN",
            "tcp        0      0 127.0.0.1:3306          0.0.0.0:*               LISTEN",
            "tcp6       0      0 :::80                   :::*                    LISTEN"
        ]
        return True, header + "\\n" + "\\n".join(connections)

    def find_files(self, args: List[str]) -> Tuple[bool, str]:
        """Find files in the system"""
        if not args:
            return False, "Usage: find [path] [options]"
        
        path = args[0]
        pattern = None
        
        if len(args) > 2 and args[1] == '-name':
            pattern = args[2]
        
        files = [
            f"{path}/file1.txt",
            f"{path}/dir1/file2.txt",
            f"{path}/dir2/file3.log"
        ]
        
        if pattern:
            files = [f for f in files if pattern.replace('"', '') in f]
        
        return True, "\\n".join(files)

    def grep_search(self, args: List[str]) -> Tuple[bool, str]:
        """Search file contents"""
        if len(args) < 2:
            return False, "Usage: grep [pattern] [file]"
        
        pattern = args[0]
        filename = args[1]
        
        sample_content = [
            "Line 1: Some content here",
            f"Line 2: Found {pattern} here",
            "Line 3: More content",
            f"Line 4: Another {pattern} match"
        ]
        
        matches = [line for line in sample_content if pattern in line]
        return True, "\\n".join(matches)

    def list_directory(self, args: List[str]) -> Tuple[bool, str]:
        """List directory contents"""
        path = self.current_directory
        show_hidden = False
        show_details = False
        
        for arg in args:
            if arg == '-a':
                show_hidden = True
            elif arg == '-l':
                show_details = True
            else:
                path = os.path.join(self.current_directory, arg)

        try:
            files = os.listdir(path)
            if not show_hidden:
                files = [f for f in files if not f.startswith('.')]
            
            if show_details:
                result = []
                for f in sorted(files):
                    filepath = os.path.join(path, f)
                    stat_info = os.stat(filepath)
                    mode = stat.filemode(stat_info.st_mode)
                    size = stat_info.st_size
                    mtime = datetime.fromtimestamp(stat_info.st_mtime).strftime('%Y-%m-%d %H:%M')
                    result.append(f"{mode} {size:8d} {mtime} {f}")
                return True, '\n'.join(result)
            
            return True, '  '.join(sorted(files))
        except Exception as e:
            return False, f"Error: {str(e)}"

    def concatenate(self, args: List[str]) -> Tuple[bool, str]:
        """Display file contents"""
        if not args:
            return False, "Error: No file specified"
        try:
            file_path = os.path.join(self.current_directory, args[0])
            with open(file_path, 'r') as f:
                return True, f.read()
        except Exception as e:
            return False, f"Error: {str(e)}"

    def print_working_directory(self, args: List[str]) -> Tuple[bool, str]:
        """Print current working directory"""
        return True, self.current_directory

    def change_directory(self, args: List[str]) -> Tuple[bool, str]:
        """Change current directory"""
        try:
            path = args[0] if args else '.'
            new_dir = os.path.join(self.current_directory, path)
            os.chdir(new_dir)
            self.current_directory = os.getcwd()
            return True, f"Changed directory to {self.current_directory}"
        except Exception as e:
            return False, f"Error: {str(e)}"

    def make_directory(self, args: List[str]) -> Tuple[bool, str]:
        """Create new directory"""
        if not args:
            return False, "Error: No directory specified"
        try:
            dir_path = os.path.join(self.current_directory, args[0])
            os.mkdir(dir_path)
            return True, f"Created directory {args[0]}"
        except Exception as e:
            return False, f"Error: {str(e)}"

    def touch_file(self, args: List[str]) -> Tuple[bool, str]:
        """Create empty file"""
        if not args:
            return False, "Error: No file specified"
        try:
            file_path = os.path.join(self.current_directory, args[0])
            open(file_path, 'w').close()
            return True, f"Created file {args[0]}"
        except Exception as e:
            return False, f"Error: {str(e)}"

    def remove_file(self, args: List[str]) -> Tuple[bool, str]:
        """Remove file"""
        if not args:
            return False, "Error: No file specified"
        try:
            file_path = os.path.join(self.current_directory, args[0])
            os.remove(file_path)
            return True, f"Removed file {args[0]}"
        except Exception as e:
            return False, f"Error: {str(e)}"

    def change_permissions(self, args: List[str]) -> Tuple[bool, str]:
        """Change file permissions"""
        if len(args) != 2:
            return False, "Usage: chmod [mode] [file]"
        
        mode, filename = args
        filepath = os.path.join(self.current_directory, filename)
        
        try:
            if mode.startswith('+') or mode.startswith('-'):
                current = stat.S_IMODE(os.stat(filepath).st_mode)
                if mode == '+x':
                    new_mode = current | 0o111
                elif mode == '-x':
                    new_mode = current & ~0o111
                else:
                    return False, "Unsupported permission mode"
            else:
                new_mode = int(mode, 8)
            
            os.chmod(filepath, new_mode)
            return True, f"Changed permissions of {filename} to {mode}"
        except Exception as e:
            return False, f"Error: {str(e)}"

    def clear_screen(self, args: List[str]) -> Tuple[bool, str]:
        """Clear terminal screen"""
        return True, "\033[2J\033[H"

    def show_date(self, args: List[str]) -> Tuple[bool, str]:
        """Show current date/time"""
        return True, datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def who_am_i(self, args: List[str]) -> Tuple[bool, str]:
        """Show current user"""
        return True, self.username

    def echo_message(self, args: List[str]) -> Tuple[bool, str]:
        """Display a message"""
        return True, ' '.join(args)

    def show_help(self, args: List[str]) -> Tuple[bool, str]:
        """Show help information for commands"""
        if not args:
            help_text = "╭──────────────── Quick-Snatch Help ────────────────╮\n"
            help_text += "│ Available Commands:                                 │\n"
            help_text += "│                                                    │\n"

            # Group commands by category
            categories = {}
            for cmd, info in self.commands.items():
                cat = info['category']
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append((cmd, info['description']))

            # Display commands by category
            for category, commands in categories.items():
                help_text += f"│  {category}:                                  │\n"
                for cmd, desc in commands:
                    help_text += f"│    {cmd:<8} - {desc:<30} │\n"
                help_text += "│                                                    │\n"

            help_text += "╰────────────────────────────────────────────────────╯"
            return True, help_text

        cmd = args[0]
        if cmd not in self.commands:
            return False, f"No help available for '{cmd}'. Type 'help' for available commands."

        info = self.commands[cmd]
        help_text = f"Command: {cmd}\n"
        help_text += f"Category: {info['category']}\n"
        help_text += f"Description: {info['description']}\n"
        help_text += f"Usage: {info['usage']}\n"
        help_text += "Examples:\n"
        for example in info['examples']:
            help_text += f"  {example}\n"
        return True, help_text

    def update_progress(self, cmd_name: str, args: List[str]) -> None:
        """Update challenge progress based on command usage"""
        # Navigation commands
        if cmd_name in ['cd', 'pwd'] and not self.challenge_progress['objectives']['navigation']['completed']:
            self.challenge_progress['objectives']['navigation']['completed'] = True
            self.challenge_progress['points'] += 10
            self.challenge_progress['completed_steps'] += 1

        # File operations
        if cmd_name in ['ls', 'cat', 'touch', 'mkdir', 'rm'] and not self.challenge_progress['objectives']['file_ops']['completed']:
            if len(self.command_history) >= 3:  # Require at least 3 file operations
                self.challenge_progress['objectives']['file_ops']['completed'] = True
                self.challenge_progress['points'] += 20
                self.challenge_progress['completed_steps'] += 1

        # Permissions
        if cmd_name == 'chmod' and not self.challenge_progress['objectives']['permissions']['completed']:
            self.challenge_progress['objectives']['permissions']['completed'] = True
            self.challenge_progress['points'] += 30
            self.challenge_progress['completed_steps'] += 1

        # Search operations
        if cmd_name in ['find', 'grep'] and not self.challenge_progress['objectives']['search']['completed']:
            self.challenge_progress['objectives']['search']['completed'] = True
            self.challenge_progress['points'] += 40
            self.challenge_progress['completed_steps'] += 1

    def get_progress_info(self) -> str:
        """Get formatted progress information"""
        progress = self.challenge_progress
        info = "\n╭──────────── Challenge Progress ────────────╮"
        info += f"\n│ Steps Completed: {progress['completed_steps']}/{progress['total_steps']}"
        info += f"\n│ Points: {progress['points']}/{progress['max_points']}"
        info += f"\n│ Commands Used: {len(self.command_history)}"
        info += f"\n│ Hints Used: {progress['hints_used']}"
        
        # Calculate time elapsed
        time_elapsed = datetime.now() - progress['time_started']
        minutes = int(time_elapsed.total_seconds() / 60)
        seconds = int(time_elapsed.total_seconds() % 60)
        info += f"\n│ Time Elapsed: {minutes}m {seconds}s"
        
        info += "\n│"
        info += "\n│ Objectives:"
        for obj_name, obj_data in progress['objectives'].items():
            status = "✓" if obj_data['completed'] else "✗"
            info += f"\n│  {status} {obj_name.title()} ({obj_data['points']} pts)"
        
        info += "\n╰──────────────────────────────────────────╯"
        return info

    def show_progress(self, args: List[str]) -> Tuple[bool, str]:
        """Show detailed progress information"""
        return True, self.get_progress_info()

    def show_hint(self, args: List[str]) -> Tuple[bool, str]:
        """Show hints for the current challenge"""
        self.challenge_progress['hints_used'] += 1
        hints = {
            'navigation': 'Try using cd and pwd to navigate the filesystem',
            'file_ops': 'Create and manipulate files using touch, mkdir, and rm',
            'permissions': 'Use chmod to modify file permissions (e.g., chmod 755 file)',
            'search': 'Search for the flag using find or grep commands'
        }
        
        if not args:
            return True, "Available hint categories: " + ", ".join(hints.keys()) + "\nUse 'hint <category>' for specific hints"
        
        category = args[0]
        if category in hints:
            return True, f"Hint for {category}: {hints[category]}\n" + self.get_progress_info()
        return False, f"No hints available for '{category}'"

    def submit_flag(self, args: List[str]) -> Tuple[bool, str]:
        """Submit a flag for verification"""
        if not args:
            return False, "Usage: submit <flag>"
        
        submitted_flag = args[0]
        # Add your flag verification logic here
        is_correct = submitted_flag == "test_flag"  # Replace with actual flag
        
        if is_correct:
            bonus_points = max(0, 50 - self.challenge_progress['hints_used'] * 10)
            self.challenge_progress['points'] += bonus_points
            return True, f"🎉 Congratulations! Flag is correct!\nBonus points: {bonus_points}\n" + self.get_progress_info()
        return False, "Incorrect flag. Keep trying!\n" + self.get_progress_info()
