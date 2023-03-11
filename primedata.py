from datetime import datetime
import sys
import sqlite3

def sieve_of_eratosthenes(start, end):
    # Create a boolean array "is_prime[0..n]" and initialize
    # all entries it as true. A value in is_prime[i] will
    # finally be false if i is Not a prime, else true.
    n = end + 1
    is_prime = [True] * n
    primes = []

    # Loop through all numbers up to the square root of n
    for p in range(2, int(n ** 0.5) + 1):
        # If p is prime, mark all its multiples as not prime
        if is_prime[p]:
            for i in range(p ** 2, n, p):
                is_prime[i] = False

    # Append all prime numbers in the given range to the primes list
    for p in range(max(start, 2), n):
        if is_prime[p]:
            primes.append(p)

    return primes


def sieve_of_sundaram(start, end):
    # If Invalid input
    if start < 2:
        start = 2
    if end < start:
        return []

    k = 2 * end + 1
    n = (k - 2) // 2
    sieve = [False] * (n + 1)

    for i in range(1, n + 1):
        j = i
        while i + j + 2 * i * j <= n:
            sieve[i + j + 2 * i * j] = True
            j += 1

    primes = [2] + [2 * i + 1 for i in range(1, n + 1) if not sieve[i]]
    primes_between_a_b = [p for p in primes if p >= start and p <= end]
    return primes_between_a_b

def sieve_of_atkin(start, end):
    # Initialize the sieve
    sieve = [False] * (end - start + 1)

    # Set up the prime sieve for the sieve of Atkin
    primes = [2, 3, 5]
    sqrt_end = int(end**0.5) + 1
    prime_sieve = [True] * (sqrt_end + 1)
    for i in range(2, sqrt_end):
        if prime_sieve[i]:
            for j in range(i**2, sqrt_end + 1, i):
                prime_sieve[j] = False
            primes.append(i)

    # Apply the sieve of Atkin to find all prime numbers in the range
    for x in range(1, int(sqrt_end)):
        for y in range(1, int(sqrt_end)):
            n = 4*x**2 + y**2
            if n <= end and n >= start and (n % 12 == 1 or n % 12 == 5):
                sieve[n - start] = not sieve[n - start]
            n = 3*x**2 + y**2
            if n <= end and n >= start and n % 12 == 7:
                sieve[n - start] = not sieve[n - start]
            n = 3*x**2 - y**2
            if x > y and n <= end and n >= start and n % 12 == 11:
                sieve[n - start] = not sieve[n - start]

    # Collect all prime numbers in the range
    primes += [i for i in range(start, end+1) if sieve[i - start]]

    # Handle special cases for start=1 and start=2
    if start <= 2:
        primes = [2] + primes
    if start <= 1 and end >= 2:
        primes = [2] + primes[1:]

    return primes
  
conn = sqlite3.connect('primes.db')
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS primes (timestamp TEXT, start INTEGER, end INTEGER, algorithm TEXT, num_primes INTEGER, time_elapsed REAL)')

def get_primes(start, end, algorithm):
    if start < 0 or end < 0 or end < start:
        print('invalid input')
        return
    if algorithm not in ['eratosthenes', 'sundaram', 'atkin']:
        print('invalid input')
        return

    t1 = datetime.utcnow()

    if algorithm == 'eratosthenes':
        primes = sieve_of_eratosthenes(start,end)
    elif algorithm == 'sundaram':
        primes=sieve_of_sundaram(start,end)
    else:
        primes = sieve_of_atkin(start,end)

    t2 = datetime.utcnow()
    time_elapsed = (t2 - t1).total_seconds()

    primes_in_range = [p for p in primes if p >= start and p <= end]
    num_primes = len(primes_in_range)

    # Insert the record into the database
    c.execute('INSERT INTO primes VALUES (?, ?, ?, ?, ?, ?)',
              (str(t1), start, end, algorithm, num_primes, time_elapsed))
    conn.commit()

    print(num_primes, primes_in_range)
print('1.command line')
print('2.program input')
ch=int(input('enter choice '))
if (ch==1):
  start = int(sys.argv[1])
  end = int(sys.argv[2])
  algo = str(sys.argv[3])
elif (ch==2):
  start = int(input('enter start point'))
  end = int(input('enter end point'))
  algo = input('enetr algorithm name ')
else:
  print('invalid input')

# Call the sieve_of_atkin function and print the result
get_primes(start, end , algo)
conn.close()