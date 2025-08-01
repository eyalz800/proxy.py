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
    def __init__(self):
        self.total_time = 0

    def execute_query(self, query: str) -> str:
        print(f"[PERF_TRACE]: before execute {query}")
        start_time = time.perf_counter()
        # Note: proxy.get(Database, self) retrieves the original Database instance
        result = proxy.get(Database, self).execute_query(query)
        end_time = time.perf_counter()
        elapsed_time = (end_time - start_time) * 1000 # in milliseconds
        print(f"[PERF_TRACE]: after execute {query}, query took {elapsed_time:.2f}ms")
        self.total_time += elapsed_time
        return result

    def summary(self) -> str:
        return f"Total time: {self.total_time:.2f}ms"

    # Any other methods or fields (like 'connect/disconnect' in this example) that are not
    # explicitly defined in DatabasePerformanceTracer will be automatically
    # delegated to the 'Database' instance by the proxy mechanism

# --- How to use ---

if __name__ == "__main__":
    # This example shows how to use the proxy with a real object.
    # The proxy will automatically delegate calls to the original object
    # and provide additional functionality (like performance tracing in this case).

    print("--- Using Database with Performance Tracing Proxy ---")
    # 1. Create an instance of the object you want to proxy
    real_db_instance = Database()

    # 2. Create a proxied instance using `proxy.create`
    # The first argument is the proxy class, the second is the object to proxy.
    db = proxy.create(DatabasePerformanceTracer, real_db_instance)

    # Now, interact with the proxy instance
    print("\n--- Interacting with db ---")
    print(db.connect())
    print(db.execute_query("SELECT * FROM users;"))
    print(db.execute_query("SELECT * FROM products;"))
    db.disconnect() # This call is delegated and autocompleted by LSP automatically
    db.summary()  # Call the summary method to see total time

    print("\n--- Accessing the underlying proxied object ---")
    # You can get the original object back using `proxy.get`
    original_object = proxy.get(Database, db)
    print(f"Is original_object the same as real_db_instance? {original_object is real_db_instance}")
    original_object.execute_query("SELECT * FROM users;")
