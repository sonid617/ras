import requests
import json
import pandas as pd

# Function to get predictions from the Flask server
def get_predictions(messages):
    """Send messages to the Flask server for sentiment analysis."""
    try:
        response = requests.post(
            'http://localhost:5000/analyze',
            headers={'Content-Type': 'application/json'},
            data=json.dumps({"messages": messages})
        )
        if response.status_code == 200:
            return response.json()  # Return the JSON response if successful
        else:
            print(f"Error: {response.status_code}")
            return []
    except Exception as e:
        print(f"Exception occurred: {e}")
        return []

# Function to calculate accuracy
def calculate_accuracy(test_data, predictions):
    """Calculate the accuracy of the model based on predictions."""
    correct = 0
    total = len(test_data)
    
    for i, item in enumerate(test_data):
        true_label = item['sentiment']  # Get the true label
        predicted_label = predictions[i]['sentiment']  # Get the predicted label
        
        if true_label == predicted_label:  # Compare true and predicted labels
            correct += 1  # Increment correct predictions
    
    # Calculate accuracy as the ratio of correct predictions to total
    accuracy = (correct / total) * 100
    return accuracy

# Load the dataset from a CSV file
csv_file_path = r'C:\Users\ASUS\Downloads\archive (3)\chat_dataset.csv'  # Use raw string notation

# Read the CSV file using pandas
import pandas as pd
data = pd.read_csv(csv_file_path)

# Continue with the rest of your code...


# Extract messages and labels
test_data = data[['message', 'sentiment']].to_dict(orient='records')  # Convert to list of dictionaries

# Extract messages for prediction
test_messages = [item['message'] for item in test_data]

# Get predictions from the Flask server
predictions = get_predictions(test_messages)

# Calculate the accuracy of the model
if predictions:
    accuracy = calculate_accuracy(test_data, predictions)
    print(f"Model Accuracy: {accuracy:.2f}%")
else:
    print("Failed to get predictions from the server.")
