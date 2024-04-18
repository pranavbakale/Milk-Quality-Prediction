import pickle
import secrets
from flask import Flask, request, jsonify, send_file, session, render_template, send_from_directory
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
import pandas as pd
import numpy as np
import pickle
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from datetime import datetime
import matplotlib
matplotlib.use('Agg')  # Use the 'Agg' backend
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import accuracy_score 
from pandas import json_normalize
from sklearn.model_selection import train_test_split
from io import BytesIO, StringIO
import re
import datetime
from dateutil.relativedelta import relativedelta
from fpdf import FPDF

import smtplib
from email.message import EmailMessage
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

app = Flask(__name__)
CORS(app, supports_credentials=True)
# Configure Flask-Mail with SMTP server details
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'abhidadavc@gmail.com'  # Your email address
app.config['MAIL_PASSWORD'] = 'prwt zmlh zemc fpcd'  # Your email password

mail = Mail(app)

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
    current_date_time = datetime.datetime.now()
    formatted_date_time = current_date_time.strftime('%b_%d_%f')
    print("Metadata:", metadata)  # Print metadata dictionary
    
    collection_name = re.sub(r'[^a-zA-Z0-9_]', '_', file_name.split('.')[0]+formatted_date_time)
    print("Collection name:", collection_name)  # Print collection name
    
    # Convert CSV data to a pandas DataFrame
    df = pd.read_csv(StringIO(csv_data))
    # Convert DataFrame to dictionary records
    records = df.to_dict(orient='records')
    print("Records:", records)  # Print records
    # Insert records into MongoDB collection
    milk_db[collection_name].insert_many(records)
    milkdata_collection.insert_one(metadata)



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

with open('ensemble_model.pkl', 'rb') as f:
    rf_model, svm_model, meta_model, acccuracy = pickle.load(f)

# Load the dataset
df = pd.read_csv('milknew.csv')
grade_mapping = {'low': 0, 'medium': 1, 'high': 2}

# Map the categorical values to numerical values
df['Grade'] = df['Grade'].map(grade_mapping)
# Define features and target variable
X = df.drop('Grade', axis=1)
y = df['Grade']

# Define preprocessing steps (standardization for numerical features)
numerical_features = ['Taste', 'Odor', 'Colour']
preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numerical_features)
    ],
    remainder='passthrough'
)

# Fit and transform the entire dataset
X_encoded = preprocessor.fit_transform(X)

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X_encoded, y, test_size=0.4, random_state=42)

# Train the base models
rf_model.fit(X_train, y_train)
svm_model.fit(X_train, y_train)

# Generate predictions from base models
rf_predictions = rf_model.predict(X_test)
svm_predictions = svm_model.predict(X_test)

# Create a new dataset with base model predictions as features
X_stacked = np.column_stack((rf_predictions, svm_predictions))

# Train the meta-model (Logistic Regression) on the stacked dataset
meta_model.fit(X_stacked, y_test)


app.secret_key = 'your_secret_key_here'

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

        if user_db.users.find_one({"email": email}):
            return jsonify({"error": "User already exists"}), 409

        token = generate_token()

        # Construct the new user object
        newUser = {'name': name, 'email': email, 'password': password,'phone':phone, 'token': token}

        # Insert the new user with token
        user_id = user_db.users.insert_one(newUser).inserted_id
        

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
    msg = Message('Password Reset', sender='abhidadavc@gmail.com', recipients=[email])
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


