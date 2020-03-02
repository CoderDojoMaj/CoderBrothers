import hashlib

salt = b'a$_\xff\x1b\xa3\xa8\xcde\xaa\x88Y\xbb\xdd\xa2>Q\xf5A\xa2' # TODO: make this generated by each server from os.urandom or sth like that

# Create a 32 bit digest (large number) based on the data. Checking for equality in digests is the same as if we checked if a passaword is equal to another one
def encrypt(data): # Used for encrypting a password into a number
    return hashlib.pbkdf2_hmac('sha256', data.encode('utf8'), salt, 150000)

def validate(data, digest): # Used for password checking (if the compute the same digest)
    return encrypt(data) == digest
