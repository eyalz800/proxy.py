# Proxy Type With LSP Autocompletions

This small Python module provides a flexible and generic way to create proxy objects. It allows you to wrap an existing object and delegate method calls and attribute access to the wrapped (proxied) object, while still allowing the proxy class to define its own behavior or extend the proxied object's functionality.

## Features

*   **Generic Proxy Creation:** Easily create proxy classes for any Python object.
*   **Automatic Delegation:** Automatically delegates attribute access and method calls to the underlying proxied object.
*   **Customizable Proxy Behavior:** Define additional methods or override existing ones in your proxy class.
*   **Type Hinting Support:** Includes type hints for better code clarity and maintainability.

## Installation

This module is provided as a single file (`proxy.py`). To use it, simply copy `proxy.py` into your project directory.

## Usage

Here's how to use the `proxy` module to create and interact with proxy objects:

```python
from proxy import proxy
import time

# The actual implementation of the database connection
class Database:
    def connect(self) -> str:
        print("Database: Connecting to database...")
        return "Connected"

    def disconnect(self):
        print("Database: Disconnecting from database...")

    def execute_query(self, query: str) -> str:
        print(f"Database: Executing query: {query}")
        time.sleep(1)
        return f"Result for '{query}'"

# Define a proxy class that alters the behavior of Database
@proxy(Database)
class DatabasePerformanceTracer(Database): # Inheritance is just to get completions, and removed by the proxy.
    def execute_query(self, query: str) -> str:
        print(f"[PERF_TRACE]: before execute {query}")
        start_time = time.perf_counter()
        # Note: proxy.get(Database, self) retrieves the original Database instance
        result = proxy.get(Database, self).execute_query(query)
        end_time = time.perf_counter()
        elapsed_time = (end_time - start_time) * 1000 # in milliseconds
        print(f"[PERF_TRACE]: after execute {query}, query took {elapsed_time:.2f}ms")
        return result

    # Any other methods or fields (like 'connect/disconnect' in this example) that are not
    # explicitly defined in DatabasePerformanceTracer will be automatically
    # delegated to the 'Database' instance by the proxy mechanism

# --- How to use ---

# 1. Create an instance of the object you want to proxy
real_db_instance = Database()

# 2. Create a proxied instance using `proxy.create`
# The first argument is the proxy class, the second is the object to proxy.
db = proxy.create(DatabasePerformanceTracer, real_db_instance)

# Now, interact with the proxy instance
print("\n--- Interacting with db ---")
print(db.connect())
print(db.execute_query("SELECT * FROM users;"))
db.disconnect() # This call is delegated and autocompleted by LSP automatically

print("\n--- Accessing the underlying proxied object ---")
# You can get the original object back using `proxy.get`
original_object = proxy.get(Database, db)
print(f"Is original_object the same as real_db_instance? {original_object is real_db_instance}")
original_object.connect()
```

## How It Works

The core of this proxy mechanism relies on Python's magic methods:

*   **`@proxy` decorator (`Proxy.__call__`):** Transforms your class into a proxy. It wraps your class's `__init__` method to store the proxied object and injects a `__getattr__` method. The `__getattr__` method is responsible for delegating any attribute or method access that is not explicitly defined in your proxy class to the underlying proxied object.
*   **`proxy.create` (`Proxy.create`):** A factory method that instantiates your proxy class, passing the object to be proxied.
*   **`proxy.get` (`Proxy.get`):** Provides a way to retrieve the original object that the proxy is wrapping.

## Type Hinting

The module utilizes Python's `typing` module, to provide robust type hints. This improves code readability, enables LSP completion for the IDE.

## License

This project is licensed under the MIT License.
