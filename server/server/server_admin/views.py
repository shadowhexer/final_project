import base64, json
from django.db.models import Q
import requests
from server_admin.middleware.DecryptData import Decrypt
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from adrf.decorators import api_view
from .models import Message, CustomUser
from asgiref.sync import sync_to_async


@api_view(['POST'])
async def register(request):
    try: 
        data = json.loads(request.body)

        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        public_key = data.get('public_key')

        # Validate required fields
        if not all([username, email, password, public_key]):
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
            username=base64.b64decode(username.encode()).decode('utf-8'),
            email=base64.b64decode(email.encode()).decode('utf-8'),
            password=base64.b64decode(password.encode()).decode('utf-8'),
            public_key=public_key
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

    except requests.RequestException as e:
        return JsonResponse({'error': repr(e)}, status=500)


@api_view(['POST'])
async def get(request):

    if request.method == 'POST':
        # Parse JSON data from request body
        data = json.loads(request.body)
        auth = data.get('author')
        

        try:
            # Extract expected fields
            encrypted_data = data.get('encrypted_data')
            author = await sync_to_async (CustomUser.objects.get)(id=data.get('author'))
            key = data.get('key')
            iv = data.get('iv')

            if encrypted_data and author and key and iv:
                # Create a new Message instance with the decrypted data
                message = Message(message=encrypted_data, author_id=author, key=key, iv=iv)
                
                # Save the Message instance
                if hasattr(message, 'asave'):  # Check if async save is available
                    await message.asave()
                else:
                    await sync_to_async(message.save)()

                return JsonResponse({'message': 'Inserted successfully'}, status=200)
            else:
                return JsonResponse({'error': 'Empty data'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
        except Exception as e:
            return JsonResponse({'error': repr(e)}, status=500)



@api_view(['POST'])
async def send(request):
    if request.method == 'POST':
        try:
            # Fetch the message objects asynchronously
            messages = await sync_to_async(list)(Message.objects.select_related('author_id').all())

            messages_list = []
            
            for message in messages:
                # Add author details (if needed)
                author_details = {
                    'id': message.author_id.id,
                    'username': message.author_id.username  # Fetch username using select_related
                }
                
                receiver_payload = {
                    'author': author_details,  # Include full author details
                    'data': message.message,
                    'iv': message.iv,
                    'key': message.key,
                    'timeSent': message.timeStamp,
                }
                messages_list.append(receiver_payload)
            
            # Return the response directly as JSON
            return JsonResponse({'messages': messages_list}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON in request body'}, status=400)
        except Exception as e:
            # General exception handling for unexpected errors
            return JsonResponse({'error': f'An unexpected error occurred: {repr(e)}'}, status=500)
    

@api_view(['POST'])
async def user(request):

    if request.method == 'POST':
        data = json.loads(request.body)

        try:
                
            # Fetch the message object asynchronously
            user_object = await sync_to_async(CustomUser.objects.values('username', 'email', 'public_key').get)(username=data.get('username'))

            # Prepare the payload for the response
            receiver_payload = {
                'username': user_object['username'],
                'email': user_object['email'],
                'public_key': user_object['public_key'],
            }
            # Return the response directly as JSON
            return JsonResponse(receiver_payload, status=200)
        
        except CustomUser.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        except Exception as e:
            # Catch any unexpected errors
            return JsonResponse({'error': f'Unexpected error: {str(e)}'}, status=500)