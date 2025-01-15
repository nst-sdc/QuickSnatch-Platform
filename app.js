require('dotenv').config();
const express = require('express');
const session = require('express-session');
const passport = require('passport');
const LocalStrategy = require('passport-local').Strategy;
const mongoose = require('mongoose');
const bcrypt = require('bcryptjs');
const MongoStore = require('connect-mongo');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

// MongoDB connection
mongoose.connect(process.env.MONGODB_URI || 'mongodb://localhost/quicksnatch', {
    useNewUrlParser: true,
    useUnifiedTopology: true
});

// Middleware
app.set('view engine', 'ejs');
app.use(express.static('public'));
app.use(express.urlencoded({ extended: true }));
app.use(express.json());

// Session configuration
app.use(session({
    secret: process.env.SESSION_SECRET || 'your-secret-key',
    resave: false,
    saveUninitialized: false,
    store: MongoStore.create({
        mongoUrl: process.env.MONGODB_URI || 'mongodb://localhost/quicksnatch'
    }),
    cookie: {
        maxAge: 1000 * 60 * 60 * 24 // 24 hours
    }
}));

// Passport middleware
app.use(passport.initialize());
app.use(passport.session());

// Models
const User = require('./models/User');
const Submission = require('./models/Submission');

// Passport configuration
passport.use(new LocalStrategy(async (username, password, done) => {
    try {
        const user = await User.findOne({ username });
        if (!user) return done(null, false, { message: 'Incorrect username' });
        
        const isMatch = await bcrypt.compare(password, user.password);
        if (!isMatch) return done(null, false, { message: 'Incorrect password' });
        
        return done(null, user);
    } catch (err) {
        return done(err);
    }
}));

passport.serializeUser((user, done) => done(null, user.id));
passport.deserializeUser((id, done) => {
    User.findById(id)
        .then(user => done(null, user))
        .catch(err => done(err));
});

// Challenge answers
const ANSWERS = {
    1: "flag{quick_basics}",
    2: "flag{chmod_master}",
    3: "flag{grep_master_123}",
    4: "flag{process_hunter}",
    5: "flag{network_ninja}",
    6: "flag{bash_wizard}",
    7: "flag{archive_explorer}",
    8: "flag{system_stalker}",
    9: "flag{cron_master}",
    10: "flag{ultimate_champion}"
};

// Routes
app.get('/', (req, res) => {
    res.render('index');
});

app.get('/login', (req, res) => {
    res.render('login');
});

app.post('/login', passport.authenticate('local', {
    successRedirect: '/challenge/1',
    failureRedirect: '/login',
    failureFlash: true
}));

app.get('/register', (req, res) => {
    res.render('register');
});

app.post('/register', async (req, res) => {
    try {
        const { username, password } = req.body;
        
        // Check if user exists
        const existingUser = await User.findOne({ username });
        if (existingUser) {
            return res.render('register', { error: 'Username already exists' });
        }
        
        // Hash password
        const hashedPassword = await bcrypt.hash(password, 10);
        
        // Create new user
        const user = new User({
            username,
            password: hashedPassword,
            currentLevel: 1
        });
        
        await user.save();
        res.redirect('/login');
    } catch (err) {
        console.error(err);
        res.render('register', { error: 'Error creating user' });
    }
});

app.get('/challenge/:level', async (req, res) => {
    if (!req.isAuthenticated()) return res.redirect('/login');
    
    const level = parseInt(req.params.level);
    if (level < 1 || level > 10) return res.redirect('/challenge/1');
    
    res.render(`challenges/level_${level}`);
});

app.post('/challenge/:level/submit', async (req, res) => {
    if (!req.isAuthenticated()) return res.json({ success: false, message: 'Not authenticated' });
    
    const level = parseInt(req.params.level);
    const { answer } = req.body;
    
    if (answer === ANSWERS[level]) {
        await User.findByIdAndUpdate(req.user._id, {
            currentLevel: Math.max(req.user.currentLevel, level + 1),
            lastSubmission: new Date()
        });
        
        await new Submission({
            userId: req.user._id,
            level,
            isCorrect: true,
            submittedAt: new Date()
        }).save();
        
        res.json({ success: true });
    } else {
        await new Submission({
            userId: req.user._id,
            level,
            isCorrect: false,
            submittedAt: new Date()
        }).save();
        
        res.json({ success: false, message: 'Incorrect answer' });
    }
});

app.get('/logout', (req, res) => {
    req.logout();
    res.redirect('/');
});

app.get('/leaderboard', async (req, res) => {
    const users = await User.find()
        .sort({ currentLevel: -1, lastSubmission: 1 })
        .limit(10)
        .select('username currentLevel lastSubmission');
    
    res.render('leaderboard', { users });
});

app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
