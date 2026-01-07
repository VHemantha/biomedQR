from flask import Flask, render_template, request, jsonify, redirect, url_for
import requests
import json
from datetime import datetime
import os

app = Flask(__name__)

# Configuration
CLIENT_ID = 'WHL5UBGONVTWJAKCBYUC3WKF3KK2AYTLJYPVBDHP'
CLIENT_SECRET = 'EY8qYHICL8M7Qc690nFcohD5IRD-sjt9CGUng68OMpzHz4ru5xkpiVIL5ITK3jCHET7bqiZG'
TOKEN_URL = 'https://app.workhub24.com/api/auth/token'
API_ENDPOINT = 'https://app.workhub24.com/api/workflows/VTAQAOUPYELWDVZBIRVMEQHT6P7DKIB7/wd9e53c83d2/cards'
CONS_API_ENDPOINT ='https://app.workhub24.com/api/workflows/VTAQAOUPYELWDVZBIRVMEQHT6P7DKIB7/w7a45294262/cards'
USER_TRN_API_ENDPOINT = 'https://app.workhub24.com/api/workflows/VTAQAOUPYELWDVZBIRVMEQHT6P7DKIB7/w938b656364/cards'
OTS_API_ENDPOINT ='https://app.workhub24.com/api/workflows/VTAQAOUPYELWDVZBIRVMEQHT6P7DKIB7/wb9cbe5aa42/cards'
REPAIR_API_ENDPOINT = 'https://app.workhub24.com/api/workflows/VTAQAOUPYELWDVZBIRVMEQHT6P7DKIB7/wa97c783b94/cards'
# Datatable endpoints for GET requests (fetching data)
DATATABLE_ENDPOINT = 'https://app.workhub24.com/api/datatables/VTAQAOUPYELWDVZBIRVMEQHT6P7DKIB7/X4WRTFUICR7IWB6K7YG6OEZDDZGYEDYNYA6HQMUH/records'
CONS_DATATABLE_ENDPOINT = 'https://app.workhub24.com/api/datatables/VTAQAOUPYELWDVZBIRVMEQHT6P7DKIB7/P66XQNQVY7NCVN2YE3YLEXYRKN5IU7NP3VBPWUUD/records'
OTS_DATATABLE_ENDPOINT = 'https://app.workhub24.com/api/datatables/VTAQAOUPYELWDVZBIRVMEQHT6P7DKIB7/LNDO6RVKEA4XV5WU2ULJZVDELKNFOPNPWGRTYLLF/records'
USER_TRN_DATATABLE_ENDPOINT = 'https://app.workhub24.com/api/datatables/VTAQAOUPYELWDVZBIRVMEQHT6P7DKIB7/W77VKUNWCN5EF4TX5LQEUBZHVOW4NO65DFNXBLAL/records'
REPAIR_DATATABLE_ENDPOINT = 'https://app.workhub24.com/api/datatables/VTAQAOUPYELWDVZBIRVMEQHT6P7DKIB7/UNKCZOGOASTYG74CQJCNSZ5RUE5ZDC2II34Y77DO/records'
# PUT request endpoints for updating ratings (one endpoint per activity type)
# Note: These endpoints should match the corresponding datatable for each activity type
DEFAULT_PUT_ENDPOINT = 'https://app.workhub24.com/api/datatables/VTAQAOUPYELWDVZBIRVMEQHT6P7DKIB7/X4WRTFUICR7IWB6K7YG6OEZDDZGYEDYNYA6HQMUH/records'
CONSUMABLE_PUT_ENDPOINT = 'https://app.workhub24.com/api/datatables/VTAQAOUPYELWDVZBIRVMEQHT6P7DKIB7/P66XQNQVY7NCVN2YE3YLEXYRKN5IU7NP3VBPWUUD/records'
USER_TRAINING_PUT_ENDPOINT = 'https://app.workhub24.com/api/datatables/VTAQAOUPYELWDVZBIRVMEQHT6P7DKIB7/W77VKUNWCN5EF4TX5LQEUBZHVOW4NO65DFNXBLAL/records'
OTS_PUT_ENDPOINT = 'https://app.workhub24.com/api/datatables/VTAQAOUPYELWDVZBIRVMEQHT6P7DKIB7/LNDO6RVKEA4XV5WU2ULJZVDELKNFOPNPWGRTYLLF/records'
REPAIR_PUT_ENDPOINT = 'https://app.workhub24.com/api/datatables/VTAQAOUPYELWDVZBIRVMEQHT6P7DKIB7/UNKCZOGOASTYG74CQJCNSZ5RUE5ZDC2II34Y77DO/records'

