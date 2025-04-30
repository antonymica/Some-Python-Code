from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Set a secret key for session

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get the comma-separated items from the form
        items_input = request.form.get('items', '')
        
        # Split the input by commas and strip whitespace
        items = [item.strip() for item in items_input.split(',') if item.strip()]
        
        # Store items in session
        session['items'] = items
        
        return redirect(url_for('arrange'))
    
    return render_template('index.html')

@app.route('/arrange', methods=['GET', 'POST'])
def arrange():
    # Retrieve items from session
    items = session.get('items', [])
    
    if not items:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        # Get the reordered items from form
        new_order = request.form.getlist('items[]')
        session['items'] = new_order
        
        return redirect(url_for('result'))
    
    return render_template('arrange.html', items=items)

@app.route('/result')
def result():
    # Retrieve the arranged items from session
    arranged_items = session.get('items', [])
    
    if not arranged_items:
        return redirect(url_for('index'))
    
    return render_template('result.html', items=arranged_items)

@app.route('/update_order', methods=['POST'])
def update_order():
    new_order = request.json.get('items', [])
    session['items'] = new_order
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)