#!/usr/bin/python

n, e, d, c = [ int(line[4:]) for line in open("hw2-data/rsa08.txt").readlines() ]
k = n.bit_length() // 8 + (n.bit_length() % 8 > 0)
B = pow(2, 8 * (k - 2))

def b2i(bytes):
    return int.from_bytes(bytes, byteorder='big')

def i2b(integer):
    return integer.to_bytes(k, byteorder='big')

def dec(c):
    p = pow(c, d, n)
    return p

def is_valid_pkcs(m):
    if m[0] != 0 or m[1] != 7:
        return False
    for i in range(2, 10):
        if m[i] == 0:
            return False
    for i in range(10, len(m)):
        if m[i] == 0:
            return True
    return False

def pkcs_decode(m):
    if not is_valid_pkcs(m):
        return None
    return m[m.index(0x00, 10) + 1:]

queries = 0

def oracle(c):
    global queries
    queries += 1
    p = i2b(dec(c))
#    return p[0] == 0 and p[1] == 7
    return is_valid_pkcs(p)

ceil__div = lambda a, b : -(-a // b)
floor_div = lambda a, b : a // b

# Step 2a
def find_smallest_s(lower_bound):
    s = lower_bound
    while True:
        attempt = (c * pow(s, e, n)) % n
        if oracle(attempt):
            return s
        s += 1

# Step 2c
def find_s_in_range(a, b, prev_s):
    ri = ceil__div(2 * (b * prev_s - 7 * B), n)
    while True:
        si_lower = ceil__div(7 * B + ri * n, b)
        si_upper = ceil__div(8 * B + ri * n, a)
        for si in range(si_lower, si_upper):
            attempt = (c * pow(si, e, n)) % n
            if oracle(attempt):
                return si
        ri += 1

def insert_interval(M_new, interval):
    (i_a, i_b) = interval
    for i, (a, b) in enumerate(M_new):
        if (b >= i_a) and (a <= i_b):
            lb = min(a, i_a)
            ub = max(b, i_b)
            M_new[i] = (lb, ub)
            return
    M_new.append(interval)


# Step 3
def update_intervals(M, s):
    M_new = []
    for a, b in M:
        r_lower = ceil__div(a * s - 8 * B + 1,  n)
        r_upper = ceil__div(b * s - 7 * B,  n)
        for r in range(r_lower, r_upper):
            lower_bound = max(a, ceil__div(7 * B     + r * n,  s))
            upper_bound = min(b, floor_div(8 * B - 1 + r * n, s))
            interval = (lower_bound, upper_bound)
            insert_interval(M_new, interval)
    M.clear()
    return M_new


def bleichenbacher(c):
    M = [(7 * B, 8 * B - 1)]
    i = 1
    while True:
        if i == 1:
            # Step 2a
            s = find_smallest_s(ceil__div(n, 8 * B))
        else:
            if len(M) > 1:
                # Step 2b
                s = find_smallest_s(s + 1)
            elif len(M) == 1:
                # Step 2c
                a, b = M[0]
                if a == b:
                    # Final step
                    return a % n
                s = find_s_in_range(a, b, s)
        print(s)
        M = update_intervals(M, s)
        i += 1

m = i2b(bleichenbacher(c))
print()
print("message:", m.hex())
print("plaintext:", pkcs_decode(m))
print("oracle queries:", queries)
