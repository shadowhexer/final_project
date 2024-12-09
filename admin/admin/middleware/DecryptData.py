import base64
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Util.Padding import unpad

class Decrypt:
    def __init__(self, get_response):
        self.get_response = get_response

    def process_request(self, request):
        # Check for required attributes on the request
        if hasattr(request, 'encrypted_session_key') and hasattr(request, 'private_key') and hasattr(request, 'iv'):
            try:
                # Extract required data from request
                private_key = request.private_key  # Assuming this contains the private RSA key (PEM format)
                encrypted_data = request.data.get('encrypted_data')  # Base64 encoded ciphertext
                encrypted_author = request.data.get('encrypted_author')  # Base64 encoded ciphertext
                encrypted_session_key = request.encrypted_session_key  # Base64 encoded RSA-encrypted session key
                iv = request.iv  # Base64 encoded initialization vector

                # Decode Base64 encoded values
                encrypted_data = base64.b64decode(encrypted_data)
                encrypted_author = base64.b64decode(encrypted_author)
                encrypted_session_key = base64.b64decode(encrypted_session_key)
                iv = base64.b64decode(iv)

                # Step 1: Decrypt the session key using RSA private key
                rsa_cipher_decrypt = PKCS1_OAEP.new(RSA.import_key(private_key))
                decrypted_session_key = rsa_cipher_decrypt.decrypt(encrypted_session_key)

                # Step 2: Decrypt the data and author using the AES session key
                aes_cipher_decrypt = AES.new(decrypted_session_key, AES.MODE_CBC, iv)
                decrypted_data = unpad(aes_cipher_decrypt.decrypt(encrypted_data), AES.block_size)
                decrypted_author = unpad(aes_cipher_decrypt.decrypt(encrypted_author), AES.block_size)

                # Set decrypted values on the request object for later use
                request.data_response = decrypted_data.decode('utf-8')
                request.author_response = decrypted_author.decode('utf-8')

            except Exception as e:
                # Handle errors gracefully and log them
                request.decryption_error = f"Decryption failed: {str(e)}"


    def __call__(self, request):
        # Process the request
        self.process_request(request)
        # Pass the request to the next middleware or view
        response = self.get_response(request) if self.get_response else None
        return response
