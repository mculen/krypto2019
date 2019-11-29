import random
import utils
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import hashlib
import gmpy2

LENGTH = 64

def generate_key(prime_length):

    # generate safe prime number
    while True:
        q = utils.generate_prime(prime_length-1)
        p = 2*q + 1
        if gmpy2.is_prime(p):
            break
        
    # generate a generator
    while True:
        g = random.randint(2, p-1)
        if pow(g, q, p) > 1:
            break

    # generate private and publc key
    x = random.randint(2, p-1)
    y = pow(g, x, p)
    
    public_key = (p, g, y)
    secret_key = (p, g, x)

    return public_key, secret_key

def encrypt_integer(public_key, m):
    (p, g, y) = public_key
    if m >= p:
        raise Exception("Message is to big!")
    k = random.randint(1, p-1)
    return (pow(g, k, p), (m * pow(y, k, p)) % p)

def decrypt_integer(secret_key, c):
    (p, g, x) = secret_key
    (r, s) = c
    return (s * pow(r, p-1-x, p)) % p

def pass2key(password):
    return hashlib.sha256(bytearray(password, 'utf8')).digest()[:16]

def int2bytes(x):
    return x.to_bytes(LENGTH, 'big')
    
###############################################################################
def genHW(idx):
    passwd = f'p{random.randint(0,2*10**6-1):09}'
    with open(f'password{idx:02}.txt', 'wt') as f:
        f.write(passwd)
    print(passwd)
    pk, sk = generate_key(LENGTH * 8)
    K  = pass2key(passwd)
    aes = AES.new(K, AES.MODE_CTR)
    p, g, y = pk
    plaintext = b''.join([int2bytes(p), int2bytes(g), int2bytes(y)])
    ciphertext = aes.encrypt(plaintext)
    nonce = aes.nonce
    aes = AES.new(K, AES.MODE_CTR)
    sessionK = get_random_bytes(16)
    r, s = encrypt_integer(pk, int.from_bytes(sessionK, 'big'))
    session_pt = b''.join([int2bytes(r), int2bytes(s)])
    session_ct = aes.encrypt(session_pt)
    session_nonce = aes.nonce
    communication = {'step1' : (nonce, ciphertext), 'step2': (session_nonce, session_ct)}
    with open(f'protocol{idx:02}.txt', 'wt') as f:
        f.write(str(communication))
   
###############################################################################

for idx in range(1,16):
    print(f'HW {idx:02} ======================================')
    genHW(idx)
