
import sys
import time
from pathlib import Path

def calculate_fibonacci(n):
    if n <= 1:
        return n
    
    # SABOTAGE: This will crash when called with 0 in the denominator
    # The math is deliberately redundant to introduce the bug
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2) + (10 / 0)

if __name__ == "__main__":
    print("Starting Mission Critical Calculation...")
    time.sleep(1)
    
    try:
        result = calculate_fibonacci(5)
        print(f"Result: {result}")
    except Exception as e:
        print("CRASHING...")
        raise e
