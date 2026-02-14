from flask import Flask, render_template, request, redirect, url_for
import csv
import os
import random
import re

app = Flask(__name__)

# Use relative path for compatibility with both local Windows and Render (Linux)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, 'data.csv')

def extract_number(text):
    # Extract number from "問１" or "第1問" etc. using regex
    # Handles both half-width and full-width numbers
    match = re.search(r'(\d+)', text.translate(str.maketrans('０１２３４５６７８９', '0123456789')))
    return int(match.group(1)) if match else 999

def load_data():
    questions = []
    try:
        with open(DATA_FILE, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Add a sort key for sequential ordering
                row['sort_key'] = extract_number(row['QuestionID'])
                questions.append(row)
    except Exception as e:
        print(f"Error loading data: {e}")
    return questions

@app.route('/')
def index():
    data = load_data()
    years = sorted(list(set(q['Year'] for q in data if q['Year'])))
    
    # Organize topics by category: {Category: [Topic1, Topic2, ...]}
    categories_dict = {}
    for q in data:
        cat = q['Category']
        topic = q['Topic']
        if cat and topic:
            if cat not in categories_dict:
                categories_dict[cat] = set()
            categories_dict[cat].add(topic)
    
    # Sort categories and convert sets to sorted lists
    sorted_categories = {}
    for cat in sorted(categories_dict.keys()):
        sorted_categories[cat] = sorted(list(categories_dict[cat]))

    return render_template('index.html', years=years, categories=sorted_categories)

@app.route('/quiz')
def quiz():
    year = request.args.get('year')
    category = request.args.get('category')     # e.g., "民法"
    topic = request.args.get('topic')           # e.g., "地役権"
    q_index = int(request.args.get('index', 0)) # Current index in the filtered list
    
    data = load_data()
    filtered_questions = []
    
    # Filter Logic
    for q in data:
        if year and q['Year'] != year:
            continue
        if category and q['Category'] != category:
            continue
        if topic and q['Topic'] != topic:
            continue
        filtered_questions.append(q)
    
    if not filtered_questions:
        return "No questions found for this selection.", 404

    # Sort sequentially by QuestionID if a Year is selected (Feature 2)
    # If Category/Topic selected, sort as well for consistency.
    filtered_questions.sort(key=lambda x: x['sort_key'])

    # Handle index out of bounds (loop or stop) - let's stop/loop
    total_questions = len(filtered_questions)
    if q_index >= total_questions:
        q_index = 0 # Loop back to start or handle "Finish" screen
    
    question = filtered_questions[q_index]
    
    # Determine next index
    next_index = q_index + 1
    has_next = next_index < total_questions
    
    return render_template('quiz.html', 
                           question=question, 
                           index=q_index, 
                           total=total_questions,
                           year=year,
                           category=category,
                           topic=topic,
                           has_next=has_next)

@app.route('/next_question')
def next_question():
    # Redirect to quiz with incremented index and same filters
    year = request.args.get('year')
    category = request.args.get('category')
    topic = request.args.get('topic')
    current_index = int(request.args.get('index', 0))
    
    return redirect(url_for('quiz', year=year, category=category, topic=topic, index=current_index + 1))

    # Use PORT environment variable if available (Render uses this), otherwise default to 5000
    port = int(os.environ.get('PORT', 5000))
    # Debug mode should be False in production
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
