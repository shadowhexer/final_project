import base64, json
from django.db.models import OuterRef, Subquery, Q
from django.contrib.auth import authenticate
import requests
from server_admin.middleware.DecryptData import Decrypt
from server_admin.middleware.EncryptData import Encrypt
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from adrf.decorators import api_view
from .models import Message, CustomUser
from asgiref.sync import sync_to_async
from utils.key_utils import KeyManager

@api_view(['GET'])
async def get_public_key(request):
    # Generate or retrieve the public key
    public_key = KeyManager.generate_keys('server')
    
    # Ensure the public key is returned as a string (if it’s a byte object)
    public_key_str = public_key.decode('utf-8') if isinstance(public_key, bytes) else str(public_key)
    
    return JsonResponse({'pub_key': public_key_str}, status=200)


@api_view(['POST'])
async def register(request):
    if(request.method == 'POST'):
        try: 
            private_key = KeyManager.get_private_key('server')
            data = json.loads(request.body)
            encrypted_data_list = data.get('encrypted_data', [])

            if encrypted_data_list:
                try:
                    decrypt = Decrypt(None)

                    # Pass the encrypted data to the decryption class
                    request.private_key = private_key
                    request.encrypted_data = encrypted_data_list

                    decrypt.process_request(request)
                    
                except json.JSONDecodeError:
                    return JsonResponse({'error': 'Invalid JSON format'}, status=400)
                except Exception as e:
                    return JsonResponse({'error': repr(e)}, status=500)
                
                try:
                    result = getattr(request, 'data_response', None)

                    username = result[0]
                    email = result[1]
                    password = result[2]

                    # Validate required fields
                    if not all([username, email, password]):
                        return JsonResponse({
                            'error': 'Missing required fields'
                        }, status=400)
                    
                    # Check if username exists
                    if await sync_to_async(CustomUser.objects.filter(Q(username=username) | Q(email=email)).exists)():
                        return JsonResponse({
                            'error': 'Already taken'
                        }, status=409)

                    # Create new user using Django's User model
                    new_user = await sync_to_async(CustomUser.objects.create_user)(
                        username=username,
                        email=email,
                        password=password,
                    )

                    # Check if user was created successfully
                    if new_user and new_user.id:
                        return JsonResponse({
                            'message': 'User registered successfully',
                            'user_id': new_user.id
                        }, status=201)
                    else:
                        return JsonResponse({
                            'error': 'Failed to create user'
                        }, status=500)
                
                except Exception as e:
                    return JsonResponse({'error': repr(e)}, status=500)

        except requests.RequestException as e:
            return JsonResponse({'error': repr(e)}, status=500)



@api_view(['POST'])
async def get_message(request):

    if request.method == 'POST':
        private_key = KeyManager.get_private_key('server')

        # Parse JSON data from request body
        data = json.loads(request.body)
        encrypted_data_list = data.get('encrypted_data', [])

        if encrypted_data_list:

            try:
                decrypt = Decrypt(None)

                # Pass the encrypted data to the decryption class
                request.private_key = private_key
                request.encrypted_data = encrypted_data_list

                decrypt.process_request(request)
                
            except json.JSONDecodeError:
                return JsonResponse({'error': 'Invalid JSON format'}, status=400)
            except Exception as e:
                return JsonResponse({'error': repr(e)}, status=500)
            
            try:
                result = getattr(request, 'data_response', None)

                decrypted_message = result[0]
                decrypted_author = result[1]
                decrypted_receiver = result[2]

                author_id = await sync_to_async (CustomUser.objects.get)(id=decrypted_author)
                receiver_id = await sync_to_async (CustomUser.objects.get)(id=decrypted_receiver)


                if author_id and receiver_id and receiver_id:
                    # Create a new Message instance with the decrypted data
                    message = Message(message=decrypted_message, author_id=author_id, receiver_id=receiver_id)
                    
                    # Save the Message instance
                    if hasattr(message, 'asave'):  # Check if async save is available
                        await message.asave()
                    else:
                        await sync_to_async(message.save)()

                    return JsonResponse({'message': 'Inserted successfully'}, status=200)
                else:
                    return JsonResponse({'error': 'Empty data'}, status=400)
                
            except CustomUser.DoesNotExist:
                return JsonResponse({'error': 'User not found'}, status=404)
            except Exception as e:
                return JsonResponse({'error': repr(e)}, status=500)


async def get_messages(sender_id, receiver_id):
    # Subquery to fetch the author's username
    author_username_subquery = CustomUser.objects.filter(
        id=OuterRef('author_id')
    ).values('username')[:1]

    # Subquery to fetch the receiver's username
    receiver_username_subquery = CustomUser.objects.filter(
        id=OuterRef('receiver_id')
    ).values('username')[:1]

    # Main query
    messages = await sync_to_async(
        lambda: list(
            Message.objects.select_related('author_id', 'receiver_id').filter(
                Q(author_id=sender_id, receiver_id=receiver_id) |
                Q(author_id=receiver_id, receiver_id=sender_id)
            ).order_by('timeStamp').annotate(
                author_username=Subquery(author_username_subquery),
                receiver_username=Subquery(receiver_username_subquery)
            ).values(
                'message', 'timeStamp', 'author_id', 'receiver_id',
                'author_username', 'receiver_username'
            ).iterator()
        )
    )()
    return messages


