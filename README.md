# Equipment QR System - Flask Application

## Overview
This Flask application provides a web-based Equipment QR Code system that allows users to:
- Generate QR codes for equipment
- Scan QR codes to access equipment action menus
- Submit repair, training, maintenance, and status requests

## Features
- **QR Code Generation**: Two methods (Online service and JavaScript library)
- **Equipment Actions**: Repair, Training, Maintenance, and Status requests
- **API Integration**: Connects to WorkHub24 API for request processing
- **Responsive Design**: Modern UI with gradient backgrounds and animations
- **Download Functionality**: Download generated QR codes

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Run the Flask application:
```bash
python app.py
```

3. Open your browser and navigate to:
```
http://localhost:5000
```

## Project Structure
```
BioMed/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── templates/            # HTML templates
│   ├── base.html         # Base template
│   ├── index.html        # QR generator page
│   └── equipment.html    # Equipment actions page
└── static/               # Static files
    ├── css/
    │   └── style.css     # Main stylesheet
    └── js/
        └── main.js       # Common JavaScript functions
```

## API Configuration
The application uses the following API credentials (configured in `app.py`):
- **Client ID**: JYL3LVURXHMERKNRTUR6GAVI2GCOKD7IJUDWG4YT
- **Client Secret**: cGD22PuMvfIytbBoNI_3iZ1_60rbbwSb19PS7BmAnpQbux4yGtS6CMdppGIhGBaG6Jcd093m
- **Token URL**: https://app.workhub24.com/api/auth/token
- **API Endpoint**: https://app.workhub24.com/api/workflows/XMFFQMFUEFUXL5UEC72I5XJZQB24ME56/w6890b2a840/cards

## Usage

### Generating QR Codes
1. Enter an equipment ID (e.g., EQP-001)
2. Choose QR generation method (Online or JS Library)
3. Click "Generate QR Code"
4. Download the QR code if needed

### Equipment Actions
When a QR code is scanned, users can:
- **Repair**: Submit repair requests (High priority)
- **Training**: Request training materials (Medium priority)
- **Maintenance**: Schedule maintenance (Medium priority)
- **Status**: Check equipment status (Low priority)

## Routes
- `/` - QR Code generator page
- `/equipment/<equipment_id>` - Equipment actions page
- `/api/action` - API endpoint for handling actions
- `/generate_qr` - Generate QR code URL

## Development
The application runs in debug mode by default. To run in production:
1. Set `debug=False` in `app.py`
2. Use a production WSGI server like Gunicorn
3. Configure proper environment variables for API credentials

## Dependencies
- Flask 2.3.3 - Web framework
- requests 2.31.0 - HTTP library for API calls
- Werkzeug 2.3.7 - WSGI toolkit
- Jinja2 3.1.2 - Template engine


HI