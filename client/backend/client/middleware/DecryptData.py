import base64
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Util.Padding import unpad

class Decrypt:
    def __init__(self, get_response=None):
        self.get_response = get_response

    def process_request(self, request):

        # Extract required data from request
        private_key = getattr(request, 'private_key', None)
        
        # Get the data to encrypt (normalize to a list)
        encrypted_data_list = getattr(request, 'encrypted_data', [])
        if not isinstance(encrypted_data_list, list):
            encrypted_data_list = [encrypted_data_list]  # Wrap non-list values in a list

        # Check for missing data and log issues
        if not private_key:
            request.error = "Missing private key"
            return
        
        if not encrypted_data_list:
            request.error = "Missing encrypted data"
            return

        decrypted_values = []
        for encrypted_data in encrypted_data_list:
            value = encrypted_data['value']
            iv = encrypted_data['iv']
            encrypted_session_key = encrypted_data['session_key']

            # Check for missing values
            if not all([value, iv, encrypted_session_key]):
                request.error = "Missing value, iv or session_key"
                return
            
            try:
                # Decrypt the session key with RSA
                rsa_cipher_decrypt = PKCS1_OAEP.new(RSA.import_key(private_key))
                decrypted_session_key = rsa_cipher_decrypt.decrypt(base64.b64decode(encrypted_session_key))
                aes_cipher_decrypt = AES.new(decrypted_session_key, AES.MODE_CBC, base64.b64decode(iv))

                # Decrypt the value
                decrypted_value = base64.b64decode(value)
                decrypted_data = unpad(aes_cipher_decrypt.decrypt(decrypted_value), AES.block_size)
                decrypted_values.append(decrypted_data.decode('utf-8'))

            except Exception as e:
                request.error = f"Decryption error: {repr(e)}"
                return
            
        # Store the decrypted values in the request
        request.data_response = decrypted_values

    def __call__(self, request):
        # Process the request
        self.process_request(request)
        # Pass the request to the next middleware or view
        response = self.get_response(request) if self.get_response else None
        return response
