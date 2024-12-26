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
        encrypted_data = getattr(request, 'encrypted_data', None)
        encrypted_session_key = getattr(request, 'session_key', None)
        iv = getattr(request, 'iv', None)

        # Check for missing data and log issues
        missing_data = []
        if not private_key:
            missing_data.append("private_key")
        if not encrypted_data:
            missing_data.append("encrypted_data")
        if not encrypted_session_key:
            missing_data.append("session_key")
        if not iv:
            missing_data.append("iv")

        if missing_data:
            request.error = f"Missing data for decryption: {', '.join(missing_data)}"
            return

        try:
            # Extract required data
            private_key = getattr(request, 'private_key', None)
            encrypted_data = getattr(request, 'encrypted_data', None)
            encrypted_session_key = getattr(request, 'session_key', None)
            iv = getattr(request, 'iv', None)

            # Ensure all data is present
            if not all([private_key, encrypted_data, encrypted_session_key, iv]):
                request.error = "Missing data for decryption"
                return

            # Convert data to bytes if necessary
            try:
                encrypted_data = encrypted_data.encode('utf-8') if isinstance(encrypted_data, str) else encrypted_data
                encrypted_session_key = (
                    encrypted_session_key.encode('utf-8') if isinstance(encrypted_session_key, str) else encrypted_session_key
                )
                iv = iv.encode('utf-8') if isinstance(iv, str) else iv
            except Exception as e:
                request.error = f"Error converting data to bytes: {repr(e)}"
                return

            # Decode Base64 encoded values
            try:
                decoded_data = base64.b64decode(encrypted_data)
                decoded_session_key = base64.b64decode(encrypted_session_key)
                decoded_iv = base64.b64decode(iv)
            except Exception as e:
                request.error = f"Error decoding Base64 values: {repr(e)}"
                return

            # Step 1: Decrypt the session key using RSA private key
            try:
                rsa_cipher_decrypt = PKCS1_OAEP.new(RSA.import_key(private_key))
                decrypted_session_key = rsa_cipher_decrypt.decrypt(decoded_session_key)
            except Exception as e:
                request.error = f"Error decrypting session key with RSA: {repr(e)}"
                return

            # Step 2: Decrypt the data using the AES session key
            try:
                aes_cipher_decrypt = AES.new(decrypted_session_key, AES.MODE_CBC, decoded_iv)
                decrypted_data = unpad(aes_cipher_decrypt.decrypt(decoded_data), AES.block_size)
            except ValueError as ve:
                request.error = f"Padding error during AES decryption: {repr(ve)}"
                return
            except Exception as e:
                request.error = f"Error decrypting data with AES: {repr(e)}"
                return

            # Set decrypted values on the request object
            request.data_response = decrypted_data.decode('utf-8')

        except ValueError as ve:
            request.error = f"Padding error: {repr(ve)}"
        except Exception as e:
            request.error = f"Decryption failed: {repr(e)}"

    def __call__(self, request):
        # Process the request
        self.process_request(request)
        # Pass the request to the next middleware or view
        response = self.get_response(request) if self.get_response else None
        return response
