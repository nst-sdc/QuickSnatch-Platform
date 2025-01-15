# QuickSnatch - Interactive Terminal Challenge Platform

QuickSnatch is an interactive web-based platform for learning Linux terminal commands through engaging challenges. Users progress through various levels, each teaching different aspects of terminal usage and system administration.

## Features

- 10 Progressive Challenges
- Interactive Terminal Emulator
- User Authentication
- Real-time Leaderboard
- Fullscreen Terminal Mode
- Comprehensive Command Support

## Technologies Used

- Node.js
- Express.js
- MongoDB
- EJS Templates
- Bootstrap 5
- Custom Terminal Emulator

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/QuickSnatch.git
cd QuickSnatch
```

2. Install dependencies:
```bash
npm install
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Start MongoDB:
```bash
sudo systemctl start mongodb
```

5. Run the application:
```bash
npm start
```

## Available Commands in Terminal

The terminal emulator supports various Linux commands:
- `ls` - List directory contents
- `cd` - Change directory
- `cat` - View file contents
- `chmod` - Change file permissions
- `ps` - List processes
- `top` - System monitor
- `netstat` - Network statistics
- `grep` - Search text
- `find` - Search files
- `lsof` - List open files
- `nc` - NetCat utility

## Challenge Levels

1. Basic Terminal Navigation
2. File Permissions
3. Text Search
4. Process Management
5. Network Tools
6. Bash Scripting
7. Archive Management
8. System Information
9. Cron Jobs
10. Final Challenge

## Security Features

- Secure session management
- Password hashing with bcrypt
- CSRF protection
- XSS prevention
- Secure headers
- Environment-based configurations

## Development

1. Start in development mode:
```bash
export FLASK_ENV=development
python app.py
```

2. Access the application:
```
http://localhost:7771
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - feel free to use and modify for your purposes.

## Author

[Your Name]
