from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import boto3
import os
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

app = Flask(__name__, static_folder='.')

# Allow ALL origins so Amplify frontend can call this Render backend
# You can restrict to your Amplify URL e.g. origins=["https://main.xxxxx.amplifyapp.com"]
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=False)

# AWS Configuration
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID', '')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', '')
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')

# Demo mode - use mock data if AWS credentials are not set
DEMO_MODE = not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY or AWS_ACCESS_KEY_ID == 'your-access-key'

if not DEMO_MODE:
    # Initialize Rekognition client
    rekognition = boto3.client(
        'rekognition',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION
    )

# Category mapping based on detected labels
CATEGORY_MAPPING = {
    'recyclable': [
        'bottle', 'plastic', 'can', 'metal', 'glass', 'paper', 'cardboard',
        'box', 'container', 'jar', 'cup', 'carton', 'package', 'wrapping',
        'aluminum', 'tin', 'steel', 'PET', 'HDPE', 'recycle', 'recyclable'
    ],
    'organic': [
        'fruit', 'vegetable', 'food', 'apple', 'banana', 'orange', 'leaf',
        'plant', 'organic', 'compost', 'biodegradable', 'natural', 'wood',
        'bread', 'leftover', 'peel', 'skin', 'seed', 'nut', 'grain'
    ],
    'hazardous': [
        'battery', 'chemical', 'paint', 'oil', 'pesticide', 'medicine',
        'medical', 'syringe', 'needle', 'electronic', 'e-waste', 'bulb',
        'fluorescent', 'mercury', 'asbestos', 'radioactive', 'toxic',
        'corrosive', 'explosive', 'hazardous', 'dangerous'
    ]
}

ADVICE_MAPPING = {
    'recyclable': 'Rinse the item to remove food residue, remove caps if possible, and place in the recycling bin. Check local recycling guidelines for specific materials.',
    'organic': 'This item can be composted. Place it in a compost bin or green waste collection. Avoid composting meat, dairy, or oily foods in home compost.',
    'hazardous': '⚠️ WARNING: This item requires special disposal. Do not throw in regular trash. Take to a designated hazardous waste facility or contact local authorities for proper disposal instructions.',
    'unknown': 'Could not determine the waste category. Please check with your local waste management facility for proper disposal instructions.'
}


def detect_category(labels):
    """Determine waste category based on detected labels"""
    label_names = [label.lower() for label in labels]
    
    # Check for hazardous first (highest priority)
    for label in label_names:
        for hazardous_item in CATEGORY_MAPPING['hazardous']:
            if hazardous_item in label:
                return 'hazardous'
    
    # Check for organic
    for label in label_names:
        for organic_item in CATEGORY_MAPPING['organic']:
            if organic_item in label:
                return 'organic'
    
    # Check for recyclable
    for label in label_names:
        for recyclable_item in CATEGORY_MAPPING['recyclable']:
            if recyclable_item in label:
                return 'recyclable'
    
    return 'unknown'


