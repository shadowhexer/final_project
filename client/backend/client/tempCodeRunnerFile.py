import uuid

reference_key = str(uuid.uuid4()).encode('utf-8')  # Ensure it's bytes
message = b'Hello there animal'  # Use bytes
author = b'Hexer'  # Use bytes

# Attach data to the request for encryption
request.encrypt_data = message
request.encrypt_author = author
request.public_key = public_key  # Ensure `public_key` is defined correctly

# Explicitly call the middleware
encrypt = Encrypt(None)  # Assuming None is acceptable as the argument
encrypt.process_request(request)

# Retrieve encrypted data from the request
encrypted_data = getattr(request, 'encrypted_data', None)
encrypted_author = getattr(request, 'encrypted_author', None)
encrypted_session_key = getattr(request, 'encrypted_session_key', None)
iv = getattr(request, 'iv', None)

print(encrypted_data)