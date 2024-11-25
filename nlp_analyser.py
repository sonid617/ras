from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os

app = Flask(__name__)
CORS(app)

# Set your OpenAI API key
openai.api_key = os.getenv('org-voFGXXlwqUYilQPstO3jSLBj')

def analyze_sentiment_with_openai(messages):
    results = []
    for message in messages:
        prompt = f"Analyze the sentiment of the following message and classify it as Friendly, Neutral, or Non-Friendly:\n\nMessage: \"{message}\""

        try:
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                max_tokens=60,
                temperature=0.7
            )
            
            sentiment = response.choices[0].text.strip().lower()

            if "friendly" in sentiment:
                behavior = "friendly"
            elif "non-friendly" in sentiment:
                behavior = "non-friendly"
            else:
                behavior = "neutral"
            
            results.append({
                "message": message,
                "sentiment": sentiment,
                "behavior": behavior
            })
        except Exception as e:
            results.append({
                "message": message,
                "sentiment": "unknown",
                "behavior": "unknown",
                "error": str(e)
            })
    
    return results

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    if not data or 'messages' not in data:
        return jsonify({"error": "Invalid input, 'messages' key missing."}), 400

    messages = data.get('messages', [])
    if not messages:
        return jsonify({"error": "Messages list is empty."}), 400

    results = analyze_sentiment_with_openai(messages)

    counts = {"friendly": 0, "neutral": 0, "non-friendly": 0}
    for result in results:
        behavior = result["behavior"]
        if behavior in counts:
            counts[behavior] += 1
            return jsonify(result)
    

if __name__ == "__main__":
    app.run(debug=True)