# Activity type to PUT endpoint mapping
ACTIVITY_PUT_ENDPOINT_MAP = {
    'Consumable Request': CONSUMABLE_PUT_ENDPOINT,
    'User Training': USER_TRAINING_PUT_ENDPOINT,
    'User Training Request': USER_TRAINING_PUT_ENDPOINT,
    'One Time Service': OTS_PUT_ENDPOINT,
    'One Time Service Request': OTS_PUT_ENDPOINT,
    'Repair': REPAIR_PUT_ENDPOINT,
    'Repair Request': REPAIR_PUT_ENDPOINT,
    'Repair Process Request': REPAIR_PUT_ENDPOINT,
    # Default fallback
    'default': DEFAULT_PUT_ENDPOINT
}
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
            print(f"Access token obtained successfully{response}")
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


def make_api_request_consumable(data):
    """Make API POST request with proper authentication for consumable requests"""
    token = get_access_token()
    if not token:
        raise Exception('Failed to obtain access token')

    print(f"🔑 Using token: {token[:20]}...")

    try:
        response = requests.post(CONS_API_ENDPOINT,
                               headers={
                                   'Authorization': f'Bearer {token}',
                                   'Content-Type': 'application/json',
                                   'Accept': 'application/json',
                                   'User-Agent' : 'Mozilla/5.0 (Linux; Android 16; Pixel 9) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.12.45 Mobile Safari/537.36'
                               },
                               json=data)

        print(f"📥 Consumable API Response Status: {response.status_code}")
        print(f"📥 Response Headers: {dict(response.headers)}")
        print(f"📥 Response Body: {response.text}")

        if response.status_code in [200, 201]:
            result = response.json()
            print(f"✅ API Response Data: {result}")
            return result
        else:
            error_text = response.text
            try:
                error_json = response.json()
                error_message = error_json.get('message') or error_json.get('error') or error_text
            except:
                error_message = error_text

            print(f"❌ API Error: {error_message}")
            raise Exception(f"API request failed ({response.status_code}): {error_message}")

    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {str(e)}")
        raise Exception(f"Network error: {str(e)}")


def make_api_request_userTraining(data):
    """Make API POST request with proper authentication for consumable requests"""
    token = get_access_token()
    if not token:
        raise Exception('Failed to obtain access token')

    print(f"🔑 Using token: {token[:20]}...")

    try:
        response = requests.post(USER_TRN_API_ENDPOINT,
                               headers={
                                   'Authorization': f'Bearer {token}',
                                   'Content-Type': 'application/json',
                                   'Accept': 'application/json',
                                   'User-Agent' : 'Mozilla/5.0 (Linux; Android 16; Pixel 9) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.12.45 Mobile Safari/537.36'
                               },
                               json=data)

        print(f"📥 Consumable API Response Status: {response.status_code}")
        print(f"📥 Response Headers: {dict(response.headers)}")
        print(f"📥 Response Body: {response.text}")

        if response.status_code in [200, 201]:
            result = response.json()
            print(f"✅ API Response Data: {result}")
            return result
        else:
            error_text = response.text
            try:
                error_json = response.json()
                error_message = error_json.get('message') or error_json.get('error') or error_text
            except:
                error_message = error_text

            print(f"❌ API Error: {error_message}")
            raise Exception(f"API request failed ({response.status_code}): {error_message}")

    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {str(e)}")
        raise Exception(f"Network error: {str(e)}")


def make_api_request_repair(data):
    """Make API POST request with proper authentication for consumable requests"""
    token = get_access_token()
    if not token:
        raise Exception('Failed to obtain access token')

    print(f"🔑 Using token: {token[:20]}...")

    try:
        response = requests.post(REPAIR_API_ENDPOINT,
                               headers={
                                   'Authorization': f'Bearer {token}',
                                   'Content-Type': 'application/json',
                                   'Accept': 'application/json',
                                   'User-Agent' : 'Mozilla/5.0 (Linux; Android 16; Pixel 9) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.12.45 Mobile Safari/537.36'
                               },
                               json=data)

        print(f"📥 Consumable API Response Status: {response.status_code}")
        print(f"📥 Response Headers: {dict(response.headers)}")
        print(f"📥 Response Body: {response.text}")

        if response.status_code in [200, 201]:
            result = response.json()
            print(f"✅ API Response Data: {result}")
            return result
        else:
            error_text = response.text
            try:
                error_json = response.json()
                error_message = error_json.get('message') or error_json.get('error') or error_text
            except:
                error_message = error_text

            print(f"❌ API Error: {error_message}")
            raise Exception(f"API request failed ({response.status_code}): {error_message}")

    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {str(e)}")
        raise Exception(f"Network error: {str(e)}")


