"""Example script 01 - Demonstrate usage of package features."""

# First party modules
from piptools_sync import piptools_sync

num, result = piptools_sync.get_config()
exp_result = [True for i in range(num)]
print(f"Result from function 'get_config': {result}")


result = piptools_sync.fizzbuzz(16)
print(f"Result from function 'fizzbuzz(16)': {result}")


result = piptools_sync.fibonacci(10)
print(f"Result from function 'fibonacci(10)': {result}")
