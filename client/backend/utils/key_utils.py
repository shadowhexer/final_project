import os
from Crypto.PublicKey import RSA


class KeyManager:
    _key_dir = "./keys/"  # Directory to store the private keys

    @classmethod
    def initialize(cls):
        """Ensure the key directory exists."""
        if not os.path.exists(cls._key_dir):
            os.makedirs(cls._key_dir)

    @classmethod
    def generate_keys(cls, username):
        """
        Generate RSA keys for a specific user and save the private key in a file.
        The public key is returned for other uses.
        
        :param username: Unique identifier (e.g., username) for the private key file.
        :return: public_key (bytes)
        """
        cls.initialize()  # Ensure the directory exists

        # Generate RSA key pair
        rsa_key = RSA.generate(2048)
        private_key = rsa_key.export_key()
        public_key = rsa_key.publickey().export_key()

        # Save the private key with the username as the filename
        private_key_path = os.path.join(cls._key_dir, f"{username}_private.pem")
        with open(private_key_path, "wb") as key_file:
            key_file.write(private_key)

        print(f"Private key saved to {private_key_path}")
        return public_key

    @classmethod
    def get_private_key(cls, username):
        """
        Retrieve the private key for a given user from the keys directory.
        
        :param username: Unique identifier for the private key file.
        :return: private_key (bytes) or None if not found.
        """
        private_key_path = os.path.join(cls._key_dir, f"{username}_private.pem")
        if os.path.exists(private_key_path):
            with open(private_key_path, "rb") as key_file:
                return key_file.read()
        else:
            print(f"Private key for {username} not found.")
            return None