def make_api_request_ots(data):
    """Make API POST request with proper authentication for consumable requests"""
    token = get_access_token()
    if not token:
        raise Exception('Failed to obtain access token')

    print(f"🔑 Using token: {token[:20]}...")

    try:
        response = requests.post(OTS_API_ENDPOINT,
                               headers={
                                   'Authorization': f'Bearer {token}',
                                   'Content-Type': 'application/json',
                                   'Accept': 'application/json',
                                   'User-Agent' : 'Mozilla/5.0 (Linux; Android 16; Pixel 9) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.12.45 Mobile Safari/537.36'
                               },
                               json=data)

        print(f"📥 Consumable API Response Status: {response.status_code}")
        print(f"📥 Response Headers: {dict(response.headers)}")
        print(f"📥 Response Body: {response.text}")

        if response.status_code in [200, 201]:
            result = response.json()
            print(f"✅ API Response Data: {result}")
            return result
        else:
            error_text = response.text
            try:
                error_json = response.json()
                error_message = error_json.get('message') or error_json.get('error') or error_text
            except:
                error_message = error_text

            print(f"❌ API Error: {error_message}")
            raise Exception(f"API request failed ({response.status_code}): {error_message}")

    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {str(e)}")
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
    productModel = request.args.get('productModel', '')
    return render_template('equipment.html', 
                           equipment_id=item_id,
                           hospital=hospital,
                           unit_code=unit_code,
                           serial_number=serial_number,
                           supplier_name=supplier_name,
                           unit=unit,
                           item_id=item_id,
                           productModel=productModel
                           )