@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    df = json_normalize(data)
    # Perform preprocessing
    data_encoded = preprocessor.transform(df)
    # Generate predictions from base models
    rf_prediction = rf_model.predict(data_encoded)
    svm_prediction = svm_model.predict(data_encoded)
    
    # Create a new dataset with base model predictions as features
    X_stacked = np.column_stack((rf_prediction, svm_prediction))

    # Make prediction using the meta-model
    meta_prediction = meta_model.predict(X_stacked)

    if(meta_prediction[0]==0):
        pred = 'low'
    elif(meta_prediction[0]==1):
        pred= 'medium'
    else:
        pred='high'
    approximated_accuracy = round(acccuracy * 100, 2)
    pH = data.get('pH')
    temperature = data.get('Temperature')
    taste = data.get('Taste')
    odor = data.get('Odor')
    fat = data.get('Fat')
    turbidity = data.get('Turbidity')
    colour = data.get('Colour')
    current_date = datetime.datetime.now().strftime('%d-%b-%Y')
    current_month = datetime.datetime.now().month
    current_year = datetime.datetime.now().year
    user_token = request.args.get('token')
    user = user_db.users.find_one({"token": user_token})
    user_id = user.get('_id')
    time = datetime.datetime.now().strftime("%H:%M:%S")
    Grade = pred
    prediction_data = {
        'user_id':user_id,
        'time': time,
        'date': current_date,
        'month': current_month,
        'year': current_year,
        'pH': pH,
        'Temperature': temperature,
        'Taste': taste,
        'Odor': odor,
        'Fat':fat,
        'Turbidity':turbidity,
        'Colour':colour,
        'Grade': Grade
    }
    milk_db.milk_prediction_result.insert_one(prediction_data)
    return jsonify({'prediction': pred, 'accuracy':  approximated_accuracy})

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



@app.route('/last-six-months-data', methods=['POST'])
def get_last_six_months_data():
    files = []
    user_token = request.args.get('token')
    user = user_db.users.find_one({'token':user_token})
    user_id = user.get('_id')
    current_year = datetime.datetime.now().year
    current_month = datetime.datetime.now().month

    for i in range(6):
        target_month = current_month - i
        target_year = current_year
        if target_month <= 0:
            target_month += 12
            target_year -= 1

        data_exists = milk_db.milk_prediction_result.find_one(
            {'month': target_month, 'year': target_year,'user_id': user_id}
        )
     
        if data_exists:
            current_month_data_cursor = milk_db.milk_prediction_result.find(
                {'month': target_month, 'year': target_year , 'user_id':user_id},
                {'_id': 0}
            )

            current_month_data_df = pd.DataFrame(list(current_month_data_cursor))
            columns_to_keep = ['date','time','pH', 'Temperature', 'Taste', 'Odor', 'Fat', 'Turbidity', 'Colour', 'Grade']
            current_month_data_df = current_month_data_df[columns_to_keep]
            month_year_str = datetime.datetime(target_year, target_month, 1).strftime('%b%Y')
            csv_file_name = f'milk_data_{month_year_str}.csv'
            #file path
            csv_file_path = os.path.join(app.root_path, csv_file_name)
            current_month_data_df.to_csv(csv_file_path, index=False)

            files.append({'file_name': csv_file_name, 'file_path': csv_file_path})

    return jsonify(files)



# API endpoint to get pH data
@app.route('/api/pH')
def get_pH_data():
    pH_data = df['pH'].tolist()
    return jsonify(pH_data)

# API endpoint to get temperature data
@app.route('/api/temperature')
def get_temperature_data():
    temperature_data = df['Temperature'].tolist()
    return jsonify(temperature_data)

# API endpoint to get color data
@app.route('/api/color')
def get_color_data():
    color_data = df['Colour'].value_counts().to_dict()
    return jsonify(color_data)

@app.route('/get-predictions', methods=['GET'])
def get_predictions():
    # Get the current year and month
    current_year = datetime.datetime.now().year
    current_month = datetime.datetime.now().month

    # Generate the file name using the current year and month
    month_year_str = datetime.datetime(current_year, current_month, 1).strftime('%b%Y')
    # print("in backedn month year",month_year_str)
    csv_file_name = f'milk_data_{month_year_str}.csv'
    csv_file_path = os.path.join(app.root_path, csv_file_name)

    # Check if the CSV file exists
    if os.path.exists(csv_file_path):
        # Read the CSV file into a DataFrame
        df = pd.read_csv(csv_file_path)
        df = df.sort_values(by=['date', 'time'], ascending=False)
        value_counts_series = df['Grade'].value_counts()

# If you want to convert the result to a DataFrame
        value_counts_df = value_counts_series.reset_index()
        value_counts_df.columns = ['Value', 'Count']
        # Convert DataFrame to a list of dictionaries
        grade_count = value_counts_df.to_dict(orient='records')
        predictions = df.to_dict(orient='records')
        # get_csvdata(df)
        # Return predictions as JSON response
        return jsonify({'predictions': predictions, 'grade_count':grade_count})
    else:
        return jsonify({'predictions': predictions})



