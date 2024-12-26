import os, requests, base64, json, httpx
from utils.key_utils import KeyManager
from Crypto.Cipher import PKCS1_OAEP
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view
from client.middleware import Encrypt, Decrypt

# Step 1: Generate RSA public/private keys


# Create your views here.
@api_view(['POST'])
def registration(request): 

    if request.method == 'POST':
        # Ensure private key is generated
        data = json.loads(request.body)

        username = data.get('username')
        public_key = KeyManager.generate_keys(username)

        email = data.get('email')
        password = data.get('password')

        if username and email and password and public_key:
            try:
                # Create payloads for APIs
                server = {
                    'username': base64.b64encode(username.encode()).decode('utf-8'),
                    'email': base64.b64encode(email.encode()).decode('utf-8'),
                    'password': base64.b64encode(password.encode()).decode('utf-8'),
                    'public_key': public_key.decode('utf-8'),
                }

                # Send data to APIs
                admin_api_url = 'http://127.0.0.1:7000/register/'
                headers = {'Content-Type': 'application/json'}

                admin_response = requests.post(admin_api_url, json=server, headers=headers)

                # Check API responses
                if admin_response.status_code == 201:
                    return JsonResponse({'status': 'Success'}, status=200)

                else:
                    return JsonResponse({
                        'error': 'Failed to register',
                    }, status=500)
                
            except requests.RequestException as e: 
                return JsonResponse({'Request failed': repr(e), 'Payload': server}, status=500)

        else:
            return JsonResponse({'error': 'Invalid data'}, status=400)
    

@api_view(['POST'])
def send_message(request):
    import uuid, logging
    
    # Setup logging
    # logging.basicConfig(level=logging.DEBUG)

    # Retrieve data from the request
    if request.method == 'POST':

        data = json.loads(request.body)
        author = data.get('author')

        # Explicitly call the middleware
        encrypt = Encrypt(None)  # Assuming None is acceptable as the argument

        # Attach data to the request for encryption
        request.encrypt_data = data.get('message')  # Use bytes
        request.public_key = data.get('public_key').encode()  # Ensure `public_key` is defined correctly

        # Uncomment this if middleware in the server side is setup or DB column is modified
        # request.encrypt_author = data.get('author')  

        encrypt.process_request(request)


    # Retrieve encrypted data from the request
    encrypted_data = getattr(request, 'encrypted_data', None)
    # encrypted_author = getattr(request, 'encrypted_author', None)
    encrypted_session_key = getattr(request, 'encrypted_session_key', None)
    iv = getattr(request, 'iv', None)

    if encrypted_data and author and encrypted_session_key and iv:
        try:
            # Create payloads for APIs
            server = {
                'key': base64.b64encode(encrypted_session_key).decode('utf-8'),
                'iv': base64.b64encode(iv).decode('utf-8'),
                'author': author,
                'encrypted_data': base64.b64encode(encrypted_data).decode('utf-8'),
            }

            # Send data to APIs
            admin_api_url = 'http://127.0.0.1:7000/receive/'
            headers = {'Content-Type': 'application/json'}

            admin_response = requests.post(admin_api_url, json=server, headers=headers)

            # Check API responses
            if admin_response.status_code == 200:
                return JsonResponse({'status': 'Success'}, status=200)

            else:
                return JsonResponse({
                    'Failed': admin_response.json(),
                }, status=500)
            
        except requests.RequestException as e:
            return JsonResponse({'error': f'API Request failed: {repr(e)}'}, status=500)

    return JsonResponse({'error': 'Failed to process encryption'}, status=500)





def process(request, item, username):
    try:
        
        
        # Extract author details
        author = item.get('author', {})
        author_id = author.get('id')
        author_username = author.get('username')

        # Extract message details
        time_sent = item.get('timeSent')

        # Load the Decrypt middleware
        decrypt = Decrypt(None)
        private_key = KeyManager.get_private_key(username)

        request.private_key = private_key
        # Attach data to request for middleware processing
        request.encrypted_data = item.get('data').encode()
        request.session_key = item.get('key').encode()
        request.iv = item.get('iv').encode()
        
        decrypt.process_request(request)

        # Middleware function (example: decryption middleware)
        # Call your middleware here, e.g., decrypt.process_request(request)
        # Assuming your middleware processes `request` and attaches decrypted data
        decrypted_message = getattr(request, 'data_response', None)

        # Return the transformed message
        return {
            'author': {
                'id': author_id,
                'username': author_username,
            },
            'message': decrypted_message,
            'timeSent': time_sent,
        }
    except Exception as e:
        # Handle errors for individual message processing
        return {'error': f'Error processing message: {repr(e)}'}






@api_view(['POST'])
def receive_message(request):
        
    if request.method == 'POST':
        try:
            # Parse the incoming JSON request body
            data = json.loads(request.body)
            username = data.get('username')
            
            # Prepare the payload for sending to the admin API
            admin_api_url = 'http://127.0.0.1:7000/send/'
            headers = {'Content-Type': 'application/json'}

            # Send the data to the admin API asynchronously
            response = requests.post(admin_api_url, headers=headers)
            response.raise_for_status()

            data = response.json()
            messages = []

            

            # Loop through each message and process it
            for item in data.get('messages', []):
                processed_message = process(request, item, username)
                messages.append(processed_message)

            return JsonResponse({'messages': messages}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON in request body'}, status=400)
        except httpx.RequestError as e:
            return JsonResponse({'error': f'Failed to send data to admin API: {str(e)}'}, status=500)
        except Exception as e:
            return JsonResponse({'error': f'Unexpected error: {repr(e)}'}, status=500)








 
@api_view(['GET'])
def get_user(request):

    if request.method == 'GET':
        username = request.GET.get('username')

        try:
            payload = {
                'username': username,
            }

            # Prepare the payload for sending to the admin API
            admin_api_url = 'http://127.0.0.1:7000/user/'
            headers = {'Content-Type': 'application/json'}

            # Send the data to the admin API asynchronously
            response = requests.post(admin_api_url, json=payload, headers=headers)
            response.raise_for_status()

            data = response.json()
            if data:
                return JsonResponse({'users': data}, status=200)
            else:
                return JsonResponse({'error': 'No users to display'}, status=400)
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON in request body'}, status=400)
        except httpx.RequestError as e:
            return JsonResponse({'error': f'Failed to send data to admin API: {str(e)}'}, status=500)
        except Exception as e:
            return JsonResponse({'error': f'Unexpected error: {str(e)}'}, status=500)