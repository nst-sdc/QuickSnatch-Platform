# QuickSnatch - Hackathon Challenge Platform

A secure, production-ready Flask application for hosting terminal-based hackathon challenges. Features team registration, real-time leaderboard, and progressive challenge system.

## 🚀 Features

- **Secure Authentication System**
  - Team-based registration
  - Session management
  - Password hashing
  - CSRF protection

- **Interactive Challenge System**
  - Progressive difficulty levels
  - Real-time feedback
  - Time tracking
  - Secure answer validation

- **Dynamic Leaderboard**
  - Real-time updates
  - Team rankings
  - Progress tracking
  - Time-based scoring

- **Production-Ready Security**
  - HTTPS enforcement
  - Security headers
  - Rate limiting
  - XSS protection
  - Content Security Policy
  - Input validation

- **Performance Optimizations**
  - Response caching
  - Database optimization
  - Static file compression
  - Efficient session handling

## 🛠️ Tech Stack

- **Backend**: Flask (Python)
- **Database**: MongoDB
- **Frontend**: HTML5, CSS3, JavaScript
- **Security**: Flask-Talisman, Flask-SeaSurf
- **Authentication**: Flask-Login
- **Styling**: Bootstrap 5
- **Icons**: Font Awesome

## 🔧 Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/QuickSnatch.git
cd QuickSnatch
```

2. Create and activate virtual environment:
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
# Edit .env with your configurations
```

5. Initialize the database:
```bash
# Ensure MongoDB is running
python init_db.py
```

## 🚀 Development Setup

1. Set environment variables:
```bash
export FLASK_ENV=development
export FLASK_DEBUG=1
```

2. Run the development server:
```bash
flask run
```

## 🌐 Production Deployment

1. Set production environment variables:
```bash
export FLASK_ENV=production
export FLASK_DEBUG=0
export SECRET_KEY=<your-secure-key>
export MONGO_URI=<your-mongodb-uri>
```

2. Run with Gunicorn:
```bash
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Nginx Configuration

```nginx
server {
    listen 443 ssl;
    server_name yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🔒 Security Features

- HTTPS enforcement
- Secure session configuration
- XSS protection
- CSRF protection
- Rate limiting
- Content Security Policy
- Secure headers
- Input validation
- Password hashing
- Session management

## 📈 Performance Features

- Response caching
- Database optimization
- Static file compression
- Efficient session handling
- Resource optimization

## 📝 Environment Variables

Create a `.env` file with the following variables:

```env
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=your-secret-key
MONGO_URI=mongodb://localhost:27017/quicksnatch
```

## 🔍 Monitoring

- Application logging
- Error tracking
- Request logging
- Performance monitoring
- Custom error pages

## 🧪 Testing

Run the test suite:
```bash
python -m pytest
```

## 📦 Project Structure

```
QuickSnatch/
├── app.py              # Main application file
├── config.py           # Configuration settings
├── requirements.txt    # Project dependencies
├── init_db.py         # Database initialization
├── static/            # Static files (CSS, JS)
├── templates/         # HTML templates
├── views/             # Template components
└── logs/              # Application logs
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 👥 Team

- Vivek W - Developer and Maintainer

## 📞 Support

For support, email [support@nstsdc.org] or create an issue in the repository.

## 🙏 Acknowledgments
- Special thanks to [ForrestKnight](https://www.youtube.com/@fknight) for the amazing [tutorial](https://youtu.be/KtYby2QN0kQ?si=gTshuFyfizpJyiM-) that inspired this project