GRAPH_FOLDER = 'graphs'
app.config['GRAPH_FOLDER'] = GRAPH_FOLDER

@app.route('/generate-graphs', methods=['POST'])
def generate_graphs():
    attribute = request.json.get('attribute')


    # Check if attributes are provided
    if not attribute:
        return jsonify({'error': 'Attributes not provided'}), 400

    graph_dir = os.path.join(app.root_path, app.config['GRAPH_FOLDER'])
    if not os.path.exists(graph_dir):
        os.makedirs(graph_dir)

    # List all files in the static directory
    existing_files = os.listdir(graph_dir)

    # Iterate over existing files and remove graphs
    for file in existing_files:
        if file.endswith('.png'):  # Check if file is a PNG image
            os.remove(os.path.join(graph_dir, file))  # Delete the file

     # Save the graphs in the graph folder
    line_plot_path = os.path.join(graph_dir, 'line_plot.png')
    histogram_path = os.path.join(graph_dir, 'histogram.png')
    box_plot_path = os.path.join(graph_dir, 'box_plot.png')
    heatmap_path = os.path.join(graph_dir, 'heatmap.png')
    count_plot_path = os.path.join(graph_dir,'count_plot.png')
    current_year = datetime.datetime.now().year
    current_month = datetime.datetime.now().month

    # Generate the file name using the current year and month
    month_year_str = datetime.datetime(current_year, current_month, 1).strftime('%b%Y')
    # print("in backedn month year",month_year_str)
    csv_file_name = f'milk_data_{month_year_str}.csv'
    csv_file_path = os.path.join(app.root_path, csv_file_name)

    # Check if the CSV file exists
    if os.path.exists(csv_file_path):
        # Read the CSV file into a DataFrame
        df = pd.read_csv(csv_file_path)
    else:
        return jsonify({'error': 'CSV file not found'}), 404
  
    numeric_columns = df.select_dtypes(include=['number']).columns
    df_numeric = df[numeric_columns]
    df = df.sort_values(by='date', ascending=True)
    plt.figure(figsize=(10, 6))
    plt.plot(df['date'], df[attribute], label=attribute)
    plt.xlabel('Date')
    plt.ylabel('Attribute Value')
    plt.title('Time Series Analysis')
    plt.legend()
    plt.savefig(line_plot_path)
    plt.close()

    # Histogram for attribute distribution
    plt.figure(figsize=(10, 6))
    sns.histplot(df[attribute], kde=True, color='blue', label=attribute)
    plt.xlabel('Attribute Value')
    plt.ylabel('Frequency')
    plt.title('Attribute Distribution')
    plt.legend()
    plt.savefig(histogram_path)
    plt.close()

    # Box plot for attribute variation
    plt.figure(figsize=(10, 6))
    sns.boxplot(data=df[[attribute]])
    plt.ylabel('Attribute Value')
    plt.title('Attribute Variation')
    plt.savefig(box_plot_path)
    plt.close()

    plt.figure(figsize=(12,8))
    plt.title("Attribute of Milk",fontsize=15)
    c1=sns.countplot(x=attribute,data=df,palette="deep")
    c1.bar_label(c1.containers[0],size=12)
    plt.xticks(rotation=45)
    plt.savefig(count_plot_path)

    # Heatmap for correlation matrix
    plt.figure(figsize=(10, 6))
    sns.heatmap(df_numeric.corr(), annot=True, cmap='coolwarm')
    plt.title('Correlation Matrix')
    plt.savefig(heatmap_path)
    plt.close()

    return jsonify({
        'linePlotUrl': 'line_plot.png',
        'histogramUrl': 'histogram.png',
        'boxPlotUrl':  'box_plot.png',
        'countPlotUrl': 'count_plot.png',
        'heatmapUrl': 'heatmap.png'
    })

@app.route('/graphs/<path:filename>')
def send_graphs(filename):
    return send_from_directory(app.config['GRAPH_FOLDER'], filename)

# app.config['GRAPH_FOLDER'] = 'graph-data'
# app.config['INSIGHT_PDF_FOLDER'] = 'graph-data-pdf'

# graph_dir = os.path.join(app.root_path, app.config['GRAPH_FOLDER'])

