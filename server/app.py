import pickle
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import pandas as pd

# MongoDB connection string
MONGO_URL = "mongodb+srv://atharva00:atharva_db123@cluster-atga-dev-01.bvrwcjt.mongodb.net/?retryWrites=true&w=majority&appName=cluster-atga-dev-01"

client = MongoClient(MONGO_URL)
db = client.user_database  # 'user_database' is the database name

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

# Load the trained RandomForestClassifier model using pickle
with open('random_forest_model.pkl', 'rb') as f:
    rf_model = pickle.load(f)

# Load the trained SVM model using pickle
with open('svm_model.pkl', 'rb') as f:
    svm_model = pickle.load(f)

app = Flask(__name__)
CORS(app, supports_credentials=True)

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

        # Insert the new user
        user_id = db.users.insert_one({'name': name, 'email': email, 'password': password}).inserted_id

        return jsonify({'message': 'User registered successfully', 'userId': str(user_id)}), 201

@app.route('/login', methods=['POST'])
def login_user():
    if request.method == 'POST':
        data = request.json
        email = data.get('email')
        password = data.get('password')

        if not (email and password):
            return jsonify({'error': 'Missing email or password'}), 400

        # Check if the user exists
        user = db.users.find_one({"email": email})

        if user and user['password'] == password:
            return jsonify({'message': 'Login successful'}), 200
        else:
            return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/predict_rf', methods=['POST'])
def predict_rf():
    if request.method == 'POST':
        # Get the data from the request
        data = request.json
        
        # Convert data to DataFrame
        df = pd.DataFrame(data)
        
        # Make prediction using the RandomForestClassifier model
        prediction = rf_model.predict(df)
        
        # Return the prediction as JSON
        return jsonify({'prediction': prediction.tolist()})

@app.route('/predict_svm', methods=['POST'])
def predict_svm():
    if request.method == 'POST':
        # Get the data from the request
        data = request.json
        
        # Convert data to DataFrame
        df = pd.DataFrame(data)
        
        # Make prediction using the SVM model
        prediction = svm_model.predict(df)
        
        # Return the prediction as JSON
        return jsonify({'prediction': prediction.tolist()})

if __name__ == '__main__':
    app.run(debug=True)
