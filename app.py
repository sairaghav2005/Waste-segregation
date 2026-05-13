from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import boto3
import os
from io import BytesIO
from PIL import Image

app = Flask(__name__, static_folder='.')

# Enable CORS for Amplify frontend
CORS(app)

# -------------------------
# AWS CONFIG (Render Env Vars)
# -------------------------
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.environ.get('AWS_REGION', 'ap-south-1')

# Demo mode fallback
DEMO_MODE = not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY

# -------------------------
# AWS Rekognition Client
# -------------------------
if not DEMO_MODE:
    rekognition = boto3.client(
        'rekognition',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION
    )

# -------------------------
# CATEGORY MAPPING
# -------------------------
CATEGORY_MAPPING = {
    'recyclable': ['bottle', 'plastic', 'can', 'glass', 'paper', 'cardboard'],
    'organic': ['fruit', 'vegetable', 'food', 'banana', 'apple', 'leaf'],
    'hazardous': ['battery', 'chemical', 'paint', 'electronic', 'e-waste']
}

def detect_category(label):
    label = label.lower()

    for item in CATEGORY_MAPPING['hazardous']:
        if item in label:
            return "hazardous"

    for item in CATEGORY_MAPPING['organic']:
        if item in label:
            return "organic"

    for item in CATEGORY_MAPPING['recyclable']:
        if item in label:
            return "recyclable"

    return "unknown"

# -------------------------
# HOME ROUTE
# -------------------------
@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "message": "Waste Segregation API is running",
        "status": "success"
    })

# -------------------------
# HEALTH CHECK
# -------------------------
@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"})

# -------------------------
# PREDICT ROUTE (IMPORTANT)
# -------------------------
@app.route('/predict', methods=['POST'])
def predict():
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image provided"}), 400

        file = request.files['image']
        image_bytes = file.read()

        # Validate image
        try:
            Image.open(BytesIO(image_bytes))
        except:
            return jsonify({"error": "Invalid image"}), 400

        # -------------------------
        # DEMO MODE
        # -------------------------
        if DEMO_MODE:
            return jsonify({
                "category": "Recyclable",
                "prediction": "Plastic Bottle",
                "confidence": 92,
                "advice": "Rinse and recycle in blue bin.",
                "dump_location": "Recycling bin"
            })

        # -------------------------
        # AWS REKOGNITION MODE
        # -------------------------
        response = rekognition.detect_labels(
            Image={'Bytes': image_bytes},
            MaxLabels=5,
            MinConfidence=70
        )

        labels = response['Labels']

        if not labels:
            return jsonify({"error": "No objects detected"}), 400

        top_label = labels[0]['Name']
        confidence = int(labels[0]['Confidence'])

        category = detect_category(top_label)

        return jsonify({
            "category": category,
            "prediction": top_label,
            "confidence": confidence
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -------------------------
# RUN APP (LOCAL ONLY)
# -------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)