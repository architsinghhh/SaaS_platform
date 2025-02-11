const express = require('express');
const bcrypt = require('bcrypt');
const { MongoClient } = require('mongodb');
const app = express();
const PORT = 3000;

// MongoDB setup
const uri = "mongodb://localhost:27017";
const client = new MongoClient(uri, { useNewUrlParser: true, useUnifiedTopology: true });

let db, usersCollection;

// Connect to the database
client.connect((err) => {
    if (err) throw err;
    db = client.db('clientDatabase');
    usersCollection = db.collection('users');
    console.log("Connected to MongoDB");
});

app.use(express.json());
app.use(express.static('public'));

app.get('/', (req, res) => {
    res.sendFile(__dirname + '/login_new.html');  // Serve loginpage.html when user visits root
});

// Express setup and MongoDB connection...

app.post('/login', async (req, res) => {
    const { username, password } = req.body;

    // Hardcoded credentials for testing
    const hardcodedUsername = 'abc'; // Change to your test username
    const hardcodedPassword = 'abc'; // Change to your test password

    if (username === hardcodedUsername && password === hardcodedPassword) {
        return res.redirect('/afterlogin.html');
    }

    return res.json({ success: false, message: 'Invalid credentials' });
});






// Serve after login page
app.get('/afterlogin.html', (req, res) => {
    res.sendFile(__dirname + '/public/afterlogin.html');
});

app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
});
