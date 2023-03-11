from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask('__main__')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///primesweb.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Execution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    range_start = db.Column(db.Integer, nullable=False)
    range_end = db.Column(db.Integer, nullable=False)
    algorithm = db.Column(db.String(50), nullable=False)
    num_primes = db.Column(db.Integer, nullable=False)
    time_elapsed = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"Execution(timestamp='{self.timestamp}', range_start='{self.range_start}', range_end='{self.range_end}', algorithm='{self.algorithm}', num_primes='{self.num_primes}', time_elapsed='{self.time_elapsed}')"

def sieve_of_eratosthenes(start, end):
    n = end + 1
    #boolean array
    is_prime = [True] * n
    primes = []

    # Loop  up to the square root of n
    for p in range(2, int(n ** 0.5) + 1):
        # If p is prime, mark all its multiples as not prime
        if is_prime[p]:
            for i in range(p ** 2, n, p):
                 # entery made false if i is Not a prime, else true.
                is_prime[i] = False

    # Append  to the primes list
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

@app.route('/',methods = ["GET", "POST"])
def get_primes():
    if request.method == "POST":
        # getting input with name = fname in HTML form

        start = int(request.form.get("snumber"))
        # getting input with name = lname in HTML form
        end = int(request.form.get("enumber"))
        algorithm = request.form.get("aname")


        if start < 0 or end < 0 or end < start:
            return jsonify({'error': 'Invalid input'}), 400
        if algorithm not in ['eratosthenes', 'sundaram', 'atkin']:
            return jsonify({'error': 'Invalid algorithm'}), 400
        t1 = datetime.utcnow()
        if algorithm == 'eratosthenes':
            primes = sieve_of_eratosthenes(start,end)
        elif algorithm == 'sundaram':
            primes=sieve_of_sundaram(start,end)
        else:
            primes = sieve_of_atkin(start,end)
        primes_in_range = [p for p in primes if p >= start and p <= end]
        t2 = datetime.utcnow()
        execution_time = "{:.20f}".format((t2 - t1).total_seconds())
        print(t1,t2)
        print(execution_time)
        num_primes = len(primes_in_range)
        with app.app_context():
          execution = Execution(range_start=start, range_end=end, algorithm=algorithm, num_primes=num_primes, time_elapsed=execution_time)
          db.session.add(execution)
          db.session.commit()
        return jsonify({'primes': primes_in_range})

if __name__ == '__main__':
  with app.app_context():
    db.create_all()
    app.run(host= '127.0.0.1', port = '5000' ,debug=True)
    executions = Execution.query.all()
    for e in executions:
        print(e)