@app.route('/api/action', methods=['POST'])
def handle_action():
    """Handle equipment actions via API"""
    try:
        data = request.get_json()
        action = data.get('action')
        equipment_id = data.get('equipment_id')
        area = data.get('area') or ''
        location = data.get('location') or ''
        hospital = data.get('hospital') or ''
        unit_code = data.get('unit_code') or ''
        serial_number = data.get('serial_number') or ''
        supplier_name = data.get('supplier_name') or ''
        unit = data.get('unit') or ''
        item_id = data.get('item_id') or ''
        contact_number = data.get('contact_number') or ''
        
        if not action or not equipment_id:
            return jsonify({'error': 'Missing action or equipment_id'}), 400
        
        if not contact_number:
            return jsonify({'error': 'Contact number is required'}), 400
        
        current_date = datetime.now().strftime('%Y-%m-%d')
        
        action_titles = {
            'repair': f'Repair Request - Item {equipment_id}',
            'user_training': f'User Training - Item {equipment_id}',
            'one_time_service': f'One Time Service Request - Item {equipment_id}',
            'consumer_request': f'Consumer Request - Item {equipment_id}',
            'consumable_request': f'Consumable Request - Item {equipment_id}'
        }

        if action not in action_titles:
            return jsonify({'error': 'Invalid action'}), 400
        
        userID = 'QF7ZMKH4ECXD3PIMIFLILEZOKKLIRPOY'
        
        # API payload with ALL fields including area and location
        api_data = {
            'title': action_titles[action],
            'userName': userID,
            'currentDate': current_date,
            'area': area,
            'location': location,
            'productModel': unit_code,
            'serialNumber': serial_number,
            'productLocation': hospital,
            'hospital': hospital,
            'requestType': action.replace('_', ' ').title(),
            'supplierName': supplier_name,
            'unit': unit,
            'itemID': item_id,
            'contactPerson': None,
            'conactTel': contact_number,
            'installationDate': None,
            'productType': None,
            'warrantyExpireDate': None,
            'unit1': unit,
            'requestDateTime': datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')
        }
        
        print(f"📤 Sending to API: {json.dumps(api_data, indent=2)}")

        # Route consumable requests to the consumable endpoint
        if action == 'consumable_request':
            print(f"🔄 Routing to CONSUMABLE endpoint: {CONS_API_ENDPOINT}")
            result = make_api_request(api_data)
        else:
            result = make_api_request(api_data)

        return jsonify({
            'success': True,
            'message': f'{action.replace("_", " ").title()} request submitted successfully!',
            'data': result
        })

    except Exception as e:
        print(f"❌ Action failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

    # CONSUMABLE REQUEST HANDLER
@app.route('/api/CR', methods=['POST'])
def handle_consumable_request():
    """Handle consumable request via API"""
    try:
        # Get and validate request data
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data received'
            }), 400

        # Extract all fields with proper validation
        action = data.get('action', 'consumable_request')
        equipment_id = data.get('equipment_id', '').strip()
        area = data.get('area', '').strip()
        location = data.get('location', '').strip()
        hospital = data.get('hospital', '').strip()
        unit_code = data.get('unit_code', '').strip()
        serial_number = data.get('serial_number', '').strip()
        supplier_name = data.get('supplier_name', '').strip()
        unit = data.get('unit', '').strip()
        item_id = data.get('item_id', '').strip()
        contact_number = data.get('contact_number', '').strip()

        # Validation
        if not equipment_id:
            return jsonify({
                'success': False,
                'error': 'equipment_id is required'
            }), 400

        if not contact_number:
            return jsonify({
                'success': False,
                'error': 'Contact number is required'
            }), 400

        # Validate contact number format
        if not contact_number or len(contact_number) < 7:
            return jsonify({
                'success': False,
                'error': 'Please provide a valid contact number (minimum 7 digits)'
            }), 400

        print('=' * 60)
        print('🔵 CONSUMABLE REQUEST HANDLER')
        print('=' * 60)
        print(f"Equipment ID: {equipment_id}")
        print(f"Item ID: {item_id}")
        print(f"Contact: {contact_number}")
        print(f"Hospital: {hospital}")
        print(f"Area: {area}")
        print(f"Location: {location}")
        print('=' * 60)

        current_date = datetime.now().strftime('%Y-%m-%d')
        action_title = f"Consumable Request - {item_id}"
        request_type = 'Consumable Request'
        userID = 'EDQETBXHJTRBOFEXNT3JXAIVAU3BP2KB'

        # API payload for consumable request - matching all fields from handle_action
        api_data = {
            'title': action_title,
            'itemID': item_id,
            'area': area,
            'requestDateTime': datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f'),
            'requestType' : request_type,
            'location': location,
            'hospital': hospital,
            'serialNumber': serial_number,
            'productModel': supplier_name,
            'conactNumber': contact_number
            
        }

        print(f"📤 Sending Consumable Request to API:")
        print(json.dumps(api_data, indent=2))
        print(f"📤 Endpoint: {CONS_API_ENDPOINT}")
        print('=' * 60)

        # Make API call
        result = make_api_request_consumable(api_data)

        print('✅ Consumable request submitted successfully')
        print('=' * 60)

        return jsonify({
            'success': True,
            'message': 'Consumable Request submitted successfully!',
            'data': result
        }), 200

    except Exception as e:
        print('=' * 60)
        print(f"❌ Consumable Request Failed: {str(e)}")
        import traceback
        traceback.print_exc()
        print('=' * 60)

        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
         
    
    
    
