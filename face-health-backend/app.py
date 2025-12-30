from flask import Flask, request, send_from_directory, jsonify
from flask_cors import CORS
import os
import time
from datetime import datetime
import google.generativeai as genai

# --- CONFIGURATION ---
# ⚠️ YAHAN APNI KEY DAAL (Double quotes ke andar)
genai.configure(api_key="AIzaSyCUBXWRMFGeUUSfH4ZDYaDbZqHH8rT5WUI")

# Model Setup (Fixed Name: gemini-1.5-flash-001)
generation_config = {
  "temperature": 0.7,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

# Changed model name to specific version to fix 404 error
model = genai.GenerativeModel(
  model_name="gemini-1.5-flash-001", 
  generation_config=generation_config,
)

# --- FOLDER SETUP ---
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, '..', 'face-health-frontend')
FRONTEND_DIR = os.path.abspath(FRONTEND_DIR)
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')

app = Flask(__name__, static_folder=FRONTEND_DIR)
CORS(app)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 1. Main Website Route
@app.route('/')
def serve_index():
    return send_from_directory(FRONTEND_DIR, 'index.html')

# 2. Static Files (JS/CSS)
@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(FRONTEND_DIR, path)

# 3. Video Upload & AI Analysis Route
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'video' not in request.files:
        return jsonify({"status": "error", "message": "No video uploaded"}), 400
    
    file = request.files['video']
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"scan_{timestamp}.webm"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    
    # Step A: Save Video Locally
    file.save(filepath)
    print(f"✅ Video Saved locally: {filepath}")

    try:
        # Step B: Upload to Gemini Cloud
        print("🚀 Uploading to Gemini...")
        video_file = genai.upload_file(path=filepath)
        
        # Step C: Wait for processing
        while video_file.state.name == "PROCESSING":
            print("⏳ AI Processing video...")
            time.sleep(2)
            video_file = genai.get_file(video_file.name)

        if video_file.state.name == "FAILED":
            raise ValueError("Video processing failed in Gemini")

        # Step D: Generate Report
        print("🤖 Generating Skin Analysis...")
        prompt = """
        Analyze this video as a Dermatologist expert.
        1. Identify face health, skin texture, dark circles, and pigmentation.
        2. Give a 'Skin Health Score' out of 100.
        3. Suggest 3 quick remedies.
        Keep it concise, professional, and slightly futuristic style.
        Format the output clearly with HTML tags like <b> for bold.
        """
        
        response = model.generate_content([video_file, prompt])
        ai_report = response.text
        print("✅ Report Generated!")

        return jsonify({
            "status": "success", 
            "filename": filename,
            "ai_report": ai_report
        }), 200

    except Exception as e:
        print(f"❌ AI Error: {e}")
        return jsonify({
            "status": "success", 
            "filename": filename,
            "ai_report": f"AI System Offline. Error: {str(e)}\n(Check logs for model list)"
        }), 200

# 4. Secret Dashboard
@app.route('/dashboard')
def dashboard():
    if not os.path.exists(UPLOAD_FOLDER): return "No uploads yet"
    files = os.listdir(UPLOAD_FOLDER)
    
    html = """
    <body style='background:#0f172a;color:white;font-family:sans-serif;padding:20px'>
        <h1 style='color:#38bdf8'>🕵️‍♂️ Secret Recordings Dashboard</h1>
        <ul style='list-style:none;padding:0'>
    """
    for f in files:
        html += f"<li style='margin:10px 0;background:#1e293b;padding:10px;border-radius:8px;'><a href='/videos/{f}' target='_blank' style='color:#4ade80;text-decoration:none;font-size:18px'>🎥 Play: {f}</a></li>"
    html += "</ul></body>"
    return html

# 5. Serve Video Files
@app.route('/videos/<filename>')
def view_video(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)