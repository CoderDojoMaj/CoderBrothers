import hashlib, python.setup as setup
import rsa

# Create a 32 bit digest (large number) based on the data. Checking for equality in digests is the same as if we checked if a passaword is equal to another one
def encrypt(data): # Used for encrypting a password into a number
    salt = setup.get_config()['salt']
    return hashlib.pbkdf2_hmac('sha256', data.encode('utf8'), salt, 150000)

def validate(data, digest): # Used for password checking (if the compute the same digest)
    return encrypt(data) == digest

def bytes_from_RSA_sendable_bytes(string):
    return bytes.fromhex(string.decode('utf8'))

def decrypt_RSA_from_bytes(bytes):
    return rsa.decrypt(bytes, setup.get_priv_key())

def decrypt_RSA_from_sendable_bytes(bytes):
    return decrypt_RSA_from_bytes(bytes_from_RSA_sendable_bytes(bytes))