@app.route('/api/UserTraining', methods=['POST'])
def handle_userT_request():
    """Handle userT request via API"""
    try:
        # Get and validate request data
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data received'
            }), 400

        # Extract all fields with proper validation
        action = data.get('action', 'consumable_request')
        equipment_id = data.get('equipment_id', '').strip()
        area = data.get('area', '').strip()
        location = data.get('location', '').strip()
        hospital = data.get('hospital', '').strip()
        unit_code = data.get('unit_code', '').strip()
        serial_number = data.get('serial_number', '').strip()
        supplier_name = data.get('supplier_name', '').strip()
        unit = data.get('unit', '').strip()
        item_id = data.get('item_id', '').strip()
        contact_number = data.get('contact_number', '').strip()
        product_model = data.get('product_model', '').strip()

        # Validation
        if not equipment_id:
            return jsonify({
                'success': False,
                'error': 'equipment_id is required'
            }), 400

        if not contact_number:
            return jsonify({
                'success': False,
                'error': 'Contact number is required'
            }), 400

        # Validate contact number format
        if not contact_number or len(contact_number) < 7:
            return jsonify({
                'success': False,
                'error': 'Please provide a valid contact number (minimum 7 digits)'
            }), 400

        print('=' * 60)
        print('🔵 USER TRAINING REQUEST HANDLER')
        print('=' * 60)
        print(f"Equipment ID: {equipment_id}")
        print(f"Item ID: {item_id}")
        print(f"Contact: {contact_number}")
        print(f"Hospital: {hospital}")
        print(f"Area: {area}")
        print(f"Location: {location}")
        print(f"Product Model: {product_model}")
        print('=' * 60)

        current_date = datetime.now().strftime('%Y-%m-%d')
        action_title = f"User Training Request - {item_id}"
        request_type = 'User Training Request'
        userID = 'EDQETBXHJTRBOFEXNT3JXAIVAU3BP2KB'

        # API payload for user training request
        api_data = {
            'title': action_title,
            'itemID': item_id,
            'requestType': request_type,
            'area': area,
            'requestDateTime': datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f'),
            'location': location,
            'hospitalDepartment': hospital,
            'modality': product_model,
            'prodcutSerielNumber': serial_number,
            'productModel': product_model,
            'requesterMobile': contact_number

        }

        print(f"📤 Sending User Training Request to API:")
        print(json.dumps(api_data, indent=2))
        print(f"📤 Endpoint: {USER_TRN_API_ENDPOINT}")
        print('=' * 60)

        # Make API call
        result = make_api_request_userTraining(api_data)

        print('✅ User Training request submitted successfully')
        print('=' * 60)

        return jsonify({
            'success': True,
            'message': 'User Training Request submitted successfully!',
            'data': result
        }), 200

    except Exception as e:
        print('=' * 60)
        print(f"❌ User Training Request Failed: {str(e)}")
        import traceback
        traceback.print_exc()
        print('=' * 60)

        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/OTS', methods=['POST'])
def handle_ots_request():
    """Handle userT request via API"""
    try:
        # Get and validate request data
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data received'
            }), 400

        # Extract all fields with proper validation
        action = data.get('action', 'ots')
        equipment_id = data.get('equipment_id', '').strip()
        area = data.get('area', '').strip()
        location = data.get('location', '').strip()
        hospital = data.get('hospital', '').strip()
        unit_code = data.get('unit_code', '').strip()
        serial_number = data.get('serial_number', '').strip()
        supplier_name = data.get('supplier_name', '').strip()
        unit = data.get('unit', '').strip()
        item_id = data.get('item_id', '').strip()
        contact_number = data.get('contact_number', '').strip()
        product_model = data.get('product_model', '').strip()

        # Validation
        if not equipment_id:
            return jsonify({
                'success': False,
                'error': 'equipment_id is required'
            }), 400

        if not contact_number:
            return jsonify({
                'success': False,
                'error': 'Contact number is required'
            }), 400

        # Validate contact number format
        if not contact_number or len(contact_number) < 7:
            return jsonify({
                'success': False,
                'error': 'Please provide a valid contact number (minimum 7 digits)'
            }), 400

        print('=' * 60)
        print('🔵 OTS REQUEST HANDLER')
        print('=' * 60)
        print(f"Equipment ID: {equipment_id}")
        print(f"Item ID: {item_id}")
        print(f"Contact: {contact_number}")
        print(f"Hospital: {hospital}")
        print(f"Area: {area}")
        print(f"Location: {location}")
        print(f"Product Model: {product_model}")
        print('=' * 60)

        current_date = datetime.now().strftime('%Y-%m-%d')
        action_title = f"One Time Service Request - {item_id}"
        request_type = "One Time Service Request"
        userID = 'EDQETBXHJTRBOFEXNT3JXAIVAU3BP2KB'

        # API payload for user training request
        api_data = {
            'title': action_title,
            'iTEMID': item_id,
            'requestType': request_type,
            'area': area,
            'requestDateTime': datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f'),
            'location': location,
            'hospital': hospital,
            'modality': product_model,
            'serialNumber1': serial_number,
            'productModel': product_model,
            'conactNumber': contact_number

        }

        print(f"📤 Sending User Training Request to API:")
        print(json.dumps(api_data, indent=2))
        print(f"📤 Endpoint: {USER_TRN_API_ENDPOINT}")
        print('=' * 60)

        # Make API call
        result = make_api_request_ots(api_data)

        print('✅ One Time Service request submitted successfully')
        print('=' * 60)

        return jsonify({
            'success': True,
            'message': 'One Time Service Request submitted successfully!',
            'data': result
        }), 200

    except Exception as e:
        print('=' * 60)
        print(f"❌ User Training Request Failed: {str(e)}")
        import traceback
        traceback.print_exc()
        print('=' * 60)

        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/repair', methods=['POST'])
