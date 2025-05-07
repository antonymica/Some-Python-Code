from flask import Flask, request, jsonify, render_template
import json
import os
from datetime import datetime

app = Flask(__name__)
DATA_FILE = "data/visitors.json"

# Chargement des visiteurs depuis le fichier
def load_visitors():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

# Sauvegarde des visiteurs
def save_visitors(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/collect", methods=["POST"])
def collect_data():
    data = request.json
    data["timestamp"] = datetime.now().isoformat()
    visitors = load_visitors()
    visitors.append(data)
    save_visitors(visitors)
    return jsonify({"status": "success"})

@app.route("/dashboard")
def dashboard():
    visitors = load_visitors()
    return render_template("dashboard.html", visitors=visitors, count=len(visitors))

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    app.run(debug=True)
