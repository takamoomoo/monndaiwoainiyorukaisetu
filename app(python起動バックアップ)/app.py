from flask import Flask, render_template, request, jsonify
import csv
import os
import random

app = Flask(__name__)

DATA_FILE = r"E:\Mypython\土地家屋調査士試験\app\data.csv"

def load_data():
    questions = []
    try:
        with open(DATA_FILE, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                questions.append(row)
    except Exception as e:
        print(f"Error loading data: {e}")
    return questions

@app.route('/')
def index():
    data = load_data()
    years = sorted(list(set(q['Year'] for q in data if q['Year'])))
    categories = sorted(list(set(q['Category'] for q in data if q['Category'])))
    return render_template('index.html', years=years, categories=categories)

@app.route('/quiz')
def quiz():
    year = request.args.get('year')
    category = request.args.get('category')
    
    data = load_data()
    filtered_questions = []
    
    for q in data:
        if year and q['Year'] != year:
            continue
        if category and q['Category'] != category:
            continue
        filtered_questions.append(q)
    
    if not filtered_questions:
        return "No questions found for this selection.", 404

    # Select a random question from the filtered list (or just the first one for simplicity/testing)
    # For a "study mode", sequential might be better, but let's do random for "Sukima"
    question = random.choice(filtered_questions)
    
    return render_template('quiz.html', question=question)

@app.route('/next_question')
def next_question():
    # Similar to /quiz but returns JSON for dynamic loading if we want,
    # or just redirects to /quiz with same params.
    # For simplicity, let's keep it server-side rendered for now.
    return quiz()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
