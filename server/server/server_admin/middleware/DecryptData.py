import base64
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Util.Padding import unpad

class Decrypt:
    def __init__(self, get_response=None):
        self.get_response = get_response

    def process_request(self, request):
        # Extract required data from request
        private_key = getattr(request, 'private_key', None)  # Assuming this contains the private RSA key (PEM format)
        encrypted_data = getattr(request, 'encrypted_data', None)  # Base64 encoded ciphertext
        encrypted_author = getattr(request, 'encrypted_author', None)  # Base64 encoded ciphertext
        encrypted_session_key = getattr(request, 'session_key', None)  # Base64 encoded RSA-encrypted session key
        iv = getattr(request, 'iv', None)  # Base64 encoded initialization vector

        # Check for required attributes on the request
        if private_key and encrypted_data and encrypted_author and encrypted_session_key and iv:
            try:

                encrypted_data = encrypted_data.encode('utf-8') if isinstance(encrypted_data, str) else encrypted_data
                encrypted_author = encrypted_author.encode('utf-8') if isinstance(encrypted_author, str) else encrypted_author
                encrypted_session_key = encrypted_session_key.encode('utf-8') if isinstance(encrypted_session_key, str) else encrypted_session_key
                iv = iv.encode('utf-8') if isinstance(iv, str) else iv

                # Decode Base64 encoded values (no UTF-8 decoding needed here)
                decoded_data = base64.b64decode(encrypted_data)
                decoded_author = base64.b64decode(encrypted_author)
                decoded_session_key = base64.b64decode(encrypted_session_key)
                decoded_iv = base64.b64decode(iv)

                # Step 1: Decrypt the session key using RSA private key
                rsa_cipher_decrypt = PKCS1_OAEP.new(RSA.import_key(private_key))
                decrypted_session_key = rsa_cipher_decrypt.decrypt(decoded_session_key)

                # Step 2: Decrypt the data and author using the AES session key
                aes_cipher_decrypt = AES.new(decrypted_session_key, AES.MODE_CBC, decoded_iv)
                decrypted_data = unpad(aes_cipher_decrypt.decrypt(decoded_data), AES.block_size)
                decrypted_author = unpad(aes_cipher_decrypt.decrypt(decoded_author), AES.block_size)

                # Set decrypted values on the request object
                request.data_response = decrypted_data.decode()
                request.author_response = decrypted_author.decode()

            except ValueError as ve:
                request.error = f"Padding error: {str(ve)}"
            except Exception as e:
                request.error = f"Decryption failed: {str(e)}"
        else:
            request.error = "Missing data for decryption"


    def __call__(self, request):
        # Process the request
        self.process_request(request)
        # Pass the request to the next middleware or view
        response = self.get_response(request) if self.get_response else None
        return response
