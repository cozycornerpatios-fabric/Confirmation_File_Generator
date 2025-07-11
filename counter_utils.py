import os

COUNTER_FILE = "counter.txt"

def read_counter():
    if not os.path.exists(COUNTER_FILE):
        return 0
    with open(COUNTER_FILE, 'r') as f:
        try:
            return int(f.read())
        except ValueError:
            return 0

def increment_counter():
    count = read_counter() + 1
    with open(COUNTER_FILE, 'w') as f:
        f.write(str(count))
    return count
