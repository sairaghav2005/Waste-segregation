from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from io import BytesIO
from PIL import Image

app = Flask(__name__)

# ✅ Allow all connections
CORS(app)

# =========================
# HEALTH CHECK
# =========================
@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "status": "success",
        "message": "Waste Segregation API is running"
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"})

# =========================
# MAIN UPLOAD ROUTE
# =========================
@app.route('/upload', methods=['POST'])
def upload():
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image uploaded"}), 400

        file = request.files['image']
        image_bytes = file.read()

        # validate image
        try:
            Image.open(BytesIO(image_bytes))
        except:
            return jsonify({"error": "Invalid image"}), 400

        # =========================
        # DEMO RESPONSE (SAFE)
        # =========================
        return jsonify({
            "category": "Recyclable",
            "prediction": "Plastic Bottle",
            "confidence": 92,
            "advice": "Rinse and recycle properly.",
            "dump_location": "Blue recycling bin"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    # Use the port assigned by Render, defaulting to 5000 for local testing
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Server starting on port {port}...")
    app.run(host='0.0.0.0', port=port)