import os, requests, base64, json, httpx
from utils.key_utils import KeyManager
from Crypto.Cipher import PKCS1_OAEP
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view
from client.middleware import Encrypt, Decrypt

# Step 1: Generate RSA public/private keys
@api_view(['GET'])
def get_public_key(request):
    # Generate or retrieve the public key
    public_key = KeyManager.generate_keys('client')
    
    # Ensure the public key is returned as a string (if it’s a byte object)
    public_key_str = public_key.decode('utf-8') if isinstance(public_key, bytes) else str(public_key)
    
    return JsonResponse({'pub_key': public_key_str}, status=200)


def fetch_public_key():
    admin_api_url = 'http://127.0.0.1:7000/pub_key'
    try:
        admin_response = requests.get(admin_api_url, headers={'Content-Type': 'application/json'})
        admin_response.raise_for_status()  # Ensures status is 200
        data = admin_response.json().get('pub_key')
        return data
    except requests.RequestException as e:
        raise Exception(f"Failed to fetch public key: {str(e)}")


# Create your views here.
@api_view(['POST'])
def registration(request): 

    if request.method == 'POST':
        # Ensure private key is generated
        data = json.loads(request.body)

        pub_key = fetch_public_key()

        # Initialize encryption logic
        encrypt = Encrypt(None)  # Assuming Encrypt is correctly defined

        values_to_encrypt = [
            str(data.get('username')),
            str(data.get('email')),
            str(data.get('password')),
        ]

        # Attach data to the request for encryption
        request.encrypt_data = values_to_encrypt
        request.public_key = pub_key

        # Process the request with encryption logic
        encrypt.process_request(request)

        # Retrieve encrypted data from the request
        result = getattr(request, 'encrypted_data', None)

        if result:
            try:
                server_payload = { 'encrypted_data': result }

                # Send encrypted data to server
                admin_api_url = 'http://127.0.0.1:7000/register/'
                headers = {'Content-Type': 'application/json'}
                admin_response = requests.post(admin_api_url, json=server_payload, headers=headers)

                # Check API responses
                if admin_response.status_code == 201:
                    return JsonResponse({'status': 'success'}, status=200)

                else:
                    return JsonResponse({
                        'error': 'Failed to register',
                    }, status=500)
                
            except requests.RequestException as e: 
                return JsonResponse({'Request failed': repr(e), 'Payload': server_payload}, status=500)

        else:
            return JsonResponse({'error': result}, status=400)
    


# Send message to server
@api_view(['POST'])
def send_message(request):
    if request.method == 'POST':
        data = json.loads(request.body)  # From the front end

        pub_key = fetch_public_key()

        # Initialize encryption logic
        encrypt = Encrypt(None)  # Assuming Encrypt is correctly defined

        values_to_encrypt = [
            str(data.get('message')),
            str(data.get('author_id')),
            str(data.get('receiver_id')),
        ]

        # Attach data to the request for encryption
        request.encrypt_data = values_to_encrypt
        request.public_key = pub_key

        # Process the request with encryption logic
        encrypt.process_request(request)

        # Retrieve encrypted data from the request
        result = getattr(request, 'encrypted_data', None)

        if result:
            try:
                server_payload = { 'encrypted_data': result }

                # Send encrypted data to server
                admin_api_url = 'http://127.0.0.1:7000/send/'
                headers = {'Content-Type': 'application/json'}
                admin_response = requests.post(admin_api_url, json=server_payload, headers=headers)

                # Check API response
                if admin_response.status_code == 200:
                    return JsonResponse({'status': 'Success'}, status=200)
                else:
                    return JsonResponse({'error': admin_response.json()}, status=500)
            except requests.RequestException as e:
                return JsonResponse({'error': f'Failed to send encrypted data: {repr(e)}'}, status=500)

        # Handle encryption failure
        error = getattr(request, 'error', 'Unknown encryption error occurred.')
        return JsonResponse({'error': error}, status=500)
    else:
        return JsonResponse({'error': 'Failed to retrieve public key'}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)