def handle_repair_request():
    """Handle repair request via API"""
    try:
        # Get and validate request data
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data received'
            }), 400

        # Extract all fields with proper validation
        action = data.get('action', 'repair')
        equipment_id = data.get('equipment_id', '').strip()
        area = data.get('area', '').strip()
        location = data.get('location', '').strip()
        hospital = data.get('hospital', '').strip()
        unit_code = data.get('unit_code', '').strip()
        serial_number = data.get('serial_number', '').strip()
        supplier_name = data.get('supplier_name', '').strip()
        unit = data.get('unit', '').strip()
        item_id = data.get('item_id', '').strip()
        contact_number = data.get('contact_number', '').strip()
        product_model = data.get('product_model', '').strip()

        # Validation
        if not equipment_id:
            return jsonify({
                'success': False,
                'error': 'equipment_id is required'
            }), 400

        if not contact_number:
            return jsonify({
                'success': False,
                'error': 'Contact number is required'
            }), 400

        # Validate contact number format
        if not contact_number or len(contact_number) < 7:
            return jsonify({
                'success': False,
                'error': 'Please provide a valid contact number (minimum 7 digits)'
            }), 400

        print('=' * 60)
        print('🔵 Repair REQUEST HANDLER')
        print('=' * 60)
        print(f"Equipment ID: {equipment_id}")
        print(f"Item ID: {item_id}")
        print(f"Contact: {contact_number}")
        print(f"Hospital: {hospital}")
        print(f"Area: {area}")
        print(f"Location: {location}")
        print(f"Product Model: {product_model}")
        print('=' * 60)

        current_date = datetime.now().strftime('%Y-%m-%d')
        action_title = f"Repair Process Request - {item_id}"
        request_type = "Repair Process Request"
        userID = 'EDQETBXHJTRBOFEXNT3JXAIVAU3BP2KB'

        # API payload for user training request
        api_data = {
            'title': action_title,
            'itemID': item_id,
            'requestType': request_type,
            'requestDateAndTime': datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f'),
            'location': location,
            'hospital': hospital,
            'productModel': product_model,
            'serialNumber': serial_number,
            'productModel': product_model,
            'unit': unit,
            'contactNumber': contact_number

        }

        print(f"📤 Sending User Training Request to API:")
        print(json.dumps(api_data, indent=2))
        print(f"📤 Endpoint: {USER_TRN_API_ENDPOINT}")
        print('=' * 60)

        # Make API call
        result = make_api_request_repair(api_data)

        print('✅ Repair request submitted successfully')
        print('=' * 60)

        return jsonify({
            'success': True,
            'message': 'Repair Request submitted successfully!',
            'data': result
        }), 200

    except Exception as e:
        print('=' * 60)
        print(f"❌ Repair Request Failed: {str(e)}")
        import traceback
        traceback.print_exc()
        print('=' * 60)

        return jsonify({
            'success': False,
            'error': str(e)
        }), 500