# line_plot_path = os.path.join(graph_dir, 'line_plot.png')
# histogram_path = os.path.join(graph_dir, 'histogram.png')
# box_plot_path = os.path.join(graph_dir, 'box_plot.png')
# heatmap_path = os.path.join(graph_dir, 'heatmap.png')
# count_plot_path = os.path.join(graph_dir,'count_plot.png')

# graph_urls = [line_plot_path,histogram_path,box_plot_path, heatmap_path,count_plot_path]
# @app.route('/generate-graphs-pdf', methods=['GET'])
# def generate_pdf(graph_urls):
#     # Create a canvas object to generate PDF
#     c = canvas.Canvas("report.pdf", pagesize=letter)
   
#     # Add graphs to the PDF
#     for index, url in enumerate(graph_urls):
#         c.drawImage(url, x=50, y=600 - (index * 200), width=400, height=200)

#     # Add insights and analysis
#     c.drawString(50, 500, "Insights:")
#     y_position = 480
#     for insight in insights:
#         c.drawString(50, y_position, insight)
#         y_position -= 20
   
#     # Save the PDF
#     c.save()

# # Function to send email with PDF attachment
# def send_email_with_attachment(email, pdf_filename):
#     # Create an EmailMessage object
#     msg = EmailMessage()
#     msg['Subject'] = 'Your Graphs and Insights'
#     msg['From'] = 'your_email@example.com'
#     msg['To'] = email
#     msg.set_content('Please find attached the PDF with your graphs and insights.')

#     # Attach the PDF to the email
#     with open(pdf_filename, 'rb') as file:
#         file_data = file.read()
#         msg.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=pdf_filename)

#     # Send the email using SMTP
#     with smtplib.SMTP('smtp.example.com', 587) as smtp:
#         smtp.starttls()
#         smtp.login('your_email@example.com', 'your_email_password')
# #         smtp.send_message(msg)

# # Usage
# if __name__ == "__main__":
#     # Replace these with your actual graph URLs and insights
#     graph_urls = ['graph1.png', 'graph2.png', 'graph3.png']
#     insights = ['Insight 1', 'Insight 2', 'Insight 3']

#     # Generate PDF
#     generate_pdf(graph_urls)

#     # Send email with PDF attachment
#     send_email_with_attachment('recipient@example.com', 'report.pdf')


# def generate_graphs_pdf():
#     attribute = request.json.get('attribute')
#     # Check if attributes are provided
#     if not attribute:
#         return jsonify({'error': 'Attributes not provided'}), 400

#     # Generate the plots (Replace this section with your actual plot generation code)
#     line_plot_path = os.path.join(app.root_path, app.config['GRAPH_FOLDER'], 'line_plot.png')
#     histogram_path = os.path.join(app.root_path, app.config['GRAPH_FOLDER'], 'histogram.png')
#     box_plot_path = os.path.join(app.root_path, app.config['GRAPH_FOLDER'], 'box_plot.png')
#     heatmap_path = os.path.join(app.root_path, app.config['GRAPH_FOLDER'], 'heatmap.png')
#     count_plot_path = os.path.join(app.root_path, app.config['GRAPH_FOLDER'], 'count_plot.png')

#     # Create a BytesIO object to store the PDF
#     pdf_bytes = BytesIO()

#     # Create a PDF document
#     pdf = FPDF()
#     pdf.set_auto_page_break(auto=True, margin=15)

#     # Add a page
#     pdf.add_page()

#     # Add the plots to the PDF
#     pdf.image(line_plot_path, x=10, y=10, w=180)
#     pdf.image(histogram_path, x=10, y=120, w=180)
#     pdf.image(box_plot_path, x=10, y=230, w=180)
#     pdf.image(count_plot_path, x=10, y=340, w=180)
#     pdf.image(heatmap_path, x=10, y=450, w=180)

#     # Generate the PDF file path
#     pdf_file_path = os.path.join(app.root_path, app.config['INSIGHT_PDF_FOLDER'], 'graphs.pdf')

#     # Output the PDF to the file system
#     pdf.output(pdf_file_path)

#     # Return the path to the folder containing the PDF file
#     return jsonify({'pdf_folder_path': os.path.dirname(pdf_file_path)})

if __name__ == '__main__':
    app.run(debug=True)