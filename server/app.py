import pickle
import secrets
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from pymongo import MongoClient
import pandas as pd
from bson import ObjectId
from sklearn.metrics import accuracy_score 
from pandas import json_normalize
from sklearn.model_selection import train_test_split

# MongoDB connection string
MONGO_URL = "mongodb+srv://atharva00:atharva_db123@cluster-atga-dev-01.bvrwcjt.mongodb.net/?retryWrites=true&w=majority&appName=cluster-atga-dev-01"

client = MongoClient(MONGO_URL)
db = client.user_database  # 'user_database' is the database name

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)


app = Flask(__name__)
CORS(app, supports_credentials=True)



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

        if not (name and email and password):
            return jsonify({'error': 'Missing name, email, or password'}), 400

        # Check if the user already exists
        if db.users.find_one({"email": email}):
            return jsonify({"error": "User already exists"}), 409

        # Generate token for the user
        token = generate_token()

        # Construct the new user object
        newUser = {'name': name, 'email': email, 'password': password, 'token': token}

        # Insert the new user with token
        user_id = db.users.insert_one(newUser).inserted_id
        
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
        user = db.users.find_one({"email": email, "password": password})

        if user:
            # Store user's token in session
            session['token'] = user.get('token')
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

    user = db.users.find_one({"token": token})
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
        user = db.users.find_one({"token": token})
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
                db.users.update_one({"token": token}, {"$set": update_query})
            
            return jsonify({'message': 'User details updated successfully'}), 200
        else:
            return jsonify({'error': 'User not found'}), 404
    else:
        return jsonify({'error': 'Token not provided'}), 401



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

if __name__ == '__main__':
    app.run(debug=True)