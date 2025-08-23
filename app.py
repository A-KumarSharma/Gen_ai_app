from flask import Flask, render_template, request, jsonify
import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()  # Loads variables from .env into environment


app = Flask(__name__)

# Load local data from JSON file
with open('training_data.json') as f:
    local_data = json.load(f)

# OpenRouter API endpoint and key
OPENROUTER_API_URL = 'https://openrouter.ai/api/v1/chat/completions'
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
 # Replace with your actual API key

# Sample data for regulations
regulations = {
    "FDA": "Food and Drug Administration",
    "EPA": "Environmental Protection Agency"
}

@app.route('/')
def index():
    return render_template('index.html', regulations=regulations)

@app.route('/ask', methods=['POST'])
def ask():
    country = request.form['country']
    regulation = request.form['regulation']
    question = request.form['question']
    
    # Check local data first
    local_answer = check_local_data(regulation, country, question)
    
    if local_answer:
        return jsonify({'answer': local_answer})
    
    # If no local answer, call the LLM to get the answer
    answer = get_llm_answer(question, regulation, country)
    
    return jsonify({'answer': answer})

def check_local_data(regulation, country, question):
    if regulation in local_data and country in local_data[regulation]:
        for key in local_data[regulation][country]:
            if question.lower() in key.lower():
                return local_data[regulation][country][key]
    return None

def get_llm_answer(question, regulation, country):
    prompt = f"Provide a detailed answer to the following question regarding {regulation} in {country}: {question}"
    
    payload = {
        "model": "deepseek/deepseek-r1-0528:free",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        # "HTTP-Referer": "https://your-site.com",  # Optional: Replace with your site
        # "X-Title": "Your App Name",              # Optional: Replace with your app name
    }

    response = requests.post(OPENROUTER_API_URL, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        try:
            return response.json()['choices'][0]['message']['content']
        except Exception:
            return "Error: Malformed response from OpenRouter."
    else:
        return f"Error: OpenRouter API returned status code {response.status_code}"

if __name__ == '__main__':
    app.run(debug=True)
