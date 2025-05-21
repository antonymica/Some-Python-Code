from flask import Flask, render_template, request, jsonify, send_file
import random
import string
import io
import csv

app = Flask(__name__)

def generate_password(base_words, length=12, use_uppercase=True, use_numbers=True, use_special_chars=True):
    """Génère un mot de passe aléatoire incluant les mots de base"""
    # Traiter les mots de base
    processed_words = []
    for word in base_words:
        if word.strip():  # Ignorer les chaînes vides
            # Optionnel: appliquer une capitalisation aléatoire
            if use_uppercase and random.choice([True, False]):
                word = word.capitalize()
            processed_words.append(word)
    
    # Générer les parties aléatoires
    characters = string.ascii_lowercase
    if use_uppercase:
        characters += string.ascii_uppercase
    if use_numbers:
        characters += string.digits
    if use_special_chars:
        characters += "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    # Calculer la longueur restante après les mots de base
    base_length = sum(len(word) for word in processed_words)
    remaining_length = max(0, length - base_length)
    
    # Générer les caractères aléatoires
    random_part = ''.join(random.choice(characters) for _ in range(remaining_length))
    
    # Combiner les mots et les caractères aléatoires dans un ordre aléatoire
    all_parts = processed_words + [random_part]
    random.shuffle(all_parts)
    
    password = ''.join(all_parts)
    
    # Tronquer si nécessaire (au cas où les mots de base dépassent la longueur)
    return password[:length]

@app.route('/')
def index():
    """Route principale qui affiche le formulaire"""
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    """Route API pour générer les mots de passe"""
    try:
        data = request.json
        count = int(data.get('count', 5))
        length = int(data.get('length', 12))
        use_uppercase = data.get('uppercase', 'true') == 'true'
        use_numbers = data.get('numbers', 'true') == 'true'
        use_special_chars = data.get('special_chars', 'true') == 'true'
        base_words = [word.strip() for word in data.get('base_words', '').split(',') if word.strip()]
        
        passwords = [
            generate_password(base_words, length, use_uppercase, use_numbers, use_special_chars)
            for _ in range(count)
        ]
        
        return jsonify({'success': True, 'passwords': passwords})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/download', methods=['POST'])
def download():
    """Route pour télécharger les mots de passe en CSV"""
    try:
        data = request.json
        passwords = data.get('passwords', [])
        
        # Créer un fichier CSV en mémoire
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Index', 'Password'])
        for i, password in enumerate(passwords, 1):
            writer.writerow([i, password])
        
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name='wifi_passwords.csv'
        )
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)