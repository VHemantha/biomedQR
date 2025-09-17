from flask import Flask, render_template, request, jsonify, redirect, url_for
import requests
import json
from datetime import datetime
import os

app = Flask(__name__)

# Configuration
CLIENT_ID = 'E7NKOOGKXQPXLF36KEEQPWPMQF5AHI2ZFUQAYBMT'
CLIENT_SECRET = 'i2HMGBswdoVL1Ta1r084XIU8ZrR9TBODtxIuFQcV2_fse5iuAfMF83VZHT-c6c_GiitngkEP'
TOKEN_URL = 'https://app.workhub24.com/api/auth/token'
API_ENDPOINT = 'https://app.workhub24.com/api/workflows/VTAQAOUPYELWDVZBIRVMEQHT6P7DKIB7/wd9e53c83d2/cards'
# Datatable endpoint to create records when generating QR
DATATABLE_ENDPOINT = 'https://app.workhub24.com/api/datatables/VTAQAOUPYELWDVZBIRVMEQHT6P7DKIB7/X4WRTFUICR7IWB6K7YG6OEZDDZGYEDYNYA6HQMUH/records'

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

def create_datatable_record(record_payload):
    """Create a datatable record using the token auth."""
    token = get_access_token()
    if not token:
        raise Exception('Failed to obtain access token')

    try:
        response = requests.post(
            DATATABLE_ENDPOINT,
            headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            json=record_payload
        )
        print(f"Datatable Response Status: {response.status_code}")
        if response.status_code in [200, 201]:
            print(f"Datatable Response Data: {response.json()}")
            return response.json()
        else:
            print(f"Datatable Error: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Datatable Network error: {str(e)}")
        return None

@app.route('/')
def index():
    """Main page - QR generator"""
    return render_template('index.html')

@app.route('/equipment/<item_id>')
def equipment_actions(item_id):
    """Equipment actions page"""
    # Read optional context from URL params for display
    hospital = request.args.get('hospital', '')
    unit_code = request.args.get('unit_code', '')
    serial_number = request.args.get('serial_number', '')
    supplier_name = request.args.get('supplier_name', '')
    unit = request.args.get('unit', '')
    return render_template('equipment.html', 
                           equipment_id=item_id,
                           hospital=hospital,
                           unit_code=unit_code,
                           serial_number=serial_number,
                           supplier_name=supplier_name,
                           unit=unit,
                           item_id=item_id)

@app.route('/api/action', methods=['POST'])
def handle_action():
    """Handle equipment actions via API"""
    try:
        data = request.get_json()
        action = data.get('action')
        equipment_id = data.get('equipment_id')  # This is now the item_id
        hospital = data.get('hospital') or ''
        unit_code = data.get('unit_code') or ''
        serial_number = data.get('serial_number') or ''
        supplier_name = data.get('supplier_name') or ''
        unit = data.get('unit') or ''
        item_id = data.get('item_id') or ''
        
        if not action or not equipment_id:
            return jsonify({'error': 'Missing action or equipment_id'}), 400
        
        current_date = datetime.now().strftime('%Y-%m-%d')
        
        # Map action identifiers to titles
        action_titles = {
            'repair': f'Repair Request - Item {equipment_id}',
            'user_training': f'User Training - Item {equipment_id}',
            'one_time_service': f'One Time Service Request - Item {equipment_id}',
            'consumer_request': f'Consumer Request - Item {equipment_id}'
        }

        if action not in action_titles:
            return jsonify({'error': 'Invalid action'}), 400

        # New API payload schema with requested mappings
        api_data = {
            'title': action_titles[action],
            'userName': 'QF7ZMKH4ECXD3PIMIFLILEZOKKLIRPOY',
            'currentDate': current_date,
            'productModel': unit_code,          # map unit code -> productModel
            'serialNumber': serial_number,      # map serial number -> serialNumber
            'productLocation': hospital,        # map hospital -> productLocation
            'hospitalName': hospital,           # also set hospital name if required
            'supplierName': supplier_name,      # add supplier name
            'unit': unit,                       # add unit
            'itemID': item_id,                  # add auto-generated item ID
            'contactPerson': None,
            'conactTel': None,
            'installationDate': None,
            'productType': None,
            'warrantyExpireDate': None,
            'supplierName': supplier_name,
            'unit1': unit
        }
        
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
    hospital = request.args.get('hospital', '')
    unit_code = request.args.get('unit_code', '')
    serial_number = request.args.get('serial_number', '')
    supplier_name = request.args.get('supplier_name', '')
    unit = request.args.get('unit', '')
    item_id = request.args.get('item_id', '')

    if not hospital or not unit_code or not serial_number or not supplier_name or not unit:
        return jsonify({'error': 'Hospital, Model, Serial Number, Supplier Name, and Unit required'}), 400
    
    # Create a datatable record using provided fields
    datatable_payload = {
        'itemID': item_id,
        'productLocation': hospital,   # hospital -> productLocation
        'productModel': unit_code,     # unit_code -> productModel
        'productType': '',             # no field provided; leaving empty
        'serialNumber': serial_number,
        'supplierName': supplier_name,
        'unit': unit  # serial_number -> serialNumber
    }

    try:
        create_datatable_record(datatable_payload)
    except Exception as e:
        # Log but do not block QR generation
        print(f"Failed to create datatable record: {str(e)}")

    qr_url = url_for('equipment_actions', 
                     item_id=item_id,
                     hospital=hospital,
                     unit_code=unit_code,
                     serial_number=serial_number,
                     supplier_name=supplier_name,
                     unit=unit,
                     _external=True)
    return jsonify({'qr_url': qr_url})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