def process(request, item):
    try:
        # Load the Decrypt middleware and private key
        private_key = KeyManager.get_private_key('client')
        if not private_key:
            return {'error': 'Private key not found'}

        decrypt = Decrypt(None)

        # Attach data to the request object for middleware processing
        request.private_key = private_key
        request.encrypted_data = item['data']

        # Process the request using the middleware
        decrypt.process_request(request)

        # Retrieve decrypted data from the request
        result = getattr(request, 'data_response', None)
        if not result:
            return {'error': 'Decryption failed or no data returned'}

        # Return the transformed message
        return result
    except KeyError as e:
        # Handle missing keys in the item dictionary
        return {'error': f'Missing key: {repr(e)}'}
    except AttributeError as e:
        # Handle issues with attributes (e.g., result being None)
        return {'error': f'Attribute error: {repr(e)}'}
    except Exception as e:
        # Catch-all for other errors
        return {'error9': f'Error processing message: {repr(e)}'}




@api_view(['POST'])
def receive_message(request):
        
    if request.method == 'POST':
        try:
            # Parse the incoming JSON request body
            data = json.loads(request.body)

            # Get the public key from the server
            try:
                pub_key = fetch_public_key()

                # Initialize encryption logic
                encrypt = Encrypt(None)  # Assuming Encrypt is correctly defined

                values_to_encrypt = [
                    str(data.get('author_id')),
                    str(data.get('receiver_id')),
                ]

                # Attach data to the request for encryption
                request.encrypt_data = values_to_encrypt
                request.public_key = pub_key

                # Process the request with encryption logic
                encrypt.process_request(request)

                # Retrieve encrypted data from the request
                result = getattr(request, 'encrypted_data', None)

                if not result:
                    return JsonResponse({'error1': 'Encryption failed, no encrypted data found'}, status=500)

                else:
                    try:
                        server_payload = { 'encrypted_data': result }

                        # print(server_payload)

                        # Send encrypted data to server
                        admin_api_url = 'http://127.0.0.1:7000/return/'
                        headers = {'Content-Type': 'application/json'}
                        admin_response = requests.post(admin_api_url, json=server_payload, headers=headers)

                        # Check API response
                        if admin_response.status_code == 200:
                            admin_response.raise_for_status()

                            data = admin_response.json()
                            messages_data = data.get('messages', [])

                            if not isinstance(messages_data, list):
                                return JsonResponse({'error': 'Invalid data format for messages'}, status=500)

                            # Loop through each message and process it
                            messages = []
                            for item in messages_data:
                                # print("M: ", item)
                                processed_message = process(request, item)

                                if 'error' in processed_message:
                                    return JsonResponse({'error': processed_message['error']}, status=500)
                                
                                messages.append({
                                        'author_id': item['author_id'],
                                        'receiver_id': item['receiver_id'],
                                        'author_username': item['author_username'],
                                        'receiver_username': item['receiver_username'],
                                        'message': processed_message,  # Include the encrypted data
                                        'timeSent': item['timestamp']
                                    })

                            # Return all processed messages
                            return JsonResponse({'messages': messages}, status=200)
                        else:
                            return JsonResponse({'error2': admin_response.json()}, status=500)
                    except requests.RequestException as e:
                        return JsonResponse({'error3': f'Failed to send encrypted data: {repr(e)}'}, status=500)
                    
            except Exception as e:
                return JsonResponse({'error4': str(e)}, status=500)

        except json.JSONDecodeError:
            return JsonResponse({'error5': 'Invalid JSON in request body'}, status=400)
        except httpx.RequestError as e:
            return JsonResponse({'error6': f'Failed to send data to admin API: {str(e)}'}, status=500)
        except Exception as e:
            return JsonResponse({'error7': f'Unexpected error: {repr(e)}'}, status=500)

 
@api_view(['POST'])
def get_user(request):

    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            payload = {
                'username': data.get('username'),
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