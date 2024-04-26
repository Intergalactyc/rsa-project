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
    

def mr_test(N: int, k: int=20) -> bool:
    # Primality test: checks that N is prime
        # Error probability less than (1/4)**k
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

def sg_test(N: int, k: int=20) -> bool:
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

def prime_range(start: int, stop: int=None, step: int=1, sg: bool=False, k: int=20, progress: bool=False):
    # Not used in the RSA algorithm, I just wanted to make this
    # Generates a list of primes between a start and stop value
    # Arguments emulate behavior of range:
        # call as ``prime_range(stop)'' to default start=0 (actually 1, see below)
        # otherwise can call as ``prime_range(start, stop)''
    # Option to have it generate Sofie Germain (sg) primes only
    if stop is None:
        # No reason to start at 0 because 0 will not be included anyways
        start, stop = 1, start
    if sg:
        primefunc = sg_test
    else:
        primefunc = mr_test
    result = []
    # The range we will iterate over has step size 2 because we can ignore even numbers
        # Because of this we need to force the start to be odd
    if start % 2 == 0:
        start += 1
    myrange = range(start,stop,2)
    if progress:
        from tqdm import tqdm
        myrange = tqdm(myrange)        
    for i in myrange:
        if primefunc(i,k):
            result.append(i)
    return result

def mersenne_list(iterations: int, k: int=30, progress: bool=False, simple: bool=True):
    # Also not used in the RSA algorithm
    # Generates a list of Mersenne primes,
    # i.e., primes which are of the form 2**N-1 for positive integer N
    # If "simple" (default), then the output list will be of strings '2^n-1'
    # rather than full base-10 integers
    # If n is composite then so is 2^n-1, so only bother checking 2^p-1 for prime p
    myrange = prime_range(iterations)
    if progress:
        from tqdm import tqdm
        myrange = tqdm(myrange)
    mersennes = []
    for i in myrange:
        p = 2**i-1
        if mr_test(p,k):
            if simple:
                mersennes.append(f"2^{i}-1")
            else:
                mersennes.append(p)
    return mersennes

def mersenne_search(initial: int, k: int=30, simple: bool=True):
    # Again, not used in the RSA algorithm
    # Finds the largest Mersenne prime up to 2**initial-1 (see mersenne_list)
    searchrange = prime_range(initial)
    for i in range(len(searchrange)):
        n = searchrange[-i-1]
        p = 2**n-1
        if mr_test(p,k):
            if simple:
                return f"2^{n}-1"
            return p
    
if __name__ == "__main__":
    # Main loop: CLI just for playing with the prime range and mersenne search functions
    mode = int(input("Available modes: [0] Prime range [1] Mersenne list [2] Mersenne search. What mode to operate in? "))
    if mode == 0:
        N = int(input("Upper limit for prime range? Enter a positive integer: "))
        res = prime_range(N, k=20, progress=True)
        print(f"There are {len(res)} primes between 1 and {N}.")
        full = input("View full list? [y/n]: ")
        if full.lower() == "y":
            print(res)
    elif mode == 1:
        print("Warning: this will be quite slow for entries over ~1000.")
        N = int(input("How many iterations for mersenne list generation? Enter a positive integer: "))
        res = mersenne_list(N, progress=True)
        print(f"{len(res)} mersenne primes found up to 2**{N}-1.")
        full = input("View full list? [y/n]: ")
        if full.lower() == "y":
            print(res)
    elif mode == 2:
        print("Warning: this will be quite slow for entries over ~3000.")
        N = int(input("Where should mersenne search begin? Enter a positive integer: "))
        res = mersenne_search(N)
        print(f"Largest mersenne prime found (up to 2**{N}-1): {res}")
    else:
        print(f"Mode '{mode}' not found.")
        
