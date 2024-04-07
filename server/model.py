import pickle
from flask import Flask, request, jsonify
import pandas as pd

# Load the dataset
df = pd.read_csv("milknew.csv")

# Model training
# Define features and target variable
X = df.drop('Grade', axis=1)
y = df['Grade']


# Split the data into training and testing sets
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Train RandomForestClassifier
from sklearn.ensemble import RandomForestClassifier

# Initialize the RandomForestClassifier
rf = RandomForestClassifier()

# Train the model
rf.fit(X_train, y_train)

# Save the trained RandomForestClassifier model using pickle
with open('random_forest_model.pkl', 'wb') as f:
    pickle.dump(rf, f)

# Train SVM
from sklearn.svm import SVC

# Initialize the SVC model
svc = SVC()

# Train the model
svc.fit(X_train, y_train)

# Save the trained SVM model using pickle
with open('svm_model.pkl', 'wb') as f:
    pickle.dump(svc, f)

