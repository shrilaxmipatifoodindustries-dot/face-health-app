from flask import Flask, request, jsonify
from flask_cors import CORS
import os, uuid
from datetime import datetime

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "recordings"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/upload", methods=["POST"])
def upload_video():
    if "video" not in request.files:
        return jsonify({"error": "no video"}), 400

    user = request.form.get("user", "guest")
    file = request.files["video"]

    filename = f"{user}_{uuid.uuid4().hex}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.webm"
    path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(path)

    return jsonify({"saved": filename})

@app.route("/recordings")
def list_videos():
    return jsonify(os.listdir(UPLOAD_FOLDER))
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
