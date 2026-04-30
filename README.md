# Waste Segregation AI

A modern web application that uses AWS Rekognition to analyze waste images and provide recycling advice.

## Features

- **Frontend**: Modern, responsive UI with drag-and-drop image upload
- **Backend**: Flask API with AWS Rekognition integration
- **AI Classification**: Detects waste categories (Recyclable, Organic, Hazardous)
- **Smart Advice**: Provides disposal instructions based on detected items

## Setup

### Prerequisites

- Python 3.8+
- AWS Account with Rekognition access
- AWS Access Key ID and Secret Access Key

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set AWS credentials as environment variables:
```bash
# Windows (PowerShell)
$env:AWS_ACCESS_KEY_ID="your-access-key"
$env:AWS_SECRET_ACCESS_KEY="your-secret-key"
$env:AWS_REGION="us-east-1"

# Linux/Mac
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_REGION="us-east-1"
```

Or replace the placeholder values in `app.py` (not recommended for production).

### Running the Backend

```bash
python app.py
```

The backend will start on `http://localhost:5000`

### Running the Frontend

Open `index.html` in a web browser, or serve it with a local server:
```bash
# Python 3
python -m http.server 8000

# Then open http://localhost:8000
```

## API Endpoints

### POST /upload
Upload an image for waste analysis.

**Request**: 
- Method: POST
- Content-Type: multipart/form-data
- Body: `image` (file)

**Response**:
```json
{
  "category": "Recyclable",
  "labels": ["Bottle", "Plastic"],
  "advice": "Rinse the item to remove food residue..."
}
```

### GET /health
Health check endpoint.

**Response**:
```json
{
  "status": "healthy"
}
```

## Category Detection Logic

The system classifies waste into three categories:

- **Recyclable** (Green): Bottles, plastic, cans, metal, glass, paper, cardboard
- **Organic** (Brown): Fruits, vegetables, food waste, plant material
- **Hazardous** (Red): Batteries, chemicals, paint, electronics, medical waste

## AWS Rekognition Setup

1. Go to AWS Console → Amazon Rekognition
2. Ensure your IAM user has `AmazonRekognitionFullAccess` or appropriate permissions
3. Get your Access Key ID and Secret Access Key from IAM → Security Credentials

## Project Structure

```
waste/
├── app.py              # Flask backend with AWS Rekognition
├── index.html          # Frontend UI
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Troubleshooting

**Error: "No labels detected in image"**
- Ensure the image is clear and well-lit
- Try with a different image

**Error: "Failed to analyze image"**
- Check AWS credentials are set correctly
- Verify your AWS account has Rekognition access
- Check the backend console for detailed error messages

**CORS errors**
- The backend includes CORS support via flask-cors
- Ensure both frontend and backend are running

## Demo Tips

For a college demo:
- Test with clear images of bottles, cans, fruits, or batteries
- The confidence percentage is mocked (85-99%) for visual effect
- The category detection uses keyword matching on AWS labels
