import random
import gmpy2

def generate_prime(bit_length):
        while True:
            lb = 2 ** (bit_length - 1)
            ub = (2 ** bit_length) - 1
            candidate = random.randint(lb, ub)
            if gmpy2.is_prime(candidate):
                return candidate
