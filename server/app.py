import pickle
import secrets
from flask import Flask, request, jsonify, session, render_template, send_from_directory
from flask_mail import Mail, Message
from flask_cors import CORS
from pymongo import MongoClient
import pandas as pd
from bson import ObjectId

import random
import string

from werkzeug.utils import secure_filename
import os
import uuid  # Import UUID module

app = Flask(__name__)
CORS(app, supports_credentials=True)
# Configure Flask-Mail with SMTP server details
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'abhidadavc@gmail.com'  # Your email address
app.config['MAIL_PASSWORD'] = 'prwt zmlh zemc fpcd'  # Your email password

mail = Mail(app)

from sklearn.metrics import accuracy_score 
from pandas import json_normalize
from sklearn.model_selection import train_test_split
from io import StringIO
import re
import datetime


# MongoDB connection string
MONGO_URL = "mongodb+srv://atharva00:atharva_db123@cluster-atga-dev-01.bvrwcjt.mongodb.net/?retryWrites=true&w=majority&appName=cluster-atga-dev-01"

client = MongoClient(MONGO_URL)
user_db = client.user_database  # 'user_database' is the database name
milk_db = client.Milk_Database
milkdata_collection = milk_db.milkdata

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)


def upload_csv_to_mongodb(csv_data, file_name, user_name, user_id):
    
    # Create metadata dictionary
    metadata = {
        'file_name': file_name,
        'upload_date': datetime.datetime.now(),
        'user_name': user_name,
        'user_id': user_id
    }
    milkdata_collection.insert_one(metadata)
 
    collection_name = re.sub(r'[^a-zA-Z0-9_]', '_', file_name.split('.')[0])

    # Convert CSV data to a pandas DataFrame
    df = pd.read_csv(StringIO(csv_data))
    # Convert DataFrame to dictionary records
    records = df.to_dict(orient='records')
    # Insert records into MongoDB collection
    milk_db[collection_name].insert_many(records)


