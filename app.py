from flask import Flask, render_template, request, jsonify, redirect, url_for
import requests
import json
from datetime import datetime
import os

app = Flask(__name__)

# Configuration
CLIENT_ID = 'JYL3LVURXHMERKNRTUR6GAVI2GCOKD7IJUDWG4YT'
CLIENT_SECRET = 'cGD22PuMvfIytbBoNI_3iZ1_60rbbwSb19PS7BmAnpQbux4yGtS6CMdppGIhGBaG6Jcd093m'
TOKEN_URL = 'https://app.workhub24.com/api/auth/token'
API_ENDPOINT = 'https://app.workhub24.com/api/workflows/XMFFQMFUEFUXL5UEC72I5XJZQB24ME56/w6890b2a840/cards'

# Global variables for token management
access_token = None
token_expiry = None

def get_access_token():
    """Obtain access token from the API"""
    global access_token, token_expiry
    
    try:
        response = requests.post(TOKEN_URL, 
                               headers={
                                   'Content-Type': 'application/json',
                                   'Accept': 'application/json'
                               },
                               json={
                                   'grant_type': 'client_credentials',
                                   'client_id': CLIENT_ID,
                                   'client_secret': CLIENT_SECRET
                               })
        
        if response.status_code == 200:
            data = response.json()
            access_token = data.get('token') or data.get('access_token')
            token_expiry = datetime.now().timestamp() + 3600  # Assume 1 hour expiry
            return access_token
        else:
            print(f"Token request failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"Error obtaining access token: {str(e)}")
        return None

def make_api_request(data):
    """Make API POST request with proper authentication"""
    token = get_access_token()
    if not token:
        raise Exception('Failed to obtain access token')
    
    try:
        response = requests.post(API_ENDPOINT,
                               headers={
                                   'Authorization': f'Bearer {token}',
                                   'Content-Type': 'application/json',
                                   'Accept': 'application/json'
                               },
                               json=data)
        
        print(f"API Response Status: {response.status_code}")
        if response.status_code in [200, 201]:
            result = response.json()
            print(f"API Response Data: {result}")
            return result
        else:
            error_text = response.text
            try:
                error_json = response.json()
                error_message = error_json.get('message') or error_json.get('error') or error_text
            except:
                error_message = error_text
            
            raise Exception(f"API request failed ({response.status_code}): {error_message}")
            
    except requests.exceptions.RequestException as e:
        raise Exception(f"Network error: {str(e)}")

@app.route('/')
def index():
    """Main page - QR generator"""
    return render_template('index.html')

@app.route('/equipment/<equipment_id>')
def equipment_actions(equipment_id):
    """Equipment actions page"""
    # Read optional context from URL params for display
    hospital = request.args.get('hospital', '')
    unit_code = request.args.get('unit_code', '')
    serial_number = request.args.get('serial_number', '')
    return render_template('equipment.html', 
                           equipment_id=equipment_id,
                           hospital=hospital,
                           unit_code=unit_code,
                           serial_number=serial_number)

@app.route('/api/action', methods=['POST'])
def handle_action():
    """Handle equipment actions via API"""
    try:
        data = request.get_json()
        action = data.get('action')
        equipment_id = data.get('equipment_id')
        
        if not action or not equipment_id:
            return jsonify({'error': 'Missing action or equipment_id'}), 400
        
        current_date = datetime.now().strftime('%Y-%m-%d')
        
        # Prepare API data based on action
        api_data = {
            'facilityID': equipment_id,
            'assigneeId':'QWOY3YPHWS5AV3SYYRTEHUFFYMPTNIE2QWOY3YPHWS5AV3SYYRTEHUFFYMPTNIE2',
            'reportedDate': current_date,
            'remarkByInitiator': f"{action.title()} request submitted via QR code scan",
            'locationID': equipment_id,
            'equipmentText': f"Equipment ID: {equipment_id}",
            'facilityText': f"{action.title()} for equipment {equipment_id}",
            'markAsCompleted': action == 'status'
        }
        
        if action == 'repair':
            api_data.update({
                'title': f'Repair Request - Equipment {equipment_id}',
                'issue': f'Repair request submitted for equipment {equipment_id}',
                'priorityLevel': 'High',
                'confirmedToIssueSpareparts': False
            })
        elif action == 'training':
            api_data.update({
                'title': f'Training Request - Equipment {equipment_id}',
                'issue': f'Training materials requested for equipment {equipment_id}',
                'priorityLevel': 'Medium'
            })
        elif action == 'maintenance':
            api_data.update({
                'title': f'Maintenance Request - Equipment {equipment_id}',
                'issue': f'Scheduled maintenance requested for equipment {equipment_id}',
                'priorityLevel': 'Medium',
                'numOfDays': 7
            })
        elif action == 'status':
            api_data.update({
                'title': f'Status Check - Equipment {equipment_id}',
                'issue': f'Status check requested for equipment {equipment_id}',
                'priorityLevel': 'Low'
            })
        else:
            return jsonify({'error': 'Invalid action'}), 400
        
        # Make API request
        result = make_api_request(api_data)
        
        return jsonify({
            'success': True,
            'message': f'{action.title()} request submitted successfully!',
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/generate_qr')
def generate_qr():
    """Generate QR code URL"""
    equipment_id = request.args.get('equipment_id')
    hospital = request.args.get('hospital', '')
    unit_code = request.args.get('unit_code', '')
    serial_number = request.args.get('serial_number', '')

    if not equipment_id:
        return jsonify({'error': 'Equipment ID required'}), 400
    if not hospital or not unit_code or not serial_number:
        return jsonify({'error': 'Hospital, Unit code, and Serial Number required'}), 400
    
    qr_url = url_for('equipment_actions', 
                     equipment_id=equipment_id, 
                     hospital=hospital,
                     unit_code=unit_code,
                     serial_number=serial_number,
                     _external=True)
    return jsonify({'qr_url': qr_url})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
