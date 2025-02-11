const bcrypt = require('bcrypt');
const { MongoClient } = require('mongodb');

async function createUser(username, password) {
    const uri = "mongodb://localhost:27017";
    const client = new MongoClient(uri);

    try {
        await client.connect();
        const db = client.db('clientDatabase');
        const usersCollection = db.collection('users');

        // Hash the password before saving to the database
        const hashedPassword = await bcrypt.hash(password, 10);
        const user = { username, password: hashedPassword };

        // Insert user into the database
        await usersCollection.insertOne(user);
        console.log(`User ${username} created successfully with hashed password: ${hashedPassword}`);
    } catch (err) {
        console.error(err);
    } finally {
        await client.close();
    }
}

// Create a user
createUser('clientuser', 'securepassword');
