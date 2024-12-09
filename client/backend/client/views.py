import os, requests, base64, json, httpx
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view
from client.middleware import Encrypt, Decrypt

# Step 1: Generate RSA public/private keys
rsa_key = RSA.generate(2048)
private_key = rsa_key.export_key()
public_key = rsa_key.publickey().export_key()


# # Create your views here.
# @api_view(['POST'])
# def registration(request): 
#     username = request.data.get('username')
#     email = request.data.get('email')
#     password = request.data.get('password')

#     if username and email and password:
#         return JsonResponse({'message': 'Registered successfully'}, statuse=200)
#     else:
#         return JsonResponse({'error': 'Invalid data'}, status=400)


# @api_view(['POST'])
# def login(request):
#     email = request.data.get('email')
#     password = request.data.get('password')

#     stored_email = 'amba@tu.blaw'
#     stored_password = 'omayghat_oshet'

#     if email and password:
#         if email == stored_email and password == stored_password:
#             return JsonResponse({'message': 'Login Successfully'}, status=201)
#         else: 
#             return JsonResponse({'error', 'Invalid credentiaks'}, status=400)
#     else: 
#         return JsonResponse({'error': 'Invalid data'}, status=400)\
    

@api_view(['POST'])
def send_message(request):
    import uuid, logging
    
    # Setup logging
    logging.basicConfig(level=logging.DEBUG)

    reference_key = str(uuid.uuid4()).encode('utf-8')  # Ensure it's bytes

    if request.method == 'POST':

        data = json.loads(request.body)

        # Explicitly call the middleware
        encrypt = Encrypt(None)  # Assuming None is acceptable as the argument

        # Attach data to the request for encryption
        request.encrypt_data = data.get('message')  # Use bytes
        request.encrypt_author = data.get('author')  # Use bytes
        request.public_key = public_key  # Ensure `public_key` is defined correctly

        encrypt.process_request(request)

    # Retrieve encrypted data from the request
    encrypted_data = getattr(request, 'encrypted_data', None)
    encrypted_author = getattr(request, 'encrypted_author', None)
    encrypted_session_key = getattr(request, 'encrypted_session_key', None)
    iv = getattr(request, 'iv', None)

    if encrypted_data and encrypted_session_key and iv:
        try:
            # Create payloads for APIs
            server = {
                'reference_key': base64.b64encode(reference_key).decode('utf-8'),
                'author': base64.b64encode(encrypted_author).decode('utf-8'),
                'encrypted_data': base64.b64encode(encrypted_data).decode('utf-8'),
            }

            # Send data to APIs
            admin_api_url = 'http://127.0.0.1:7000/receive/'
            headers = {'Content-Type': 'application/json'}

            admin_response = requests.post(admin_api_url, json=server, headers=headers)

            # Check API responses
            if admin_response.status_code == 200:
                return JsonResponse({
                'reference_key': base64.b64encode(reference_key).decode('utf-8'),
                'key': base64.b64encode(encrypted_session_key).decode('utf-8'),
                'iv': base64.b64encode(iv).decode('utf-8'),
            }, status=200)

            else:
                return JsonResponse({
                    'error': 'Failed to send data to one or both APIs',
                    'admin_status': admin_response.status_code,
                    'admin_response': admin_response.text,
                }, status=500)
            

        except requests.RequestException as e:
            logging.error("API Request failed: %s", str(e))
            return JsonResponse({'error': f'API Request failed: {str(e)}'}, status=500)

    return JsonResponse({'error': 'Failed to process encryption'}, status=500)


@api_view(['POST'])
def receive_message(request):
    try:
        # Parse the incoming JSON request body
        if request.method == 'POST':
            data = json.loads(request.body)
            
            reference_key = data.get('reference_key')
            encrypted_session_key = data.get('key')
            encrypted_iv = data.get('iv')

            # Handle the case when the request contains a reference key, session key, and IV
            if reference_key and encrypted_session_key and encrypted_iv:
                    
                # Prepare the payload for sending to the admin API
                server_payload = {'reference_key': reference_key}
                admin_api_url = 'http://127.0.0.1:7000/send/'
                headers = {'Content-Type': 'application/json'}

                # Send the data to the admin API asynchronously
                response = requests.post(admin_api_url, json=server_payload, headers=headers)
                response.raise_for_status()

                response_data = response.json()

                decrypt = Decrypt(None)

                # Assuming `private_key` is provided by some method, e.g., as part of the request or server settings
                request.private_key = private_key  
                request.encrypted_data = response_data.get('data')
                request.encrypted_author = response_data.get('author')
                request.session_key = encrypted_session_key
                request.iv = encrypted_iv

                decrypt.process_request(request)

                author = getattr(request, 'author_response', None)
                message = getattr(request, 'data_response', None)

                if not author and not message:
                    return JsonResponse({'error': getattr(request, 'error', None)}, status=500)
                
                else:
                    return JsonResponse({'author': author, 'message': message}, status=200)

            else:
                return JsonResponse({'error': 'Missing required data in POST request'}, status=400)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON in request body'}, status=400)
    except httpx.RequestError as e:
        return JsonResponse({'error': f'Failed to send data to admin API: {str(e)}'}, status=500)
    except Exception as e:
        return JsonResponse({'error': f'Unexpected error: {str(e)}'}, status=500)