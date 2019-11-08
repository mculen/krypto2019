#!/usr/bin/python

#
# Zoberme si prvé dve rovnice (prvé dva riadky matice A a prvky s a b):
#   <a0, s> + e0 = b0
#   <a1, s> + e1 = b1
# Vieme, že a1 = c * a0 + d^n (d^n myslíme vektor dĺžky n s prvkami d), dosadíme:
#   <c * a0 + d^n, s> + e1 = b1
# Platí:
#   <c * a0, s> + <s, d^n> + e1 = b1
#   c * <a0, s> + <s, d^n> + e1 = b1
# Vyjadríme z prvej rovnice <a0, s> a dosadíme:
#   c * (b0 - e0) + <s, d^n> + e1 = b1
#   <s, d^n> = (b1 - e1) - c * (b0 - e0)
# Toto zjavne platí pre každú dvojicu zodp. riadkov.
#
# Ako prvé nájdeme množinu možných hodnôt <s, d^n> = sdn - prejdeme
# všetkými dvojicami riadkov, a pre každú vyskúšame všetkých |{-3, ..., 3}|^2 =
# = 7^2 = 49 možností hodnôt e0 a e1 a z vyššieuvdeného vzťahu vypočítame
# zodp. hodnoty sdn. Finálna množina sdn je jednoducho prienik všetkých množín
# pre všetky riadky.
#
# Potom začneme postupne skúšať všetky hodnoty sdn. Pre každú dvojciu riadkov
# nájdeme dvojicu chýb (e0, e1), ktorá spolu s daným sdn spĺňa náš vzťah.
# Predchádzajúcim cyklom sme zaistili, že vždy taká musí existovať, a v praxi
# sa zdá, že existuje práve jedna. Keď máme chybový vektor e, môžeme
# teraz ľahko dopočítať také s, pre ktoré A * s = (b - e).
# Ak také nájdeme, vypíšeme ho a skončíme, ak nie, pokračujeme skúšaním
# ďalšieho sdn.
#

import copy
import itertools
import json

pk = json.loads(open("hw3-data/pk08.txt").read().replace("'", '"').replace('(', '[').replace(')', ']'))
(q, A, b, c, d) = (pk['q'], pk['A'], pk['b'], pk['c_mult'], pk['c_add'])
n, m = len(A[0]), len(A)

# pre q = 257 lenivý spôsob stačí...
inv_q = [[b for b in range(q) if (a * b) % q == 1][0] if a != 0 else 0 for a in range(q)]

# vráti s také, že A * s = b
# A musí byť štvorcová matica
def solve(A, b):
    A = copy.deepcopy(A)
    b = copy.deepcopy(b)
    n, m = len(A), len(A[0])
    assert n == m
    assert n == len(b)
    det = 1
    for i in range(n - 1):
        k = i
        for j in range(i + 1, n):
            if A[j][i] > A[k][i]:
                k = j
        if k != i:
            A[i], A[k] = A[k], A[i]
            b[i], b[k] = b[k], b[i]
            det = -det

        for j in range(i + 1, n):
            t = (A[j][i] * inv_q[A[i][i]]) % q
            for k in range(i + 1, n):
                A[j][k] = (A[j][k] - t * A[i][k]) % q
            b[j] = (b[j] - t * b[i]) % q

    for i in range(n - 1, -1, -1):
        for j in range(i + 1, n):
            t = A[i][j]
            b[i] = (b[i] - t * b[j]) % q
        t = inv_q[A[i][i]]
        det = (det * A[i][i]) % q
        b[i] = (b[i] * t) % q
    return b if det else [0] * n

def mul(A, b):
    n, m = len(A), len(A[0])
    p = len(b)
    assert p == m
    c = [0 for i in range(n)]
    for i in range(n):
        c[i] = sum(A[i][k] * b[k] for k in range(p)) % q
    return c

def err(a, b):
    diff = (a - b) % q
    if diff * 2 > q:
        return diff - q
    else:
        return diff


# začiatok

sdn_set = set(range(q))
for i in range(0, m, 2):
    sdn_set &= set([((b[i + 1] - e1) - c * (b[i] - e0)) % q for (e0, e1) in itertools.product(range(-3, 4), range(-3, 4))])

new_b = [ 0 for _ in range(m) ]
for sdn in sdn_set:
    for i in range(0, m, 2):
        errors = [ ]
        for (e0, e1) in itertools.product(range(-3, 4), range(-3, 4)):
            if sdn == ((b[i + 1] - e1) - c * (b[i] - e0)) % q:
                errors.append((e0, e1))
        assert len(errors) == 1 # TODO: platí vždy
        (e0, e1) = errors[0]
        new_b[i] = (b[i] - e0) % q
        new_b[i + 1] = (b[i + 1] - e1) % q
    # TODO: Ideálne by sme asi mali riešiť plnú sústavu A * s = (b - e), tu ale
    # riešime iba sústavu s štvorcovým výsekom z A, pozostávajúcim z prvých 40
    # párnych riadkov (a0, a2, ...), a potom overíme, či skutočne A * s = (b - e).
    # Je teoreticky možné (aj keď keďže koeficienty sú náhodné, asi
    # nepravdepodobné), že táto sústava nie je riešiteľná, aj keď pôvodná je,
    # a teda môžeme prehliadnuť správne riešenie. Na vyriešenie tejto úlohy to
    # ale stačí (a aj na všetky ostatné z pk**.txt), takže to nechávam takto.
    s = solve(A[:2*n:2], new_b[:2*n:2])
    As = mul(A, s)
    if As == new_b:
        assert sdn == (sum(s) * d) % q
        print("s: ", s)
        print("e: ", [err(b[i], As[i]) for i in range(n)])
        print()
        quit()

