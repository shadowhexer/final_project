from utils.key_utils import KeyManager


def get_public_key(request):
    # Generate or retrieve the public key
    public_key = KeyManager.generate_keys('server')
    
    # Ensure the public key is returned as a string (if it’s a byte object)
    public_key_str = public_key.decode('utf-8') if isinstance(public_key, bytes) else str(public_key)
    
    return JsonResponse({'pub_key': public_key_str}, status=200)