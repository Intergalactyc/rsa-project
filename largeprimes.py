import secrets

def powmod(b: int, a: int, N: int) -> int:
    # Computes (b**a)%N

    # Update result iteratively using "Algorithm 1"
    r = 1
    beta = b
    alpha = a
    while alpha > 0:
        if alpha % 2 == 1:
            r = (r * beta) % N
        alpha = int(alpha//2)
        beta = (beta * beta) % N
        
    return r

def mr_single_test(N: int, q: int, t: int) -> bool:
    # Partial primality test: Tests whether N is composite.
        # Assertions of True are always accurate
        # Assertions of False may be mistaken
    # N, q, t positive integers; q odd
        # Must satisfy N - 1 == (2**t) * q

    # Choose random integer b from 2 to N-1 inclusive
    b = secrets.randbelow(N-2)+2

    # Create "roots" list
    current = powmod(b, q, N)
    roots = [current]
    for _ in range(1,t+1):
        current = (current*current)%N
        roots.append(current)

    if 1 not in roots: return False # N has been proven composite
    # Find the least nonnegative integer e such that b**((2**e)*q)%N==1
    # Do so by iterating through the roots list
    e = 0
    index = 0
    searching = True
    while searching and index < t+1:
        if roots[index] == 1:
            e = index
            searching = False
        index += 1
    if e == 0 or (e > 0 and roots[e-1] == N - 1): return True
    return False # N must be composite
    

def mr_test(N: int, k: int) -> bool:
    # Prime test: checks that N is prime
        # Error probability of (1/4)**k
    # N, k positive integers

    # Easy & edge cases
    if N == 2: return True
    if N == 1 or N % 2 == 0: return False

    # Find positive integers t, q such that N - 1 == (2**t) * q
    t = 0
    q = N - 1
    while q % 2 == 0:
        q = q // 2
        t += 1
        
    # Test N to see if it is composite
    for _ in range(k):
        if not mr_single_test(N,q,t): return False
    return True

def sg_test(N: int, k: int) -> bool:
    # Sofie-Germain prime test
        # See nextsafeprime below
    if not mr_test(N, k):
        return False
    return mr_test(2*N+1, k)

def nextprime(n: int, K: int=20) -> int:
    # Finds and returns the smallest prime p >= n
    # With given value of k = 20, confidence is 1-(1/4)**20: very close to 1
        # Chance of error is bounded above by 9.1e-13: about 1 in 1 trillion
    p = n
    while not mr_test(p, K):
        p += 1
    return p

def safeprime(n: int, K: int=20) -> int:
    # Finds and returns the safe prime 2p+1 corresponding to the
    # smallest Sofie Germain prime p >= n
        # A prime p is a Sofie Germain prime if 2p+1 is also prime
        # The corresponding prime 2p+1 is in this case a "safe prime"
    p = n
    while not sg_test(p, K):
        p += 1
    return 2*p+1
