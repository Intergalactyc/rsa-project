from largeprimes import powmod, nextprime, safeprime
import secrets
from math import log2

# RSA key generation implementation

def gcd(a: int, b: int) -> int:
    # Euclidean algorithm to compute greatest common divisor
    # of two integers
    if b == 0:
        return a
    return gcd(b, a%b)

def lcm(a: int, b: int) -> int:
    # Compute least common multiple of two integers
    return (a * b) // gcd(a,b)

def egcd(a: int, b: int) -> tuple[int, int, int]:
    # Extended Euclidean algorithm, computes gcd alongside
    # integer coefficients x, y such that ax+by==gcd(a,b)
    # Output of form (gcd, x, y)
    def recurse(r, s, t, r1, s1, t1):
        if r1 == 0:
            return (r, s, t)
        q = r // r1
        return recurse(r1, s1, t1, r-q*r1, s-q*s1, t-q*t1)
    return recurse(a, 1, 0, b, 0, 1)
    
def e_mmi(e: int, N: int) -> tuple[int, int]:
    # Compute modular multiplicative inverse of e, modulo N
    # using the extended Euclidean algorithm
    # If it turns out gcd != 1, e will be changed to the next prime
    # and the process repeats until a satisfactory tuple (e, e^-1 mod N)
    # is found and returned
    g, candidate, _ = egcd(e, N)
    if g == 1:
        if candidate < 0:
            candidate = N + candidate
        return (e, candidate)
    return e_mmi(nextprime(e,32), N)
    

def keypair(b: int=1024, *, e: int=65537, safe=False) -> dict:
    # Generate a pair of keys - public and private
    # The public key should be (roughly) b bits

    k = b // 2
    
    # First, create the two prime factors whose product constitute
    # the primary part of the public key. Large random integers
    # (k bits) are chosen, and the next prime number is found

    # If safe: These prime factors should be "safe primes" so that p-1, q-1
    # have large prime factors (to avoid use of Pollard's p-1 algorithm)
        # Downside is that this takes MUCH longer because of sparsity
        # of large safe primes
    if safe: genprime = safeprime
    else: genprime = nextprime
    
    def gen_pqn():
        initializers = (secrets.randbits(k-safe),secrets.randbits(k-safe))
        # If safe mode is on:
            # Because of the safeprime algorithm implementation,
            # the smallest possible return value is 2*initial+1,
            # so we'll reduce our starting value by a bit to compensate
            # The chance that the result is k+1 bits is very small for fairly
            # large k [~= 1/((density of safe primes around 2^k)* 2^(k-2))]
            # Even if it is k+1 bits it doesn't really matter for the
            # purposes of this implementation though
        p = genprime(initializers[0],32)
        q = genprime(initializers[1],32)
        n = p * q # first part of the public key
        if abs(p-q) < 2*n**(1/4):
            # p and q should not be too close, otherwise it is easy
            # to factor n via Fermat factorization
            return gen_pqn()
        return (p,q,n)

    p,q,n = gen_pqn()

    totient = lcm(p-1,q-1) # Carmichael totient of n

    # The value e given is by default 2**16+1 = 65537
        # This value must be smaller than the totient
        # and relatively prime to it. If prime (as default)
        # it may hence not divide the totient
    e, d = e_mmi(e, totient) # private key as inverse of e mod the totient
    # e may change (see e_mmi), its final value is the second part of
    # the public key
    
    return {"public" : (n,e), "private" : d}

def encrypt(plaintext: str, public: tuple[int,int]) -> int:
    # RSA encryption
    # Given public key (n,e):
        # Take unpadded plaintext string, pad into integer 0 <= m < n
        # Encrypt m into ciphertext c = (m**e)%n
    n, e = public
    M = str(plaintext) # just in case an integer is passed in
    max_bytes = int(log2(n))//8 # max bytes that we can safely have m be
    if len(plaintext) >= max_bytes - 1:
        print("Plaintext is too large.")
        return None
    m_hex = ''.join(format(ord(char), 'x') for char in plaintext)    
    m_hex += "00" # pad with a 0 byte
    # Follow the 0 with random junk padding
    for i in range(max_bytes - len(plaintext) - 2):
        junk = secrets.randbits(8)
        m_hex += format(junk, 'x')
    m = int(m_hex, 16)
    c = powmod(m, e, n) # encrypt
    return c

def decrypt(ciphertext: int, key: dict) -> str:
    # RSA decryption
    # Given private key d:
        # Take ciphertext integer, decrypt it
        # Unpad the result by stripping everything after the 0 byte
    n = key["public"][0]
    m = powmod(ciphertext, key["private"], n) # decrypt (m = (c**d)%n)
    # Convert to hex, chunk into bytes, remove 00 byte and everything after
    m_hex = hex(m)[2:]
    byte_pad = [m_hex[2*i:2*i+2] for i in range(len(m_hex)//2)]
    if "00" in byte_pad:
        # If string is a good decryption of a properly padded message
        byte_unpad = byte_pad[:byte_pad.index("00")]
    else:
        # Still have to return something upon a failure
        byte_unpad = byte_pad
    # Turn back into a string and return the result
    result = ''.join([chr(int(byte,16)) for byte in byte_unpad])
    return result

# add a way to sign messages? needs a hash function
    
def hexkey(keys):
    # Convenience function for converting key to hexadecimal
    pub = keys["public"]
    pri = keys["private"]
    return {"public" : (hex(pub[0]), hex(pub[1])),
            "private" : hex(pri)}

if __name__ == "__main__":
    import time
    # Brief demonstration
    print("Generating key pair...\n")
    key = keypair()
    print(f"Public key: {key['public']}")
    print(f"Private key: {key['private']}\n")
    time.sleep(1)
    message = input("Input a brief message to encrypt: ")
    encrypted = encrypt(message, key["public"])
    if encrypted is None:
        import sys
        sys.exit()
    print("Message encrypted using public key.")
    print(f"Encrypted message: {encrypted}\n")
    time.sleep(1)
    private = input("Provide a private key to decrypt the message (press <RETURN> to automatically use that given): ")
    if private != "":
        unlock = {"public": key["public"], "private": int(private)}
    else:
        unlock = key
    print("Decrypting message using public key and provided private key...")
    decrypted = decrypt(encrypted, unlock)
    print("Message decrypted.")
    print(f"Decrypted message: {decrypted}\n")
    
