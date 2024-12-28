from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Util.Padding import pad, unpad
import os, base64

class Encrypt:
    def __init__(self, get_response=None):
        self.get_response = get_response

    def process_request(self, request):
        public_key = getattr(request, 'public_key', None)

        if hasattr(request, 'encrypt_data') and public_key:
            try:
                # Ensure public key is in bytes
                public_key = public_key.encode('utf-8') if isinstance(public_key, str) else public_key

                # Prepare a list for encrypted data with associated IV and session key
                encrypted_data_list = []

                # Get the data to encrypt (normalize to a list)
                encrypt_data = getattr(request, 'encrypt_data', [])
                if not isinstance(encrypt_data, list):
                    encrypt_data = [encrypt_data]  # Wrap non-list values in a list

                for value in encrypt_data:
                    # Generate a unique session key and IV for each value
                    
                    session_key = os.urandom(16)
                    aes_cipher = AES.new(session_key, AES.MODE_CBC)
                    iv = aes_cipher.iv

                    # Encrypt the session key using RSA public key
                    rsa_cipher = PKCS1_OAEP.new(RSA.import_key(public_key))
                    encrypted_session_key = rsa_cipher.encrypt(session_key)

                    # Ensure the value is in bytes
                    value = value.encode('utf-8') if isinstance(value, str) else value

                    # Encrypt the data using AES
                    encrypted_value = aes_cipher.encrypt(pad(value, AES.block_size))

                    # Append the encrypted data and associated parameters
                    encrypted_data_list.append({
                        "value": base64.b64encode(encrypted_value).decode('utf-8'),
                        "iv": base64.b64encode(iv).decode('utf-8'),
                        "session_key": base64.b64encode(encrypted_session_key).decode('utf-8')
                    })

                # Store the structured data in the request
                request.encrypted_data = encrypted_data_list

            except Exception as e:
                request.error = f"Encryption failed: {repr(e)}"
        else:
            request.error = "Missing data for encryption"


    def __call__(self, request):
        # Process the request
        self.process_request(request)
        # Pass the request to the next middleware or view
        response = self.get_response(request) if self.get_response else None
        return response
