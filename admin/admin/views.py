import base64, json
from django.db.models import Q
from admin.middleware.DecryptData import Decrypt
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from adrf.decorators import api_view
from .models import Message, User
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
        if await sync_to_async(User.objects.filter(Q(username=username) | Q(email=email)).exists)():
            return JsonResponse({
                'error': 'Already taken'
            }, status=409)

        # Create new user using Django's User model
        new_user = await sync_to_async(User.objects.create_user)(
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

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@api_view(['POST'])
async def get(request):
    try:
        # Parse JSON data from request body
        data = json.loads(request.body)
        
        # Extract expected fields
        encrypted_data = data.get('encrypted_data')
        author = data.get('author')
        key = data.get('key')
        iv = data.get('iv')

        if encrypted_data and author and key and iv:
            # Create a new Message instance with the decrypted data
            message = Message(message=encrypted_data, author=author, key=key, iv=iv)
            
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
        return JsonResponse({'error': str(e)}, status=500)

@api_view(['POST'])
async def send(request):
    try:

        # Fetch the message object asynchronously
        message_object = await sync_to_async(Message.objects.all)()
        
        # Prepare the payload for the response
        receiver_payload = {
            'author': message_object.author,
            'data': message_object.message,
            'iv': message_object.iv,
            'key': message_object.key,
            'timeSent': message_object.timeStamp,

        }

        # Return the response directly as JSON
        return JsonResponse(receiver_payload, status=200)

    except Message.DoesNotExist:
        return JsonResponse({'error': 'Message not found'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON in request body'}, status=400)
    except Exception as e:
        # General exception handling for unexpected errors
        return JsonResponse({'error': f'An unexpected error occurred: {str(e)}'}, status=500)