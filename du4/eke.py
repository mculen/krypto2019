#!/usr/bin/python

#
# V cykle skúšame všetky možné heslá. Pre každé vypočítame zodpovedajúci
# symetrický kľúč a týmto kľúčom dešifrujeme zachytené správy. Potom overíme,
# či získané hodnoty p, g, y, r, s zodpovedajú platným obsahom správ
# protokolu ElGamal-EKE, teda či:
#     1) p je 8L bitové číslo,
#     2) y, r, s ∈ (0, p),
#     3) g ∈ (1, p),
#     4) y != g (keďže y = g^x mod p a x > 1),
#     5) p a q = (p - 1) / 2 sú prvočísla,
#     6) g ^ q mod p > 1,
# pričom časovo náročnejšie podmeinky (využívajúce test prvočíselnosti,
# modulárne mocnenie) vykonávame ako posledné. Ak správa spĺňa všetky podmienky,
# zapamätáme si zodpovedajúce heslo. Na konci všetky možné heslá jednoducho
# vypíšeme.
#

from Crypto.Cipher import AES
import hashlib
import gmpy2
import ast

LENGTH = 64

inp = ast.literal_eval(open('hw4-data/protocol08.txt').read())

(st1_nonce, st1_ct) = inp['step1']
(st2_nonce, st2_ct) = inp['step2']

def pass2key(password):
    return hashlib.sha256(bytearray(password, 'utf8')).digest()[:16]

def decrypt(K, nonce, ct):
    aes = AES.new(K, AES.MODE_CTR, nonce=nonce)
    return aes.decrypt(ct)

def b2i(x):
    return int.from_bytes(x, 'big')

def i2b(x):
    return x.to_bytes(LENGTH, 'big')

def verify(p, g, y, r, s):
    if ((p >> (8 * LENGTH - 1)) != 1):
        return False
    if not (1 < g < p and 0 < y < p and y != g):
        return False
    if not (0 < r < p and 0 < s < p):
        return False
    if not gmpy2.is_prime(p):
        return False
    q = (p - 1) // 2
    if not gmpy2.is_prime(q):
        return False
    if not (pow(g, q, p) > 1):
        return False
    return True


candidates = [ ]

for i in range(0, 2 * 10**6):
    password = f'p{i:09}'
    K = pass2key(password)
    st1_pt = decrypt(K, st1_nonce, st1_ct)
    (p, g, y) = (b2i(st1_pt[0:LENGTH]), b2i(st1_pt[LENGTH:2*LENGTH]), b2i(st1_pt[2*LENGTH:3*LENGTH]))
    st2_pt = decrypt(K, st2_nonce, st2_ct)
    (r, s) = (b2i(st2_pt[0:LENGTH]), b2i(st2_pt[LENGTH:2*LENGTH]))
    if verify(p, g, y, r, s):
        candidates.append(password)
    if i > 0 and i & 0xfff == 0:
        print(f'{i / (2 * 10**6) * 100:06.2f}%:', candidates, end='\r')

print('100.00%:', candidates)