@app.route('/api/get_master_data/<item_id>/<flow>', methods=['GET'])
def get_master_data_with_flow_cons(item_id, flow):
    """Fetch master data details by itemID with pagination, routing based on flow

    Different flows use different ID fields:
    - consumable: uses 'requestID' field
    - default: uses 'itemID' field
    """
    try:
        token = get_access_token()
        if not token:
            return jsonify({'error': 'Failed to obtain access token'}), 500

        # Select the appropriate datatable endpoint based on flow
        if flow == 'consumable':
            datatable_endpoint = CONS_DATATABLE_ENDPOINT
            id_field = 'requestID'
            print(f"Using CONSUMABLE datatable endpoint for flow: {flow}")
        elif flow == 'ots':
            datatable_endpoint = OTS_DATATABLE_ENDPOINT
            id_field = 'requestID'
            print(f"Using OTS datatable endpoint for flow: {flow}")
            
        elif flow == 'repair':
            datatable_endpoint = REPAIR_DATATABLE_ENDPOINT
            id_field = 'requestID'
            print(f"Using REPAIR datatable endpoint for flow: {flow}")
        elif flow == 'ut':
            datatable_endpoint = USER_TRN_DATATABLE_ENDPOINT
            id_field = 'requestID'
            print(f"Using USER TRAINING datatable endpoint for flow: {flow}")    
            
        else:
            datatable_endpoint = DATATABLE_ENDPOINT
            id_field = 'itemID'
            print(f"Using DEFAULT datatable endpoint for flow: {flow}")

        print(f"Fetching data for {id_field}: {item_id}, flow: {flow}")

        # GET request to datatable endpoint with limit and offset parameters
        response = requests.get(
            f'{datatable_endpoint}?limit=100&offset=0',
            headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        )

        if response.status_code == 200:
            records = response.json()
            print(f"Fetched {len(records)} records from API")

            # Filter records by appropriate ID field based on flow
            # Try both string and integer comparison for id field
            matching_records = [r for r in records if str(r.get(id_field)) == str(item_id)]

            if matching_records:
                print(f"Found matching record for {id_field}: {item_id}")
                # Return the first matching record
                return jsonify({
                    'success': True,
                    'data': matching_records[0]
                })
            else:
                print(f"No matching record found for {id_field}: {item_id}")
                return jsonify({
                    'success': False,
                    'error': f'No record found with this {id_field}: {item_id}'
                }), 404
        else:
            print(f"API request failed: {response.status_code} - {response.text}")
            return jsonify({
                'success': False,
                'error': f'API request failed: {response.status_code}'
            }), response.status_code

    except Exception as e:
        print(f"Error in get_master_data_with_flow: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/get_master_data/<item_id>', methods=['GET'])
def get_master_data(item_id):
    """Fetch master data details by itemID with pagination (default flow)"""
    try:
        token = get_access_token()
        if not token:
            return jsonify({'error': 'Failed to obtain access token'}), 500

        # GET request to datatable endpoint with limit and offset parameters
        datatable_endpoint = DATATABLE_ENDPOINT
        print(f"Fetching data for item_id: {item_id} (default endpoint)")

        response = requests.get(
            f'{datatable_endpoint}?limit=100&offset=0',
            headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        )

        if response.status_code == 200:
            records = response.json()
            print(f"Fetched {len(records)} records from API")

            # Filter records by itemID
            matching_records = [r for r in records if r.get('itemID') == item_id]

            if matching_records:
                print(f"Found matching record for itemID: {item_id}")
                # Return the first matching record
                return jsonify({
                    'success': True,
                    'data': matching_records[0]
                })
            else:
                print(f"No matching record found for itemID: {item_id}")
                return jsonify({
                    'success': False,
                    'error': 'No record found with this Item ID'
                }), 404
        else:
            print(f"API request failed: {response.status_code} - {response.text}")
            return jsonify({
                'success': False,
                'error': f'API request failed: {response.status_code}'
            }), response.status_code

    except Exception as e:
        print(f"Error in get_master_data: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500        
        

@app.route('/generate_qr')
def generate_qr():
    """Generate QR code URL - with item_id and serial_code"""
    item_id = request.args.get('item_id', '')
    serial_code = request.args.get('serial_code', '')

    if not item_id:
        return jsonify({'error': 'Item ID is required'}), 400
    
    if not serial_code:
        return jsonify({'error': 'Serial Code is required'}), 400

    # Generate QR URL with item_id and serial_code
    qr_url = url_for('equipment_actions',
                     item_id=item_id,
                     serial_code=serial_code,
                     _external=True)
    
    return jsonify({'qr_url': qr_url})

# Add this new route for the rating page with optional flow parameter
@app.route('/rating/<item_id>')
@app.route('/rating/<item_id>/<flow>')
def rating_page(item_id, flow='default'):
    """Rating page for completed services

    URL patterns:
    - /rating/ITM021 -> default flow
    - /rating/ITM021/consumable -> consumable flow
    - /rating/ITM021/repair -> repair flow (future)
    """
    print("=" * 60)
    print("⭐ RATING PAGE ACCESSED")
    print(f"Item ID: {item_id}")
    print(f"Flow: {flow}")
    print("=" * 60)

    return render_template('rating.html', item_id=item_id, flow=flow)

# Unified route to handle rating submission for all activity types
@app.route('/api/submit_rating/<record_id>', methods=['POST'])
def submit_rating(record_id):
    """Submit rating using record_id - dynamically routes to correct endpoint based on activity type

    This function handles rating submissions for all activity types:
    - Consumable Request
    - User Training / User Training Request
    - One Time Service / One Time Service Request
    - Repair / Repair Request / Repair Process Request
    - Default (equipment)

    The activity type is passed from the frontend and determines which PUT endpoint to use.
    """
    try:
        data = request.get_json()
        rating = data.get('rating')
        comments = data.get('comments', '')
        item_id_from_body = data.get('item_id', '')
        activity_type = data.get('activity_type', 'default')  # Get activity type from request

        print("=" * 60)
        print("📝 RATING SUBMISSION REQUEST")
        print(f"Record ID: {record_id}")
        print(f"Rating: {rating}")
        print(f"Comments: {comments}")
        print(f"Item ID: {item_id_from_body}")
        print(f"Activity Type: {activity_type}")
        print("=" * 60)

        # Validate record_id is provided
        if not record_id:
            return jsonify({
                'success': False,
                'error': 'Record ID is required'
            }), 400

        # Valid rating text values
        valid_ratings = ['Highly Dissatisfied', 'Dissatisfied', 'Neutral', 'Satisfied', 'Highly Satisfied']

        if not rating or rating not in valid_ratings:
            return jsonify({
                'success': False,
                'error': f'Invalid rating. Must be one of: {", ".join(valid_ratings)}'
            }), 400

        # Get access token
        token = get_access_token()
        if not token:
            return jsonify({
                'success': False,
                'error': 'Failed to obtain access token'
            }), 500

        # Determine the correct PUT endpoint based on activity type
        put_endpoint = ACTIVITY_PUT_ENDPOINT_MAP.get(activity_type, ACTIVITY_PUT_ENDPOINT_MAP['default'])

        print(f"🎯 Activity Type: '{activity_type}'")
        print(f"🔗 Selected PUT Endpoint: {put_endpoint}")

        # Prepare PUT request payload
        # Different endpoints may use different field names for ratings
        if activity_type == 'Consumable Request':
            update_payload = {'feedback': rating}  # Consumable uses 'feedback' field
        elif activity_type == 'One Time Service Request' or activity_type == 'One Time Service':
            update_payload = {'feedback': rating}  # OTS uses 'feedback' field
        elif activity_type == 'Repair Process Request' or activity_type == 'Repair Request' or activity_type == 'Repair':
            update_payload = {'feedback': rating}  # Repair uses 'feedback' field
        elif activity_type == 'User Training' or activity_type == 'User Training Request':
            update_payload = {'feedBack': rating}    # User Training uses 'rating' field
        else:
            update_payload = {'rating': rating}    # Others use 'rating' field

        print(f"📤 Payload: {json.dumps(update_payload, indent=2)}")

        # Make PUT request to update the record
        update_url = f'{put_endpoint}/{record_id}'
        print(f"🌐 Full URL: {update_url}")

        response = requests.put(
            update_url,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "user-agent": 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
            },
            json=update_payload,
            timeout=10
        )

        print(f"📥 Response Status: {response.status_code}")
        print(f"📥 Response Body: {response.text}")

        if response.status_code in [200, 201, 204]:
            print("✅ Rating updated successfully")
            print("=" * 60)

            return jsonify({
                'success': True,
                'message': 'Rating submitted successfully!',
                'data': {
                    'rating': rating,
                    'comments': comments,
                    'record_id': record_id,
                    'activity_type': activity_type
                }
            })
        else:
            error_msg = f"API returned status {response.status_code}"
            try:
                error_data = response.json()
                error_msg = error_data.get('message') or error_data.get('error') or error_msg
            except:
                pass

            print(f"❌ Update failed: {error_msg}")
            print("=" * 60)

            return jsonify({
                'success': False,
                'error': error_msg
            }), response.status_code

    except requests.exceptions.Timeout:
        print("❌ Request timeout")
        print("=" * 60)
        return jsonify({
            'success': False,
            'error': 'Request timeout - API took too long to respond'
        }), 500
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        print("=" * 60)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)