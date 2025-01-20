from flask import Flask, request, jsonify
from textblob import TextBlob
import json

app = Flask(__name__)

# Word and phrase categories
BAD_WORDS = ["kill", "hate", "murder", "attack", "destroy", "curse", 'death',"starve you to death",'randi','whore',]
BAD_PHRASES = ['mar daluga', 'chutiya', 'madarchod', 'bhosdike', 'mari nakhis', 'bhenchod', 'starve you to death']
FRIENDLY_WORDS = ['bhai', 'yrr', 'dost', 'friend', 'brother', 'bro', 'sis', 'bhen','Bhai','baby','bacha','babe']
NEUTRAL_WORDS = ['are', 'tane', 'teri', 'no', 'yes', 'su', 'vaat']

def analyze_sentiment(message):
    message_lower = message.lower()
    message_words = message_lower.split()

    # Count categories and collect non-friendly words
    non_friendly_count = 0
    friendly_count = 0
    neutral_count = 0
    non_friendly_words = []

    # Analyze word by word
    for word in message_words:
        if word in BAD_WORDS or any(phrase in message_lower for phrase in BAD_PHRASES):
            non_friendly_count += 1
            non_friendly_words.append(word)
        elif word in FRIENDLY_WORDS:
            friendly_count += 1
        elif word in NEUTRAL_WORDS:
            neutral_count += 1

    # Perform sentiment analysis using TextBlob for backup analysis
    analysis = TextBlob(message)
    sentiment = analysis.sentiment.polarity
    
    behavior = 'neutral'  # Default behavior

    if non_friendly_count > 0:
        if non_friendly_count > friendly_count and non_friendly_count > neutral_count:
            behavior = 'non-friendly'
        elif non_friendly_count == friendly_count or non_friendly_count == neutral_count:
            behavior = 'potential non-friendly'
    elif sentiment > 0.1:
        behavior = 'friendly'
    elif sentiment < -0.1:
        behavior = 'non-friendly'

    return behavior, non_friendly_count, friendly_count, neutral_count, non_friendly_words

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    messages = data['messages']
    results = []
    total_counts = {
        "non_friendly": 0,
        "friendly": 0,
        "neutral": 0
    }

    for message in messages:
        behavior, non_friendly_count, friendly_count, neutral_count, non_friendly_words = analyze_sentiment(message)
        
        # Update total counts
        total_counts["non_friendly"] += non_friendly_count
        total_counts["friendly"] += friendly_count
        total_counts["neutral"] += neutral_count

        results.append({
            'message': message,
            'sentiment': behavior,
            'behavior': behavior,
            'non_friendly_words': sorted(non_friendly_words)  # Sort non-friendly words alphabetically
        })

    return jsonify(results=results, counts=total_counts)

@app.route('/notify', methods=['POST'])
def notify():
    data = request.json
    with open("notifications.log", "a") as logfile:
        # Organize the notification in a more readable format
        log_entry = {
            "message_type": data.get('message_type'),
            "messages": data.get('messages'),
            "analysis": data.get('analysis'),
            "non_friendly_words": sorted(data.get('non_friendly_words', []))  # Sort the non-friendly words
        }

        # Write log entry as JSON for better structure
        logfile.write(json.dumps(log_entry, indent=4) + "\n\n")  # Add indent and spacing for better readability

    if data.get('message_type') == 'non-friendly':
        print("Alert: Non-friendly message detected!")
        print(f"Non-friendly words: {sorted(data.get('non_friendly_words'))}")

    return jsonify({"status": "success", "message": "Notification received!"}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