@app.route('/upload', methods=['POST'])
def upload_image():
    try:
        # Check if file is present
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Read image
        image_bytes = file.read()
        
        # Validate image
        try:
            Image.open(BytesIO(image_bytes))
        except:
            return jsonify({'error': 'Invalid image file'}), 400
        
        # Demo mode - return mock data
        if DEMO_MODE:
            print("Running in DEMO MODE - returning mock data")
            # Mock responses for demo - single accurate prediction
            mock_responses = [
                {
                    'category': 'Recyclable',
                    'prediction': 'Plastic Bottle',
                    'confidence': 92,
                    'advice': 'Rinse the bottle with water to remove any residue. Remove the cap and label if possible. Place in the recycling bin marked for plastics. Ensure it\'s clean and dry before recycling.',
                    'dump_location': 'Blue recycling bin / Plastic recycling container'
                },
                {
                    'category': 'Recyclable',
                    'prediction': 'Glass Bottle',
                    'confidence': 89,
                    'advice': 'Rinse the glass bottle thoroughly. Remove any caps or corks. Place in the glass recycling bin. Separate by color if required by your local recycling program.',
                    'dump_location': 'Glass recycling bin / Bottle bank'
                },
                {
                    'category': 'Recyclable',
                    'prediction': 'Aluminum Can',
                    'confidence': 94,
                    'advice': 'Empty the can completely. Rinse if possible. Crush to save space. Place in the metal recycling bin. Aluminum is highly recyclable!',
                    'dump_location': 'Metal recycling bin / Can recycling point'
                },
                {
                    'category': 'Recyclable',
                    'prediction': 'Cardboard Box',
                    'confidence': 87,
                    'advice': 'Flatten the cardboard box to save space. Remove any tape or plastic packaging. Keep it dry. Place in the paper/cardboard recycling bin.',
                    'dump_location': 'Cardboard recycling bin / Paper recycling center'
                },
                {
                    'category': 'Recyclable',
                    'prediction': 'Paper',
                    'confidence': 91,
                    'advice': 'Ensure the paper is clean and dry. Remove any plastic windows or staples. Place in the paper recycling bin. Shredded paper may need special handling.',
                    'dump_location': 'Paper recycling bin / Document recycling'
                },
                {
                    'category': 'Organic',
                    'prediction': 'Tomato',
                    'confidence': 93,
                    'advice': 'This organic waste can be composted. Remove any stickers or packaging. Place in a compost bin or green waste collection. Great for garden compost!',
                    'dump_location': 'Compost bin / Green waste collection'
                },
                {
                    'category': 'Organic',
                    'prediction': 'Vegetable Waste',
                    'confidence': 88,
                    'advice': 'Vegetable peels and scraps are perfect for composting. Remove any non-organic packaging. Add to your compost pile or green waste bin.',
                    'dump_location': 'Compost bin / Green waste collection'
                },
                {
                    'category': 'Organic',
                    'prediction': 'Fruit',
                    'confidence': 90,
                    'advice': 'Fruit peels and cores can be composted. Remove stickers and packaging. Place in compost bin or green waste collection.',
                    'dump_location': 'Compost bin / Green waste collection'
                },
                {
                    'category': 'Organic',
                    'prediction': 'Banana Peel',
                    'confidence': 95,
                    'advice': 'Banana peels are excellent for composting. They add potassium to your compost. Place in compost bin or green waste collection.',
                    'dump_location': 'Compost bin / Green waste collection'
                },
                {
                    'category': 'Organic',
                    'prediction': 'Apple Core',
                    'confidence': 91,
                    'advice': 'Apple cores biodegrade quickly. Compost them in your bin or green waste collection. Remove any stickers first.',
                    'dump_location': 'Compost bin / Green waste collection'
                },
                {
                    'category': 'Organic',
                    'prediction': 'Food Scraps',
                    'confidence': 86,
                    'advice': 'Food scraps can be composted. Avoid meat, dairy, and oily foods in home compost. Use green waste collection for these items.',
                    'dump_location': 'Compost bin / Green waste collection'
                },
                {
                    'category': 'Organic',
                    'prediction': 'Leaf',
                    'confidence': 89,
                    'advice': 'Leaves are great for composting. They provide carbon to balance nitrogen-rich materials. Add to compost bin or green waste collection.',
                    'dump_location': 'Compost bin / Green waste collection'
                },
                {
                    'category': 'Hazardous',
                    'prediction': 'Battery',
                    'confidence': 95,
                    'advice': '⚠️ WARNING: Batteries contain toxic materials. Do NOT throw in regular trash. Store in a non-conductive container. Take to a designated battery recycling point or hazardous waste facility.',
                    'dump_location': 'Hazardous waste facility / Battery recycling point'
                },
                {
                    'category': 'Hazardous',
                    'prediction': 'Electronic Waste',
                    'confidence': 92,
                    'advice': '⚠️ WARNING: E-waste contains heavy metals. Do not throw in regular trash. Take to an e-waste recycling center or electronic store with recycling program.',
                    'dump_location': 'E-waste recycling center / Electronic store'
                },
                {
                    'category': 'Hazardous',
                    'prediction': 'Paint Can',
                    'confidence': 88,
                    'advice': '⚠️ WARNING: Paint is hazardous. Do not pour down drains or throw in trash. Take to a hazardous waste facility or paint recycling program.',
                    'dump_location': 'Hazardous waste facility / Paint recycling center'
                },
                {
                    'category': 'Hazardous',
                    'prediction': 'Light Bulb',
                    'confidence': 90,
                    'advice': '⚠️ WARNING: CFL and fluorescent bulbs contain mercury. Handle carefully. Do not throw in regular trash. Take to a hazardous waste facility.',
                    'dump_location': 'Hazardous waste facility / Light bulb recycling'
                }
            ]
            # Return random mock response
            import random
            return jsonify(random.choice(mock_responses))
        
        # Call AWS Rekognition
        print("🔍 Calling AWS Rekognition...")
        response = rekognition.detect_labels(
            Image={'Bytes': image_bytes},
            MaxLabels=10,
            MinConfidence=50
        )

        # Extract labels with confidence
        labels_data = response['Labels']
        print(f"📊 AWS Rekognition detected {len(labels_data)} labels:")
        for label in labels_data:
            print(f"  - {label['Name']}: {label['Confidence']:.1f}%")

        # If no labels detected, return error
        if not labels_data:
            return jsonify({'error': 'No labels detected in image'}), 400

        # Get the highest confidence label as the single prediction
        top_label = max(labels_data, key=lambda x: x['Confidence'])
        prediction = top_label['Name']
        confidence = int(top_label['Confidence'])
        print(f"✅ Top prediction: {prediction} ({confidence}%)")

        # Determine category based on top label
        category = detect_category([prediction])
        print(f"📦 Category: {category}")
        
        # Get advice and dump location
        advice = ADVICE_MAPPING.get(category, ADVICE_MAPPING['unknown'])
        
        # Add dump location based on category
        dump_locations = {
            'recyclable': 'Blue recycling bin / Local recycling center',
            'organic': 'Compost bin / Green waste collection',
            'hazardous': 'Hazardous waste facility / Special collection point',
            'unknown': 'Contact local waste management for guidance'
        }
        dump_location = dump_locations.get(category, dump_locations['unknown'])
        
        # Return response with single prediction
        return jsonify({
            'category': category.capitalize(),
            'prediction': prediction,
            'confidence': confidence,
            'advice': advice,
            'dump_location': dump_location
        })
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': f'Failed to analyze image: {str(e)}'}), 500


@app.route('/', methods=['GET'])
def index():
    return send_from_directory('.', 'index.html')

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})


if __name__ == '__main__':
    print("Starting Waste Segregation AI Backend...")
    print(f"DEMO_MODE: {DEMO_MODE}")
    print(f"AWS_ACCESS_KEY_ID set: {bool(AWS_ACCESS_KEY_ID)}")
    print(f"AWS_SECRET_ACCESS_KEY set: {bool(AWS_SECRET_ACCESS_KEY)}")
    print(f"AWS_REGION: {AWS_REGION}")
    if DEMO_MODE:
        print("⚠️ Running in DEMO MODE - using mock data")
        print("To use AWS Rekognition, set AWS credentials as environment variables:")
        print("  $env:AWS_ACCESS_KEY_ID='your-key'")
        print("  $env:AWS_SECRET_ACCESS_KEY='your-secret'")
        print("  $env:AWS_REGION='ap-south-1'")
    else:
        print("✅ Using AWS Rekognition for real image analysis")
    app.run(debug=True, host='0.0.0.0', port=5000)
