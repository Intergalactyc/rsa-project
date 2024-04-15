from large-primes import nextprime
import secrets

# RSA key generation implementation

def gcd(a: int, b: int) -> int:
    # Euclidean algorithm to compute greatest common divisor
    # of two integers
    if b==0:
        return a
    return gcd(b, a%b)

def lcm(a: int, b: int) -> int:
    # Compute least common multiple of two integers
    return (a * b) // gcd(a,b)

def mmi(a: int, N: int) -> int:
    # Extended Euclidean algorithm to compute modular multiplicative
    # inverse of integer a, modulo N

def keypair(k: int=512, *, e: int=65537) -> dict:
    # Generate a pair of keys - public and private
    
    # First, create the two prime factors whose product constitute
    # the primary part of the public key. Large random integers
    # (k bits) are chosen, and the next prime number is found
    initializers = (secrets.randbits(k),secrets.randbits(k))
    p = nextprime(initializers[0],32)
    q = nextprime(initializers[1],32)
    n = p * q # first part of the public key

    totient = lcm(p-1,q-1) # Carmichael totient of n

    # The value e given is by default 2**16+1
        # This value must be smaller than the totient
        # and may not divide that totient

    d = mmi(e, totient) # private key as inverse of e mod the totient
    
    return {"public" : (n,e), "private" : d}
