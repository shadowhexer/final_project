from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Util.Padding import pad, unpad
import os

class Encrypt:
    def __init__(self, get_response=None):
        self.get_response = get_response

    def process_request(self, request):
        # Extract data from request attributes
        data = getattr(request, 'encrypt_data', None)
        # author = getattr(request, 'encrypt_author', None)
        public_key = getattr(request, 'public_key', None)
    
        if data and public_key:
            try:
                # Ensure data is in bytes
                data = data.encode('utf-8') if isinstance(data, str) else data
                public_key = public_key.encode('utf-8') if isinstance(public_key, str) else public_key
                
                # Generate a symmetric AES session key
                session_key = os.urandom(16)

                # Encrypt the session key using RSA public key
                rsa_cipher = PKCS1_OAEP.new(RSA.import_key(public_key))
                encrypted_session_key = rsa_cipher.encrypt(session_key)

                # Encrypt the data and author using AES
                aes_cipher = AES.new(session_key, AES.MODE_CBC)
                iv = aes_cipher.iv
                encrypted_data = aes_cipher.encrypt(pad(data, AES.block_size))
                # encrypted_author = aes_cipher.encrypt(pad(author, AES.block_size))

                # Set encrypted values in request
                request.encrypted_data = encrypted_data
                # request.encrypted_author = encrypted_author
                request.encrypted_session_key = encrypted_session_key
                request.iv = iv
            except Exception as e:
                # Handle encryption errors
                request.error = f"Encryption failed: {repr(e)}"
        else:
            request.error = f"Missing data for encryption"

    def __call__(self, request):
        # Process the request
        self.process_request(request)
        # Pass the request to the next middleware or view
        response = self.get_response(request) if self.get_response else None
        return response