@api_view(['POST'])
async def return_message(request):
    if request.method == 'POST':
        private_key = KeyManager.get_private_key('server')
        try:
            data = json.loads(request.body)
            encrypted_data_list = data.get('encrypted_data', [])

            if encrypted_data_list:
                try:
                    decrypt = Decrypt(None)

                    # Pass the encrypted data to the decryption class
                    request.private_key = private_key
                    request.encrypted_data = encrypted_data_list

                    decrypt.process_request(request)
                    
                except json.JSONDecodeError:
                    return JsonResponse({'error': 'Invalid JSON format'}, status=400)
                except Exception as e:
                    return JsonResponse({'error': repr(e)}, status=500)


            # Query messages with error handling
            
            result = getattr(request, 'data_response', None)

            messages = await get_messages(result[0], result[1])

            # print(messages)

            if not messages:
                return JsonResponse({'error': 'No messages found'}, status=404)

            try: # Send the messages as a JSON response

                admin_api_url = 'http://127.0.0.1:8000/pub_key'
                headers = {'Content-Type': 'application/json'}

                try:
                    admin_response = requests.get(admin_api_url, headers=headers)
                except requests.RequestException as e:
                    return JsonResponse({'error': f'Failed to fetch public key: {repr(e)}'}, status=500)

                if admin_response.status_code == 200:
                    response = admin_response.json()

                    # Initialize encryption logic
                    encrypt = Encrypt(None)  # Assuming Encrypt is correctly defined

                    try:

                        # Initialize the list to store encrypted messages
                        messages_list = []

                        # Loop through each message
                        # Loop through each message
                        for message in messages:
                            try:
                                # Prepare the data for encryption
                                request.encrypt_data = message['message']
                                request.public_key = response.get('pub_key')

                                # Encrypt the data
                                encrypt.process_request(request)
                                result = getattr(request, 'encrypted_data', [])

                                if not result:
                                    raise ValueError("Encryption process did not return any data.")

                                # Validate the encryption result
                                for encrypted_message in result:
                                    if 'value' not in encrypted_message or 'iv' not in encrypted_message or 'session_key' not in encrypted_message:
                                        return JsonResponse({'error': 'Invalid encryption result format.'}, status=500)

                                    # Append the encrypted message to the list
                                    messages_list.append({
                                        'author_id': message['author_id'],
                                        'receiver_id': message['receiver_id'],
                                        'author_username': message['author_username'],
                                        'receiver_username': message['receiver_username'],
                                        'data': encrypted_message,  # Include the encrypted data
                                        'timestamp': message['timeStamp']
                                    })

                            except Exception as e:
                                # Handle encryption errors for individual messages
                                return JsonResponse({'error': f'Encryption failed for message {message["message"]}: {repr(e)}'}, status=500)

                        # Return the list of encrypted messages
                        # print('Items: ', messages_list)
                        return JsonResponse({'messages': messages_list}, status=200)

                    except Exception as e:
                        # Handle unexpected errors
                        return JsonResponse({'error': f'An unexpected error occurred: {repr(e)}'}, status=500)

                    except Exception as e:
                        # Handle unexpected errors
                        return JsonResponse({'error': f'An unexpected error occurred: {repr(e)}'}, status=500)

                else:
                    return JsonResponse({'error5': 'Failed to fetch public key'}, status=500)
            
            except Exception as e:
                return JsonResponse({'error6': str(e)}, status=500)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'errorc': str(e)}, status=500)
    

@api_view(['POST'])
async def user(request):

    if request.method == 'POST':
        data = json.loads(request.body)

        try:
                
            # Fetch the message object asynchronously
            user_object = await sync_to_async(CustomUser.objects.values('id', 'username', 'email').get)(username=data.get('username'))

            # Prepare the payload for the response
            receiver_payload = {
                'id': user_object['id'],
                'username': user_object['username'],
                'email': user_object['email'],
            }
            # Return the response directly as JSON
            return JsonResponse(receiver_payload, status=200)
        
        except CustomUser.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        except Exception as e:
            # Catch any unexpected errors
            return JsonResponse({'error': f'Unexpected error: {str(e)}'}, status=500)


@api_view(['POST'])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return JsonResponse({'error': 'Email and password are required'}, status=400)
    
    try:
        # Find user by email
        user = CustomUser.objects.get(email=email)
        
        # Authenticate credentials
        auth_user = authenticate(username=user.username, password=password)
        
        if auth_user is not None:
            return JsonResponse({
                'status': 'success',
                'user_id': auth_user.id,
                'email': auth_user.email,
                'username': auth_user.username,
            }, status=200)
        else:
            return JsonResponse({'error': 'Invalid credentials'}, status=401)
            
    except CustomUser.DoesNotExist:
        return JsonResponse({'error': 'Not Found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)