const bcrypt = require('bcrypt');
const { MongoClient } = require('mongodb');

async function checkPassword(username, passwordToCheck) {
    const uri = "mongodb://localhost:27017";
    const client = new MongoClient(uri);

    try {
        await client.connect();
        const db = client.db('clientDatabase');
        const usersCollection = db.collection('users');

        // Find the user in the database
        const user = await usersCollection.findOne({ username });

        if (!user) {
            console.log('User not found');
            return;
        }

        // Compare the input password with the hashed password stored in MongoDB
        const isMatch = await bcrypt.compare(passwordToCheck, user.password);
        console.log('Do passwords match?', isMatch);
    } catch (err) {
        console.error(err);
    } finally {
        await client.close();
    }
}

// Check password for the user
checkPassword('clientuser', 'securepassword'); // Use the same username and password you created
