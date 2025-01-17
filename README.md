# QuickSnatch CTF Platform

A web-based Capture The Flag (CTF) platform focused on Linux command-line skills and system administration challenges.

## Features

- 10 Progressive difficulty levels
- Real-time terminal emulation
- Time tracking for each level
- User authentication and progress tracking
- Secure flag submission system
- Comprehensive hint system
- Level-specific challenges

## Prerequisites

- Python 3.8+
- pip (Python package manager)
- Virtual environment (recommended)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/QuickSnatch.git
cd QuickSnatch
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Initialize the database:
```bash
flask db upgrade
```

## Running in Development

```bash
flask run --debug
```

## Production Deployment

1. Set environment variables:
```bash
export FLASK_ENV=production
export FLASK_APP=app.py
```

2. Run with Gunicorn:
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Security Features

- Secure session management
- CSRF protection
- XSS prevention
- SQL injection protection
- Secure password hashing
- Rate limiting
- Security headers

## Challenge Levels

1. File Explorer (Easy)
   - Basic Linux commands
   - File system navigation

2. Permission Master (Easy)
   - File permissions
   - chmod command

3. Log Detective (Medium)
   - Log file analysis
   - grep and search

4. Process Inspector (Medium)
   - Process management
   - System monitoring

5. Network Ninja (Medium)
   - Network configuration
   - Service management

6. Bash Scripting Master (Hard)
   - Shell scripting
   - Environment variables

7. Archive Explorer (Hard)
   - File compression
   - Archive management

8. System Administrator (Hard)
   - System services
   - Configuration management

9. Cron Master (Expert)
   - Scheduled tasks
   - Job automation

10. Final Challenge (Expert)
    - Combined skills
    - Advanced problem-solving

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Flask team for the excellent web framework
- Contributors and testers
- CTF community for inspiration
