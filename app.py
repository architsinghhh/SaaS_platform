from flask import Flask, request, jsonify, send_file
from flask_jwt_extended import get_jwt_identity, jwt_required
from pymongo import MongoClient
from werkzeug.security import check_password_hash, generate_password_hash
import jwt  # Use JWT for token management
import datetime
from bson import ObjectId
from flask_cors import CORS
import io
from gridfs import GridFS
from flask import Flask, request, jsonify
from flask_mail import Mail, Message
import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_mail import Mail, Message


app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Used for encoding JWT
JWT_SECRET_KEY = 'jwt_secret_key'
CORS(app)
# MongoDB setup
client = MongoClient("mongodb+srv://Ajnhawk:Ajnhawk@ajnhawk.u36yb.mongodb.net/")
db = client['projectdatabase']
users_collection = db['users']
projects_collection = db['projects']
fs = GridFS(db)  # Correctly initialize GridFS
# Configure Flask-Mail
# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Use your email provider's SMTP server
app.config['MAIL_PORT'] = 587  # Standard port for TLS
app.config['MAIL_USE_TLS'] = True  # Enable TLS
app.config['MAIL_USERNAME'] = 'kuttagta5@gmail.com'  # Your email address
app.config['MAIL_PASSWORD'] = 'Airtel4g@'  # Your email password or App Password
app.config['MAIL_DEFAULT_SENDER'] = 'no-reply@yourdomain.com'  # Generic sender address

mail = Mail(app)

# Fixed recipient email address
RECEIVER_EMAIL = 'kuttagta5@gmail.com'  # Replace with the email address you want to receive inquiries

@app.route('/send-inquiry', methods=['POST'])
def send_inquiry():
    data = request.get_json()
    user_email = data.get('email')  # This is where the user enters their email/website

    if not user_email:
        return jsonify({'message': 'Email is required!'}), 400

    # Create and send the email to the fixed receiver
    msg = Message(subject='New Inquiry from Website',
                  recipients=[RECEIVER_EMAIL],
                  body=f'You have received a new inquiry from: {user_email}.')
    
    try:
        mail.send(msg)
        print(f"Email sent successfully to {RECEIVER_EMAIL} regarding {user_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")  # Log the error
        return jsonify({'message': f'Failed to send email: {str(e)}'}), 500  # Return the error message

    return jsonify({'message': 'Inquiry email sent successfully!'}), 200

@app.route('/upload', methods=['POST'])
def upload_project():
    # Get form data
    print("hello1")
    username = request.form.get('username')
    password = request.form.get('password')
    project_name = request.form.get('project')

    print("hello2")
    if not username or not password or not project_name:
        return jsonify({'message': 'Missing fields'}), 400

    # Hash the password
    password_hash = generate_password_hash(password)

    # Store the user if they don’t already exist
    user = users_collection.find_one({'username': username})
    print("hello3")
    if not user:
        user_id = users_collection.insert_one({
            'username': username,
            'passwordHash': password_hash,
            'projects': []
        }).inserted_id
    else:
        user_id = user['_id']

    print("hello4")
    # Store the project
    project_id = projects_collection.insert_one({
        'userId': user_id,
        'name': project_name,
        'images': [],
        'model': None,  # Placeholder for model ID
    }).inserted_id

    print("hello5")
    # Handle file uploads
    images = request.files.getlist('images')
    if not images:
        return jsonify({'message': 'No images uploaded'}), 400

    image_ids = []
    for image in images:
        # Store the image in GridFS
        image_id = fs.put(image.read(), filename=image.filename, project_id=project_id)
        image_ids.append(image_id)

    print("hello6")
    # Update the project with the image IDs
    projects_collection.update_one(
        {'_id': project_id},
        {'$set': {'images': image_ids}}
    )

    # Handle model file upload
    model_file = request.files.get('model')  # Get the model file from the request
    if model_file:
        model_id = fs.put(model_file.read(), filename=model_file.filename, project_id=project_id)
        
        # Update the project with the model ID
        projects_collection.update_one(
            {'_id': project_id},
            {'$set': {'model': model_id}}  # Store the model ID in the project document
        )
    
    return jsonify({'message': 'Project, images, and model uploaded successfully!'})
    


# Generate a JWT token
def generate_token(user_id):
    token = jwt.encode({
        'user_id': str(user_id),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)  # Token expires in 1 day
    }, app.secret_key, algorithm='HS256')
    return token

# Route 1: User Login
@app.route('/login', methods=['POST'])
def login():
    try:
        # Parse request data
        data = request.json
        username = data.get('username')
        password = data.get('password')

        # Check for missing fields
        if not username or not password:
            return jsonify({'message': 'Username and password are required'}), 400

        # Find user in MongoDB
        user = users_collection.find_one({'username': username})
        if not user or not check_password_hash(user['passwordHash'], password):
            return jsonify({'message': 'Invalid username or password'}), 401

        # Generate token
        token = generate_token(user['_id'])

        return jsonify({'message': 'Login successful', 'token': token}), 200

    except Exception as e:
        # Handle unexpected errors
        return jsonify({'message': 'An error occurred during login', 'error': str(e)}), 500

