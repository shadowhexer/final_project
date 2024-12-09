import json
import os, requests
from admin.middleware.DecryptData import Decrypt
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from adrf.decorators import api_view
from .models import Message
from asgiref.sync import sync_to_async

@api_view(['POST'])
async def get(request):
    try:
        # Parse JSON data from request body
        data = json.loads(request.body)
        
        # Extract expected fields
        encrypted_data = data.get('encrypted_data')
        author = data.get('author')
        encrypted_reference_key = data.get('reference_key')

        if encrypted_data and author and encrypted_reference_key:
            # Create a new Message instance with the decrypted data
            message = Message(ref_key=encrypted_reference_key, author=author, message=encrypted_data)
            
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
        # Parse the incoming JSON request body
        data = json.loads(request.body)
        
        # Extract the reference key from the data
        encrypted_reference_key = data.get('reference_key')
        
        if not encrypted_reference_key:
            return JsonResponse({'error': 'Reference key is required'}, status=400)

        # Fetch the message object asynchronously
        message_object = await sync_to_async(Message.objects.get)(ref_key=encrypted_reference_key)
        
        # Prepare the payload for the response
        receiver_payload = {
            'author': message_object.author,
            'data': message_object.message,
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