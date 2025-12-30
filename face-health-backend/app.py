from flask import Flask, request, send_from_directory, jsonify
from flask_cors import CORS
import os
from datetime import datetime

# Current Folder Path
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# Frontend Path (Sibling folder)
FRONTEND_DIR = os.path.join(BASE_DIR, '..', 'face-health-frontend')
FRONTEND_DIR = os.path.abspath(FRONTEND_DIR) # Make it absolute

UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')

app = Flask(__name__, static_folder=FRONTEND_DIR)
CORS(app)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def serve_index():
    # Check if file exists
    file_path = os.path.join(FRONTEND_DIR, 'index.html')
    
    if not os.path.exists(file_path):
        # DEBUG: Agar file nahi mili, toh batao kya dikh raha hai
        return jsonify({
            "Error": "index.html not found!",
            "Server is looking in": FRONTEND_DIR,
            "Files in Frontend Folder": os.listdir(FRONTEND_DIR) if os.path.exists(FRONTEND_DIR) else "Frontend folder not found!",
            "Current Backend Folder": BASE_DIR,
            "Files in Backend": os.listdir(BASE_DIR),
            "Root files (..)": os.listdir(os.path.join(BASE_DIR, '..'))
        })
    
    return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(FRONTEND_DIR, path)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'video' not in request.files:
        return jsonify({"status": "error", "message": "No video uploaded"}), 400
    file = request.files['video']
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"scan_{timestamp}.webm"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    return jsonify({"status": "success", "filename": filename}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)