# Route 2: List Projects for Logged-in User
# Route 2: List Projects for Logged-in User
@app.route('/welcome', methods=['GET'])
def list_projects():
    token = request.headers.get('Authorization')  # Get token from Authorization header
    if not token:
        return jsonify({'message': 'Token is missing'}), 401

    # Remove 'Bearer ' from token if it's prefixed
    if token.startswith("Bearer "):
        token = token[7:]

    try:
        # Decode the token to get the user_id
        data = jwt.decode(token, app.secret_key, algorithms=['HS256'])
        user_id = data['user_id']
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token has expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Invalid token'}), 401

    # Convert user_id to ObjectId
    try:
        user_id_obj = ObjectId(user_id)  # Convert user_id to ObjectId
    except Exception as e:
        return jsonify({'message': 'Invalid user ID format'}), 400

    # Fetch the user's data from the users collection to get the username
    user = users_collection.find_one({'_id': user_id_obj})
    if not user:
        return jsonify({'message': 'User not found'}), 404

    username = user.get('username', 'Guest')  # Use 'Guest' if no username is found

    # Find projects belonging to the logged-in user
    projects = projects_collection.find({'userId': user_id_obj})
    project_list = [{'id': str(project['_id']), 'name': project['name']} for project in projects]

    return jsonify({'username': username, 'projects': project_list})

@app.route('/project/<project_id>', methods=['GET'])
def get_project_details(project_id):
    token = request.headers.get('Authorization')  # Get token from Authorization header
    
    if not token:
        return jsonify({'message': 'Token is missing'}), 401

    # Remove 'Bearer ' from token if it is prefixed
    if token.startswith("Bearer "):
        token = token[7:]

    try:
        # Decode the JWT token
        data = jwt.decode(token, app.secret_key, algorithms=['HS256'])
        user_id = data['user_id']
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token has expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Invalid token'}), 401

    # Convert project_id to ObjectId
    try:
        project_obj_id = ObjectId(project_id)
    except Exception as e:
        return jsonify({'message': 'Invalid project ID format'}), 400

    # Find the project based on the project_id and the user's user_id
    project = projects_collection.find_one({'_id': project_obj_id, 'userId': ObjectId(user_id)})

    if project:
        # If project found, return the project details
        project_details = {
            'id': str(project['_id']),
            'name': project['name'],
            'description': project.get('description', 'No description available'),
            # Add any other project-related data you want to return
        }
        return jsonify(project_details)
    else:
        return jsonify({'message': 'Project not found'}), 404

@app.route('/projects/<project_id>/images', methods=['GET'])
def get_project_images(project_id):
    project = projects_collection.find_one({"_id": ObjectId(project_id)})  # Use projects_collection instead of mongo.db.projects
    if not project:
        return jsonify({"error": "Project not found"}), 404

    images = []
    for image_id in project['images']:
        image_data = fs.find_one({"_id": image_id})  # Use fs instead of mongo.db.fs.files
        if image_data:
            images.append({
                'id': str(image_data._id),  # Access _id directly
                'filename': image_data.filename,
                'url': f"http://127.0.0.1:5000/images/{image_id}",  # Create the URL for the image
                'content_type': image_data.content_type,
                'upload_date': image_data.upload_date.isoformat()
            })

    print(images)
    return jsonify(images), 200


@app.route('/images/<image_id>', methods=['GET'])
def get_image(image_id):
    # Fetch the image from GridFS
    image_data = fs.find_one({'_id': ObjectId(image_id)})
    
    if image_data:
        # Use the correct way to get the filename and read the file data
        filename = image_data.filename  # Access the filename property
        file_data = fs.get(image_data._id)  # Get the actual file data using the image ID

        # Use send_file to send the file data with proper parameters
        return send_file(io.BytesIO(file_data.read()), 
                         as_attachment=False,  # Change to False if you want to display in browser
                         download_name=filename,  # Specify the filename for download
                         mimetype='image/jpeg')  # Set the correct MIME type

    return jsonify({'message': 'Image not found'}), 404

from flask import jsonify, send_file
from bson.objectid import ObjectId

@app.route('/get_model/<project_id>', methods=['GET'])
def get_model(project_id):
    try:
        print("get model function hit")
        # Find the project by ID
        print(project_id)
        project = projects_collection.find_one({'_id': ObjectId(project_id)})
        if not project:
            return jsonify({'message': 'Project not found'}), 404

        # Check if the project has a model file
        if 'model' not in project:
            return jsonify({'message': 'No model file associated with this project'}), 404

        # Retrieve the model file from GridFS using the model ID
        model_file_id = project['model']  # This is the ID of the model file
        model_file = fs.get(ObjectId(model_file_id))  # Get the model file from GridFS

        if not model_file:
            return jsonify({'message': 'Model file not found'}), 404

        # Serve the model file (e.g., .glb, .obj, .ply) to the frontend
        return send_file(model_file, mimetype='application/octet-stream', as_attachment=True, download_name=model_file.filename)
    
    except Exception as e:
        return jsonify({'message': str(e)}), 500