@app.route('/upload-csv', methods=['POST'])
def upload_csv():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        try:
            # Read the CSV file
            csv_data = file.stream.read().decode("utf-8")
            # Get the file name
            file_name = file.filename
            # Get the logged-in user name from session
            user_token = request.args.get('token')
            if not user_token:
                return jsonify({'error': 'User not logged in'}), 401
            
            # Get the name of the logged-in user
            user = user_db.users.find_one({"token": user_token})
            if not user:
                return jsonify({'error': 'User not found'}), 404

            user_name = user.get('name')
            user_id = user.get('_id')
            # Load CSV data into MongoDB with dynamic collection name
            upload_csv_to_mongodb(csv_data, file_name, user_name, user_id)
            return jsonify({'message': f'CSV data loaded successfully into MongoDB collection {file_name}'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500



# Load the trained RandomForestClassifier model using pickle
with open('random_forest_model.pkl', 'rb') as f:
    rf_model = pickle.load(f)

# Load the trained SVM model using pickle
with open('svm_model.pkl', 'rb') as f:
    svm_model = pickle.load(f)


df = pd.read_csv("milknew.csv")

# Define features and target variable
X = df.drop('Grade', axis=1)
y = df['Grade']

# Split the data into training and testing sets

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.4, random_state=40)


rf_score = accuracy_score(y_test, rf_model.predict(X_test) )
svm_score = accuracy_score(y_test, svm_model.predict(X_test))
df = pd.read_csv("milknew.csv")

# Set secret key for session management
app.secret_key = 'your_secret_key_here'

# Function to generate a random token
def generate_token():
    return secrets.token_hex(16)

@app.route('/register', methods=['POST'])
def register_user():
    if request.method == 'POST':
        # Extract the data from request
        data = request.json
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        phone = data.get('phone')

        if not (name and email and password):
            return jsonify({'error': 'Missing name, email, or password'}), 400

        # Check if the user already exists
        if user_db.users.find_one({"email": email}):
            return jsonify({"error": "User already exists"}), 409

        # Generate token for the user
        token = generate_token()

        # Construct the new user object
        newUser = {'name': name, 'email': email, 'password': password,'phone':phone, 'token': token}

        # Insert the new user with token
        user_id = user_db.users.insert_one(newUser).inserted_id
        
        # Convert user_id to string
        user_id_str = str(user_id)

        # Convert ObjectId to string in newUser
        newUser['_id'] = str(newUser['_id'])
        
        return jsonify({'message': 'User registered successfully', 'userId': user_id_str, 'newUser': newUser}), 201
    
@app.route('/login', methods=['POST'])
def login_user():
    if request.method == 'POST':
        data = request.json
        email = data.get('email')
        password = data.get('password')

        if not (email and password):
            return jsonify({'error': 'Missing email or password'}), 400

        # Check if the user exists and verify the password
        user = user_db.users.find_one({"email": email, "password": password})

        if user:
            # Store user's token in session
            try:
                session['token'] = user.get('token')
            except Exception as e:
                print(e)
            # print("in login post req")
            # print(user)
            # print(session['token'])
            
            # sessionStorage.setItem('token', 'your_token_here');
            return jsonify({'message': 'Login successful','token':session['token']}), 200
        else:
            return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/user-details', methods=['GET'])
def get_user_details():
    token = request.args.get('token')
    if not token:
        return jsonify({'error': 'Token not provided'}), 400
    
    user = user_db.users.find_one({"token": token})

    if user:
        # Convert ObjectId to string
        user['_id'] = str(user['_id'])
        # Exclude password field for security
        user.pop('password', None)
        return jsonify({'user': user}), 200
    else:
        return jsonify({'error': 'User not found'}), 404


@app.route('/update-user-details', methods=['PUT'])
def update_user_details():
    token = request.args.get('token')  # Retrieve token from query parameter
    if token:
        user = user_db.users.find_one({"token": token})
        if user:
            # Extract updated data from request
            data = request.json
            updated_name = data.get('name')
            updated_password = data.get('password')
            updated_country = data.get('country')  # Get updated country value
            updated_state = data.get('state')  # Get updated state value
            updated_phone = data.get('phone')
            
            # Update user details if provided
            update_query = {}
            if updated_name:
                update_query["name"] = updated_name
            if updated_password:
                update_query["password"] = updated_password
            if updated_country:
                update_query["country"] = updated_country
            if updated_state:
                update_query["state"] = updated_state
            if updated_state:
                update_query["phone"] = updated_phone

            if update_query:
                user_db.users.update_one({"token": token}, {"$set": update_query})
            
            return jsonify({'message': 'User details updated successfully'}), 200
        else:
            return jsonify({'error': 'User not found'}), 404
    else:
        return jsonify({'error': 'Token not provided'}), 401


@app.route('/update-password', methods=['PUT'])
def update_password():
    token = request.args.get('token')
    if token:
        user = user_db.users.find_one({"token": token})
        if user:
            data = request.json
            updated_password = data.get('newPassword')  # Get the new password from the request

            # Update the user's password
            user_db.users.update_one({"token": token}, {"$set": {"password": updated_password}})

            return jsonify({'message': 'Password updated successfully'}), 200
        else:
            return jsonify({'error': 'User not found'}), 404
    else:
        return jsonify({'error': 'Token not provided'}), 401

@app.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('email')

    # Check if the email exists in the database
    user = user_db.users.find_one({'email': email})
    if not user:
        return jsonify({'error': 'User with this email does not exist'}), 404

    # Generate a random password reset token
    token = ''.join(random.choices(string.ascii_letters + string.digits, k=20))

    # Update the user's record in the database with the token
    user_db.users.update_one({'email': email}, {'$set': {'reset_password_token': token}})

    # Send an email to the user with a password reset link containing the token
    msg = Message('Password Reset', sender='abhivc12@gmail.com', recipients=[email])
    msg.body = f'Please click the following link to reset your password: http://localhost:5000/reset-password?token={token}'
    mail.send(msg)

    return jsonify({'message': 'Password reset instructions sent to your email'}), 200



@app.route('/reset-password', methods=['GET'])
def reset_password():
    token = request.args.get('token')
    # print("token in get request:",token)
    if not token:
        return jsonify({'error': 'Token not provided'}), 400

    # Find the user by the reset password token
    user = user_db.users.find_one({'reset_password_token': token})
    if not user:
        return jsonify({'error': 'Invalid or expired token'}), 404

    # Here you can render a password reset form or perform the password reset logic
    return render_template('reset-pwd.html',token=token)
   


@app.route('/reset-password', methods=['POST'])
def reset_pwd():
    token = request.args.get('token')
    # print("in post",token)
    if not token:
        return jsonify({'error': 'Token not provided'}), 400

    # Find the user by the reset password token
    user = user_db.users.find_one({'reset_password_token': token})
    if not user:
        return jsonify({'error': 'Invalid or expired token'}), 404

    new_password = request.json.get('password')
    if not new_password:
        return jsonify({'error': 'New password not provided'}), 400

    # Update the user's password in the database
    # You may want to hash the password before saving it
    # For example: hashed_password = hash_function(new_password)
    user_db.users.update_one({'_id': user['_id']}, {'$set': {'password': new_password}})

    # Optionally, clear the reset password token and expiry date
    user_db.users.update_one({'_id': user['_id']}, {'$unset': {'reset_password_token': ''}})

    return jsonify({'message': 'Password reset successfully'}), 200

    

@app.route('/predict_rf', methods=['POST'])
def predict_rf():
    if request.method == 'POST':
        # Get data from the request
        data = request.json
        # Normalize JSON data into a DataFrame
        df = json_normalize(data)
      
        # Make prediction using the RandomForestClassifier model
        prediction = rf_model.predict(df)
        
        # Return prediction and accuracy as JSON
        return jsonify({'prediction': prediction.tolist(), 'accuracy': rf_score * 100})


# Prediction endpoint for SVM model
@app.route('/predict_svm', methods=['POST'])
def predict_svm():
    if request.method == 'POST':
        # Get data from the request
        data = request.json
        
        # Normalize JSON data into a DataFrame
        df = json_normalize(data)
        # Make prediction using the SVM model
        prediction = svm_model.predict(df)
             
        # Return prediction and accuracy as JSON
        return jsonify({'prediction': prediction.tolist(), 'accuracy': svm_score* 100})
             
UPLOAD_FOLDER = 'uploads/avatars'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload-avatar', methods=['POST'])
def upload_avatar():
    token = request.args.get('token')  # Retrieve token from query parameter
    if token:
        user = user_db.users.find_one({"token": token})
        if user:
            # Check if the post request has the file part
            if 'avatar' not in request.files:
                return jsonify({'error': 'No file provided'}), 400

            file = request.files['avatar']

            # If user does not select file, browser also submit an empty part without filename
            if file.filename == '':
                return jsonify({'error': 'No selected file'}), 400

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)

                 # Generate a unique filename using UUID
                unique_filename = str(uuid.uuid4()) + '.' + filename.rsplit('.', 1)[1].lower()

                if 'avatar' in user:
                    existing_avatar_path = os.path.join(app.config['UPLOAD_FOLDER'], str(user['avatar']))
                    if os.path.exists(existing_avatar_path):
                        os.remove(existing_avatar_path)

                # Save the new avatar
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))

                # Update user's avatar filename in the database
                user_db.users.update_one({"token": token}, {"$set": {"avatar": unique_filename}})
                return jsonify({'message': 'Avatar uploaded successfully'}), 200
            else:
                return jsonify({'error': 'Invalid file type'}), 400
        else:
            return jsonify({'error': 'User not found'}), 404
    else:
        return jsonify({'error': 'Token not provided'}), 401


@app.route('/uploads/avatars/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':
    app.run(debug=True)