@app.route('/logout', methods=['POST'])
def logout():
    return jsonify({"msg": "Successfully logged out"}), 200

@app.route('/save_annotations', methods=['POST'])
def save_annotations():
    print("save annotation function hit")
    token = request.headers.get('Authorization')  # Get token from Authorization header
    if not token:
        return jsonify({'message': 'Token is missing'}), 401

    # Remove 'Bearer ' from token if it's prefixed
    if token.startswith("Bearer "):
        token = token[7:]

    try:
        # Decode the token to get the user_id
        data = jwt.decode(token, app.secret_key, algorithms=['HS256'])
        user_id = data['user_id']
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token has expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Invalid token'}), 401

    # Convert user_id to ObjectId
    try:
        user_id_obj = ObjectId(user_id)  # Convert user_id to ObjectId
    except Exception as e:
        return jsonify({'message': 'Invalid user ID format'}), 400

    # Fetch the user's data from the users collection to get the username
    user = users_collection.find_one({'_id': user_id_obj})
    print(user)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    # Get the JSON data from the request
    data = request.get_json()
    if not data:
        return jsonify({'message': 'Request body is missing'}), 400

    # Get the project ID from the JSON data
    project_id = data.get('project_id')
    print(project_id)
    if not project_id:
        return jsonify({'message': 'Project ID is missing'}), 400
    

    # Convert project_id to ObjectId
    try:
        project_id_obj = ObjectId(project_id)
    except Exception as e:
        return jsonify({'message': 'Invalid project ID format'}), 400

    project = projects_collection.find_one({'_id': project_id_obj})
    if not project:
        return jsonify({'message': 'project not found'}), 404

    project_name = project.get('name')
    print(f"Project Name: {project_name}")

    # Retrieve the annotations from the JSON data
    annotations = data.get('annotations')
    if not annotations:
        return jsonify({'message': 'Annotations are missing'}), 400

    # Convert annotations to a format suitable for saving (if necessary)
    # For example, you can convert it to JSON or handle it based on your requirements

    # Save the annotations in the database (implement your save logic here)
    # Example: saving directly to a collection
    annotations_collection = db['annotations']
    annotation_entry = {
        'user_id': user_id_obj,
        'project_id': project_id_obj,
        'project_name': project_name,
        'annotations': annotations,  # Save annotations directly or process them as needed
    }
    annotations_collection.insert_one(annotation_entry)

    return jsonify({'message': 'Annotations saved successfully'}), 201


@app.route('/save_drone_annotations', methods=['POST'])
def save_drone_annotations():
    print("save annotation function hit")
    token = request.headers.get('Authorization')  # Get token from Authorization header
    if not token:
        return jsonify({'message': 'Token is missing'}), 401

    # Remove 'Bearer ' from token if it's prefixed
    if token.startswith("Bearer "):
        token = token[7:]

    try:
        # Decode the token to get the user_id
        data = jwt.decode(token, app.secret_key, algorithms=['HS256'])
        user_id = data['user_id']
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token has expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Invalid token'}), 401

    # Convert user_id to ObjectId
    try:
        user_id_obj = ObjectId(user_id)  # Convert user_id to ObjectId
    except Exception as e:
        return jsonify({'message': 'Invalid user ID format'}), 400

    # Fetch the user's data from the users collection to get the username
    user = users_collection.find_one({'_id': user_id_obj})
    print(user)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    # Get the JSON data from the request
    data = request.get_json()
    if not data:
        return jsonify({'message': 'Request body is missing'}), 400

    # Get the project ID from the JSON data
    project_id = data.get('project_id')
    print(project_id)
    if not project_id:
        return jsonify({'message': 'Project ID is missing'}), 400
    

    # Convert project_id to ObjectId
    try:
        project_id_obj = ObjectId(project_id)
    except Exception as e:
        return jsonify({'message': 'Invalid project ID format'}), 400

    project = projects_collection.find_one({'_id': project_id_obj})
    if not project:
        return jsonify({'message': 'project not found'}), 404

    project_name = project.get('name')
    print(f"Project Name: {project_name}")

    # Retrieve the annotations from the JSON data
    annotations = data.get('annotations')
    if not annotations:
        return jsonify({'message': 'Annotations are missing'}), 400

    # Convert annotations to a format suitable for saving (if necessary)
    # For example, you can convert it to JSON or handle it based on your requirements

    # Save the annotations in the database (implement your save logic here)
    # Example: saving directly to a collection
    annotations_collection = db['drone_annotations']
    annotation_entry = {
        'user_id': user_id_obj,
        'project_id': project_id_obj,
        'project_name': project_name,
        'annotations': annotations,  # Save annotations directly or process them as needed
    }
    annotations_collection.insert_one(annotation_entry)

    return jsonify({'message': 'Annotations saved successfully'}), 201



if __name__ == '__main__':
    app.run(debug=True)